import os
import csv
from datetime import datetime, timezone

from pymongo import MongoClient
from dotenv import load_dotenv


# ============================================================
# TRINETRA - SATELLITE EVIDENCE INTEGRATION
# Analysis Window:
# 19 Aug 2026 -> 19 Sep 2026
# ============================================================

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB", "trinetra")

CSV_PATH = "data/satellite/gee_event_metrics.csv"

EVENT_ID = "trinetra_2026_08_19_2026_09_19"


# ============================================================
# HELPERS
# ============================================================

def to_float(value):
    if value is None:
        return None

    if value == "":
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def to_int(value):
    if value is None:
        return 0

    if value == "":
        return 0

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


# ============================================================
# READ CSV
# ============================================================

def read_metrics():

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Metrics CSV not found: {CSV_PATH}"
        )

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise RuntimeError(
            "gee_event_metrics.csv is empty"
        )

    return rows[0]


# ============================================================
# EXISTING SATELLITE EVIDENCE LOGIC
# ============================================================

def calculate_satellite_evidence(row):

    s2_new_water = to_float(
        row.get(
            "sentinel2_candidate_new_water_ha"
        )
    )

    s2_net_change = to_float(
        row.get(
            "sentinel2_net_water_change_ha"
        )
    )

    s1_vv_change = to_float(
        row.get(
            "sentinel1_mean_vv_change_db"
        )
    )

    s1_new_water = to_float(
        row.get(
            "sentinel1_candidate_new_water_ha"
        )
    )

    s1_before = to_int(
        row.get(
            "sentinel1_before_scene_count"
        )
    )

    s1_after = to_int(
        row.get(
            "sentinel1_after_scene_count"
        )
    )

    s2_before = to_int(
        row.get(
            "sentinel2_before_scene_count"
        )
    )

    s2_after = to_int(
        row.get(
            "sentinel2_after_scene_count"
        )
    )

    # --------------------------------------------------------
    # Evidence components
    # --------------------------------------------------------

    evidence_points = 0

    evidence_reasons = []

    # S2 temporal coverage
    if s2_before > 0 and s2_after > 0:

        evidence_points += 1

        evidence_reasons.append(
            "Sentinel-2 before/after temporal coverage available"
        )

    # S1 temporal coverage
    if s1_before > 0 and s1_after > 0:

        evidence_points += 1

        evidence_reasons.append(
            "Sentinel-1 before/after temporal coverage available"
        )

    # --------------------------------------------------------
    # Sentinel-2 actual water change
    # --------------------------------------------------------

    if s2_net_change is not None:

        if s2_net_change > 0:

            evidence_points += 3

            evidence_reasons.append(
                f"Sentinel-2 detected positive net water change "
                f"of {s2_net_change:.2f} ha"
            )

        elif s2_net_change < 0:

            evidence_reasons.append(
                f"Sentinel-2 detected negative net water change "
                f"of {abs(s2_net_change):.2f} ha"
            )

        else:

            evidence_reasons.append(
                "Sentinel-2 detected no net water-area change"
            )

    # --------------------------------------------------------
    # Candidate new water
    # --------------------------------------------------------

    if (
        s2_new_water is not None
        and s2_new_water > 0
    ):

        evidence_points += 2

        evidence_reasons.append(
            f"Sentinel-2 candidate new-water area: "
            f"{s2_new_water:.2f} ha"
        )

    # --------------------------------------------------------
    # Sentinel-1 quantitative evidence
    # --------------------------------------------------------

    if s1_vv_change is not None:

        evidence_points += 2

        evidence_reasons.append(
            f"Sentinel-1 VV change available: "
            f"{s1_vv_change:.4f} dB"
        )

    else:

        evidence_reasons.append(
            "Sentinel-1 quantitative VV change not available"
        )

    if (
        s1_new_water is not None
        and s1_new_water > 0
    ):

        evidence_points += 2

        evidence_reasons.append(
            f"Sentinel-1 candidate new-water area: "
            f"{s1_new_water:.2f} ha"
        )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    if (
        s2_new_water is not None
        and s2_new_water > 0
    ):

        if (
            s1_vv_change is None
            and s1_new_water is None
        ):

            status = (
                "S2_POSITIVE_WATER_CHANGE_S1_QUANTITATIVE_UNAVAILABLE"
            )

        else:

            status = "SATELLITE_WATER_CHANGE_DETECTED"

    else:

        status = "INCONCLUSIVE_SATELLITE_EVIDENCE"

    return {
        "satellite_evidence_points":
            evidence_points,

        "satellite_evidence_status":
            status,

        "sentinel1_before_scene_count":
            s1_before,

        "sentinel1_after_scene_count":
            s1_after,

        "sentinel2_before_scene_count":
            s2_before,

        "sentinel2_after_scene_count":
            s2_after,

        "sentinel1_mean_vv_change_db":
            s1_vv_change,

        "sentinel1_candidate_new_water_ha":
            s1_new_water,

        "sentinel2_candidate_new_water_ha":
            s2_new_water,

        "sentinel2_net_water_change_ha":
            s2_net_change,

        "evidence_reasons":
            evidence_reasons,
    }


