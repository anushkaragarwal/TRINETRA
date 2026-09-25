from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "sentinel1_metadata.csv"
)


# =========================================================
# TRINETRA SENTINEL-1 ANALYSIS WINDOW
# =========================================================
# Required satellite analysis period:
#
# 19 August 2026 → 19 September 2026
#
# Metadata timestamps are stored in UTC.
# Window is defined in IST and converted to UTC.
# =========================================================

WINDOW_START_IST = pd.Timestamp(
    "2026-08-19 00:00:00",
    tz="Asia/Kolkata",
)

WINDOW_END_IST = pd.Timestamp(
    "2026-09-19 23:59:59",
    tz="Asia/Kolkata",
)

WINDOW_START_UTC = WINDOW_START_IST.tz_convert("UTC")
WINDOW_END_UTC = WINDOW_END_IST.tz_convert("UTC")


def main():

    print("📥 Loading Sentinel-1 metadata...")

    if not INPUT_PATH.exists():
        print("\n❌ Sentinel-1 metadata file not found:")
        print(INPUT_PATH)
        return

    df = pd.read_csv(
        INPUT_PATH,
        parse_dates=[
            "acquisition_time_utc",
            "completion_time_utc",
        ],
    )

    # -----------------------------------------------------
    # Clean acquisition timestamps
    # -----------------------------------------------------

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
    ).reset_index(drop=True)


    # =====================================================
    # FILTER REQUIRED ANALYSIS WINDOW
    # =====================================================

    nearby = df[
        (
            df["acquisition_time_utc"]
            >= WINDOW_START_UTC
        )
        &
        (
            df["acquisition_time_utc"]
            <= WINDOW_END_UTC
        )
    ].copy()


    # =====================================================
    # DISPLAY WINDOW
    # =====================================================

    print("\n" + "=" * 70)
    print("📡 TRINETRA SENTINEL-1 ANALYSIS")
    print("=" * 70)

    print(
        "\nAnalysis window (IST):"
    )

    print(
        f"{WINDOW_START_IST.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        f" → "
        f"{WINDOW_END_IST.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )

    print(
        "\nAnalysis window (UTC):"
    )

    print(
        f"{WINDOW_START_UTC.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        f" → "
        f"{WINDOW_END_UTC.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )


    # =====================================================
    # NO DATA
    # =====================================================

    if nearby.empty:

        print(
            "\n⚠️ No Sentinel-1 scenes found "
            "inside the requested window."
        )

        print(
            "\nPossible reason:"
        )

        print(
            "The current sentinel1_metadata.csv "
            "does not contain products for this period."
        )

        return


    # =====================================================
    # CALCULATE RELATION TO WINDOW
    # =====================================================

    # Split the requested period into two halves.
    #
    # BEFORE:
    # 19 Aug → 31 Aug
    #
    # AFTER:
    # 1 Sep → 19 Sep
    #
    # This gives us a practical before/after grouping
    # for the MVP satellite analysis window.

    midpoint = pd.Timestamp(
        "2026-09-01 00:00:00",
        tz="UTC",
    )

    nearby["analysis_period"] = nearby[
        "acquisition_time_utc"
    ].apply(
        lambda timestamp:
        "BEFORE"
        if timestamp < midpoint
        else "AFTER"
    )


    # =====================================================
    # PRINT ALL AVAILABLE SCENES
    # =====================================================

    print(
        f"\n✅ Sentinel-1 scenes found: "
        f"{len(nearby)}"
    )

    print("\n📋 Available Sentinel-1 scenes:\n")

    columns_to_show = [
        "product_name",
        "acquisition_time_utc",
        "analysis_period",
        "product_id",
    ]

    existing_columns = [
        column
        for column in columns_to_show
        if column in nearby.columns
    ]

    print(
        nearby[
            existing_columns
        ].to_string(
            index=False
        )
    )


    # =====================================================
    # BEFORE / AFTER GROUPS
    # =====================================================

    before = nearby[
        nearby["analysis_period"] == "BEFORE"
    ].copy()

    after = nearby[
        nearby["analysis_period"] == "AFTER"
    ].copy()


    print("\n" + "-" * 70)

    print(
        f"📊 BEFORE scenes: "
        f"{len(before)}"
    )

    print(
        f"📊 AFTER scenes : "
        f"{len(after)}"
    )


    # =====================================================
    # BEST BEFORE / AFTER CANDIDATES
    # =====================================================

    if not before.empty:

        best_before = before.iloc[-1]

        print(
            "\n⭐ Latest BEFORE scene"
        )

        print(
            f"Time       : "
            f"{best_before['acquisition_time_utc']}"
        )

        print(
            f"Product ID : "
            f"{best_before['product_id']}"
        )

        print(
            f"Product    : "
            f"{best_before['product_name']}"
        )

    else:

        print(
            "\n⚠️ No BEFORE Sentinel-1 scene "
            "is currently available."
        )


    if not after.empty:

        best_after = after.iloc[0]

        print(
            "\n⭐ Earliest AFTER scene"
        )

        print(
            f"Time       : "
            f"{best_after['acquisition_time_utc']}"
        )

        print(
            f"Product ID : "
            f"{best_after['product_id']}"
        )

        print(
            f"Product    : "
            f"{best_after['product_name']}"
        )

    else:

        print(
            "\n⚠️ No AFTER Sentinel-1 scene "
            "is currently available."
        )


    # =====================================================
    # FINAL STATUS
    # =====================================================

    print("\n" + "=" * 70)

    if not before.empty and not after.empty:

        print(
            "✅ Sentinel-1 before/after scene selection ready."
        )

        print(
            "These scenes can now be used for "
            "SAR VV change / candidate water analysis."
        )

    elif not nearby.empty:

        print(
            "⚠️ Sentinel-1 metadata exists, "
            "but a complete before/after pair "
            "is not currently available."
        )

    else:

        print(
            "❌ Sentinel-1 analysis cannot proceed "
            "with the current metadata."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()