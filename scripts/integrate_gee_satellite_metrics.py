from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

SATELLITE_METRICS_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "gee_event_metrics.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "gee_satellite_evidence_summary.csv"
)


def clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(maximum, value))


def calculate_satellite_evidence_score(row):
    """
    Conservative MVP score.

    A higher score means stronger satellite evidence of
    post-event water expansion. It does not mean confirmed flooding.
    """

    s2_new_water_ha = float(
        row["sentinel2_candidate_new_water_ha"]
    )

    s2_net_change_ha = float(
        row["sentinel2_net_water_change_ha"]
    )

    s1_vv_change_db = float(
        row["sentinel1_mean_vv_change_db"]
    )

    s1_new_water_ha = float(
        row["sentinel1_candidate_new_water_ha"]
    )

    # Sentinel-2 contribution:
    # Positive net water expansion and new-water pixels add evidence.
    optical_score = (
        min(s2_new_water_ha / 50.0, 1.0) * 20.0
        + min(max(s2_net_change_ha, 0.0) / 50.0, 1.0) * 20.0
    )

    # Sentinel-1 contribution:
    # Negative VV change can indicate smoother/open water.
    # Candidate SAR new-water area adds another signal.
    sar_drop_score = (
        min(max(-s1_vv_change_db, 0.0) / 3.0, 1.0) * 30.0
    )

    sar_water_score = (
        min(s1_new_water_ha / 10.0, 1.0) * 30.0
    )

    total_score = (
        optical_score
        + sar_drop_score
        + sar_water_score
    )

    return round(clamp(total_score), 2)


def classify_evidence(score):
    if score >= 70:
        return "STRONG_SATELLITE_EVIDENCE"

    if score >= 40:
        return "MODERATE_SATELLITE_EVIDENCE"

    if score >= 15:
        return "WEAK_SATELLITE_EVIDENCE"

    return "INCONCLUSIVE_SATELLITE_EVIDENCE"


def main():
    df = pd.read_csv(
        SATELLITE_METRICS_PATH
    )

    df["satellite_evidence_score_0_100"] = (
        df.apply(
            calculate_satellite_evidence_score,
            axis=1,
        )
    )

    df["satellite_evidence_class"] = (
        df["satellite_evidence_score_0_100"]
        .apply(classify_evidence)
    )

    summary_columns = [
        "event_id",
        "station_name",
        "event_time_ist",
        "latitude",
        "longitude",
        "sentinel2_before_scene_count",
        "sentinel2_after_scene_count",
        "sentinel2_candidate_new_water_ha",
        "sentinel2_net_water_change_ha",
        "sentinel1_orbit",
        "sentinel1_before_scene_count",
        "sentinel1_after_scene_count",
        "sentinel1_mean_vv_change_db",
        "sentinel1_candidate_new_water_ha",
        "satellite_evidence_score_0_100",
        "satellite_evidence_class",
        "satellite_evidence_status",
    ]

    summary = df[
        summary_columns
    ].copy()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("✅ GEE satellite metrics integrated.")
    print(f"Input : {SATELLITE_METRICS_PATH}")
    print(f"Output: {OUTPUT_PATH}")

    print("\n📊 Satellite evidence summary:")
    print(
        summary.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()