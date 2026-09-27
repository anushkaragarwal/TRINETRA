import os
import csv
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB", "trinetra")

CSV_PATH = "data/satellite/gee_event_metrics.csv"

EVENT_ID = "trinetra_2026_08_19_2026_09_19"


def parse_time(value):
    if isinstance(value, datetime):
        t = value
    elif isinstance(value, str):
        t = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    else:
        return None

    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)

    return t


def main():

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]

    s2 = db["sentinel2_metadata"]

    cutoff = datetime(
        2026, 9, 1,
        tzinfo=timezone.utc
    )

    before = set()
    after = set()

    # --------------------------------------------------
    # Count UNIQUE Sentinel-2 acquisitions
    # --------------------------------------------------

    for doc in s2.find({}):

        # Skip derived metrics document
        if doc.get("document_type") == "derived_metrics":
            continue

        if doc.get("satellite") != "Sentinel-2":
            continue

        t = parse_time(
            doc.get("acquisition_time_utc")
        )

        if not t:
            continue

        # Timestamp is same for tiles from one acquisition.
        # Set removes duplicate tile/product records.
        key = t.isoformat()

        if t < cutoff:
            before.add(key)
        else:
            after.add(key)

    s2_before = len(before)
    s2_after = len(after)

    print("=" * 70)
    print("🔧 FIXING SENTINEL-2 UNIQUE SCENE COUNTS")
    print("=" * 70)

    print()
    print("S2 unique BEFORE:", s2_before)
    print("S2 unique AFTER :", s2_after)

    # --------------------------------------------------
    # Update CSV
    # --------------------------------------------------

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not rows:
        raise RuntimeError("CSV is empty")

    rows[0]["sentinel2_before_scene_count"] = str(
        s2_before
    )

    rows[0]["sentinel2_after_scene_count"] = str(
        s2_after
    )

    with open(
        CSV_PATH,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n✅ CSV updated:")
    print(CSV_PATH)

    # --------------------------------------------------
    # Update MongoDB satellite_metrics
    # --------------------------------------------------

    db["satellite_metrics"].update_one(
        {
            "event_id": EVENT_ID
        },
        {
            "$set": {
                "satellite_evidence.sentinel2_before_scene_count":
                    s2_before,

                "satellite_evidence.sentinel2_after_scene_count":
                    s2_after,

                "source_metrics.sentinel2_before_scene_count":
                    s2_before,

                "source_metrics.sentinel2_after_scene_count":
                    s2_after,

                "sentinel2_before_scene_count":
                    s2_before,

                "sentinel2_after_scene_count":
                    s2_after,

                "updated_at":
                    datetime.now(timezone.utc)
            }
        }
    )

    print("\n✅ MongoDB updated")
    print("Collection: satellite_metrics")

    print("\n" + "=" * 70)
    print("🎯 FINAL COUNTS")
    print("=" * 70)

    print()
    print("Sentinel-1 BEFORE :", 5)
    print("Sentinel-1 AFTER  :", 2)
    print("Sentinel-2 BEFORE :", s2_before)
    print("Sentinel-2 AFTER  :", s2_after)

    print()
    print("🌊 S2 candidate new water : 3386.84 ha")
    print("🌊 S2 net water change    : 3386.84 ha")

    print("\n✅ COUNT CORRECTION COMPLETE")


if __name__ == "__main__":
    main()