# ============================================================
# SAVE TO MONGODB
# ============================================================

def save_to_mongodb(result, source_row):

    client = MongoClient(MONGO_URI)

    db = client[MONGO_DB]

    collection = db["satellite_metrics"]

    document = {
        "event_id": EVENT_ID,

        "analysis_window": {
            "start":
                "2026-08-19T00:00:00Z",

            "end":
                "2026-09-19T23:59:59Z"
        },

        "satellite_evidence": result,

        "source_metrics": source_row,

        "updated_at":
            datetime.now(timezone.utc),
    }

    collection.update_one(
        {
            "event_id": EVENT_ID
        },
        {
            "$set": document
        },
        upsert=True
    )

    return document


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "🚀 TRINETRA SATELLITE EVIDENCE INTEGRATION"
    )

    print(
        "19 Aug 2026 → 19 Sep 2026"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Read metrics
    # --------------------------------------------------------

    row = read_metrics()

    print("\n📄 Reading:")
    print(CSV_PATH)

    # --------------------------------------------------------
    # Calculate evidence
    # --------------------------------------------------------

    result = calculate_satellite_evidence(row)

    print("\n" + "=" * 70)
    print("🛰️ SATELLITE EVIDENCE")
    print("=" * 70)

    print(
        "\nS1 before scenes :",
        result["sentinel1_before_scene_count"]
    )

    print(
        "S1 after scenes  :",
        result["sentinel1_after_scene_count"]
    )

    print(
        "S2 before scenes :",
        result["sentinel2_before_scene_count"]
    )

    print(
        "S2 after scenes  :",
        result["sentinel2_after_scene_count"]
    )

    print(
        "\nS2 candidate new water :",
        result[
            "sentinel2_candidate_new_water_ha"
        ],
        "ha"
    )

    print(
        "S2 net water change    :",
        result[
            "sentinel2_net_water_change_ha"
        ],
        "ha"
    )

    print(
        "\nS1 mean VV change     :",
        result[
            "sentinel1_mean_vv_change_db"
        ]
    )

    print(
        "S1 candidate new water:",
        result[
            "sentinel1_candidate_new_water_ha"
        ]
    )

    print(
        "\nEvidence points:",
        result[
            "satellite_evidence_points"
        ]
    )

    print(
        "Status:",
        result[
            "satellite_evidence_status"
        ]
    )

    print("\nReasons:")

    for reason in result["evidence_reasons"]:

        print(
            " •",
            reason
        )

    # --------------------------------------------------------
    # MongoDB
    # --------------------------------------------------------

    save_to_mongodb(
        result,
        row
    )

    print("\n💾 Saved to MongoDB")
    print("Collection: satellite_metrics")

    print("\n" + "=" * 70)

    print(
        "✅ SATELLITE INTEGRATION COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()