from cwc_api import fetch_cwc_data
from processor import process_dataframe


if __name__ == "__main__":

    print("=" * 70)
    print("🌊 TRINETRA - River Hydrology Pipeline")
    print("=" * 70)

    try:

        print("\n1️⃣ Fetching CWC data from NWDP API...")

        api_df = fetch_cwc_data()

        print(
            f"\n✅ API records received: "
            f"{len(api_df)}"
        )

        print("\n2️⃣ Processing CWC data...")

        river_data = process_dataframe(
            api_df
        )

        print(
            "\n3️⃣ River data ready for AI integration."
        )

        print(
            f"📊 Final records: "
            f"{len(river_data)}"
        )

        print("\n📋 Available columns:")

        for column in river_data.columns:
            print(f"   → {column}")

        print(
            "\n✅ RIVER DATA PIPELINE COMPLETED"
        )

    except Exception as e:

        print("\n❌ River pipeline failed:")

        print(
            f"   {type(e).__name__}: {e}"
        )

    print("\n" + "=" * 70)
    print("🌊 TRINETRA RIVER PIPELINE FINISHED")
    print("=" * 70)