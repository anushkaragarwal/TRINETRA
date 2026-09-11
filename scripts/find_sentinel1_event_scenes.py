from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "sentinel1_metadata.csv"
)

# ---------------------------------------------------------
# SELECTED TRINETRA RIVER EVENT
# ---------------------------------------------------------
# CWC river event time is assumed to be Indian Standard Time.
# Sentinel-1 timestamps are in UTC.
#
# 17 July 2026, 18:30 IST
# = 17 July 2026, 13:00 UTC
# ---------------------------------------------------------
EVENT_TIME_IST = pd.Timestamp(
    "2026-07-17 18:30:00",
    tz="Asia/Kolkata",
)

EVENT_TIME_UTC = EVENT_TIME_IST.tz_convert(
    "UTC"
)

BEFORE_DAYS = 14
AFTER_DAYS = 14


def main():
    print("📥 Loading clean Sentinel-1 metadata...")

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[
            "acquisition_time_utc",
            "completion_time_utc",
        ],
    )

    # Ensure acquisition timestamps are UTC-aware.
    df["acquisition_time_utc"] = pd.to_datetime(
        df["acquisition_time_utc"],
        errors="coerce",
        utc=True,
    )

    df = df.dropna(
        subset=["acquisition_time_utc"]
    ).copy()

    df = df.sort_values(
        by="acquisition_time_utc"
    ).copy()

    # Build time window around the exact event.
    event_start = EVENT_TIME_UTC - pd.Timedelta(
        days=BEFORE_DAYS
    )

    event_end = EVENT_TIME_UTC + pd.Timedelta(
        days=AFTER_DAYS
    )

    nearby = df[
        (
            df["acquisition_time_utc"] >= event_start
        )
        & (
            df["acquisition_time_utc"] <= event_end
        )
    ].copy()

    print("\n📍 Sentinel-1 event-scene search")
    print(
        f"Event time (IST): "
        f"{EVENT_TIME_IST.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    print(
        f"Event time (UTC): "
        f"{EVENT_TIME_UTC.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    print(
        f"Search window: "
        f"{event_start.strftime('%Y-%m-%d')} → "
        f"{event_end.strftime('%Y-%m-%d')}"
    )

    if nearby.empty:
        print("\n⚠️ No Sentinel-1 scenes found in this window.")
        print(
            "Increase BEFORE_DAYS and AFTER_DAYS "
            "to 21 or 30 days."
        )
        return

    # Calculate exact distance from selected event.
    nearby["hours_from_event"] = (
        nearby["acquisition_time_utc"]
        - EVENT_TIME_UTC
    ).dt.total_seconds() / 3600

    nearby["days_from_event"] = (
        nearby["hours_from_event"] / 24
    ).round(2)

    # Important: use exact time, not just calendar date.
    nearby["relation_to_event"] = (
        nearby["hours_from_event"]
        .apply(
            lambda hours: (
                "BEFORE"
                if hours < 0
                else "AFTER"
            )
        )
    )

    nearby = nearby.sort_values(
        by="acquisition_time_utc"
    )

    print(f"\n✅ Scenes found: {len(nearby)}")

    print("\n📋 Candidate before/after scenes:")
    print(
        nearby[
            [
                "product_name",
                "acquisition_time_utc",
                "hours_from_event",
                "days_from_event",
                "relation_to_event",
                "product_id",
            ]
        ].to_string(
            index=False
        )
    )

    before = nearby[
        nearby["relation_to_event"] == "BEFORE"
    ].copy()

    after = nearby[
        nearby["relation_to_event"] == "AFTER"
    ].copy()

    if before.empty:
        print("\n⚠️ No before-event Sentinel-1 scene found.")

    if after.empty:
        print("\n⚠️ No after-event Sentinel-1 scene found.")

    if not before.empty and not after.empty:
        # Last acquisition before the event.
        best_before = before.iloc[-1]

        # First acquisition after the event.
        best_after = after.iloc[0]

        print("\n⭐ Recommended Sentinel-1 scene pair")

        print("\nBEFORE EVENT")
        print(
            f"Time       : "
            f"{best_before['acquisition_time_utc']}"
        )
        print(
            f"Hours away : "
            f"{best_before['hours_from_event']:.2f}"
        )
        print(
            f"Product ID : "
            f"{best_before['product_id']}"
        )
        print(
            f"Product    : "
            f"{best_before['product_name']}"
        )

        print("\nAFTER EVENT")
        print(
            f"Time       : "
            f"{best_after['acquisition_time_utc']}"
        )
        print(
            f"Hours away : "
            f"{best_after['hours_from_event']:.2f}"
        )
        print(
            f"Product ID : "
            f"{best_after['product_id']}"
        )
        print(
            f"Product    : "
            f"{best_after['product_name']}"
        )

        print(
            "\n✅ Pairing logic: last available SAR scene "
            "before the event and first available SAR scene "
            "after the event."
        )

        print(
            "\n⚠️ Interpretation note: This pair is selected "
            "for candidate water/flood-change analysis. "
            "It does not alone confirm a flood; validation "
            "with river telemetry, rainfall, terrain and "
            "official incident evidence is required."
        )


if __name__ == "__main__":
    main()