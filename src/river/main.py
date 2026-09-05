# TRINETRA - River Hydrology Pipeline

from processor import process_dataframe, save_data
from cwc_api import fetch_cwc_data


if __name__ == "__main__":

    print("=" * 70)
    print("🌊 TRINETRA - River Hydrology Pipeline")
    print("=" * 70)

    print("\n1️⃣ Fetching CWC data from NWDP API...")

    try:

        api_df = fetch_cwc_data()

        print(
            f"\n✅ API records received: "
            f"{len(api_df)}"
        )

        print("\n2️⃣ Processing API data...")

        processed_df = process_dataframe(
            api_df
        )


        print("\n3️⃣ Saving API-derived river features...")

        save_data(processed_df)

        print(
            "\n✅ API river pipeline completed successfully."
        )

        print(
            f"📊 Final processed records: "
            f"{len(processed_df)}"
        )

    except Exception as e:

        print("\n❌ CWC API pipeline failed:")

        print(
            f"   {type(e).__name__}: {e}"
        )

    print("\n" + "=" * 70)
    print("🌊 TRINETRA RIVER PIPELINE FINISHED")
    print("=" * 70)