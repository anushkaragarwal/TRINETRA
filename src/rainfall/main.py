# TRINETRA - Rainfall Hydrology Pipeline

from imd_api import fetch_rainfall_data
from processor import process_dataframe


if __name__ == "__main__":

    print("=" * 70)
    print("🌧️ TRINETRA - RAINFALL PIPELINE")
    print("=" * 70)

    try:

        # ====================================================
        # 1. FETCH
        # ====================================================

        print(
            "\n1️⃣ Fetching rainfall data "
            "from NWDP / IMD API..."
        )

        api_df = fetch_rainfall_data()

        print(
            f"\n✅ API records received: "
            f"{len(api_df)}"
        )

        # ====================================================
        # 2. PROCESS
        # ====================================================

        print(
            "\n2️⃣ Processing rainfall data..."
        )

        rainfall_data = process_dataframe(
            api_df
        )

        # ====================================================
        # 3. AI HANDOFF
        # ====================================================

        print(
            "\n3️⃣ Rainfall data ready "
            "for AI integration."
        )

        print(
            f"📊 Final records: "
            f"{len(rainfall_data)}"
        )

        print(
            "\n📋 Available columns:"
        )

        for column in rainfall_data.columns:

            print(
                f"   → {column}"
            )

        print(
            "\n📌 Data is kept in memory."
        )

        print(
            "📌 No processed CSV generated."
        )

        print(
            "\n✅ RAINFALL DATA PIPELINE COMPLETED"
        )

    except Exception as e:

        print(
            "\n❌ Rainfall pipeline failed:"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

    print(
        "\n" + "=" * 70
    )

    print(
        "🌧️ TRINETRA RAINFALL PIPELINE FINISHED"
    )

    print(
        "=" * 70
    )