from pathlib import Path
from datetime import datetime, timezone
import os

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "sentinel1_metadata.csv"
)

load_dotenv(ROOT / ".env")


# =========================================================
# MONGODB
# =========================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI"
)

MONGODB_DB = os.getenv(
    "MONGODB_DB",
    "trinetra"
)

COLLECTION_NAME = (
    "sentinel1_metadata"
)


# =========================================================
# ANALYSIS WINDOW
# =========================================================

START = pd.Timestamp(
    "2026-08-19 00:00:00",
    tz="UTC",
)

END = pd.Timestamp(
    "2026-09-19 23:59:59",
    tz="UTC",
)


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n🚀 TRINETRA Sentinel-1 → MongoDB"
    )

    print(
        "19 Aug 2026 → 19 Sep 2026"
    )


    # -----------------------------------------------------
    # Check CSV
    # -----------------------------------------------------

    if not CSV_PATH.exists():

        print(
            "\n❌ Sentinel-1 metadata file not found:"
        )

        print(CSV_PATH)

        return


    print(
        "\n📥 Loading Sentinel-1 metadata..."
    )


    df = pd.read_csv(
        CSV_PATH
    )


    # -----------------------------------------------------
    # Parse acquisition time
    # -----------------------------------------------------

    df[
        "acquisition_time_utc"
    ] = pd.to_datetime(
        df[
            "acquisition_time_utc"
        ],
        errors="coerce",
        utc=True,
    )


    df = df.dropna(
        subset=[
            "acquisition_time_utc"
        ]
    ).copy()


    # -----------------------------------------------------
    # Filter requested window
    # -----------------------------------------------------

    df = df[
        (
            df[
                "acquisition_time_utc"
            ] >= START
        )
        &
        (
            df[
                "acquisition_time_utc"
            ] <= END
        )
    ].copy()


    df = df.sort_values(
        "acquisition_time_utc"
    )


    print(
        f"\n✅ S1 records in window: "
        f"{len(df)}"
    )


    if df.empty:

        print(
            "\n⚠️ No Sentinel-1 records "
            "available in the requested window."
        )

        return


    # =====================================================
    # BEFORE / AFTER
    # =====================================================

    cutoff = pd.Timestamp(
        "2026-09-01 00:00:00",
        tz="UTC",
    )


    df[
        "analysis_period"
    ] = df[
        "acquisition_time_utc"
    ].apply(
        lambda x:
        "BEFORE"
        if x < cutoff
        else "AFTER"
    )


    # =====================================================
    # MONGODB
    # =====================================================

    if not MONGODB_URI:

        raise ValueError(
            "MONGODB_URI missing in .env"
        )


    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    )


    client.admin.command(
        "ping"
    )


    db = client[
        MONGODB_DB
    ]

    collection = db[
        COLLECTION_NAME
    ]


    # =====================================================
    # SAVE RECORDS
    # =====================================================

    inserted = 0
    updated = 0


    for _, row in df.iterrows():

        document = row.to_dict()


        # Convert pandas timestamp
        # to Python datetime.

        acquisition_time = (
            document.get(
                "acquisition_time_utc"
            )
        )

        if pd.notna(
            acquisition_time
        ):

            document[
                "acquisition_time_utc"
            ] = acquisition_time.to_pydatetime()


        # Completion time

        if (
            "completion_time_utc"
            in document
        ):

            completion = pd.to_datetime(
                document[
                    "completion_time_utc"
                ],
                errors="coerce",
                utc=True,
            )

            if pd.notna(
                completion
            ):

                document[
                    "completion_time_utc"
                ] = completion.to_pydatetime()


        # Add source information

        document[
            "source"
        ] = "Copernicus Data Space"


        document[
            "satellite"
        ] = "Sentinel-1"


        document[
            "analysis_window"
        ] = {
            "start":
                START.to_pydatetime(),

            "end":
                END.to_pydatetime(),
        }


        document[
            "created_at"
        ] = datetime.now(
            timezone.utc
        )


        product_id = document.get(
            "product_id"
        )


        if not product_id:
            continue


        result = collection.update_one(
            {
                "product_id":
                    product_id
            },
            {
                "$set":
                    document
            },
            upsert=True,
        )


        if result.upserted_id:

            inserted += 1

        else:

            updated += 1


    # =====================================================
    # INDEXES
    # =====================================================

    collection.create_index(
        "product_id",
        unique=True,
    )

    collection.create_index(
        "acquisition_time_utc"
    )

    collection.create_index(
        "analysis_period"
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    before_count = len(
        df[
            df[
                "analysis_period"
            ] == "BEFORE"
        ]
    )


    after_count = len(
        df[
            df[
                "analysis_period"
            ] == "AFTER"
        ]
    )


    unique_acquisitions = (
        df[
            "acquisition_time_utc"
        ]
        .drop_duplicates()
        .sort_values()
    )


    print(
        "\n" + "=" * 70
    )

    print(
        "🛰️ SENTINEL-1 MONGODB SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"\nProduct records : "
        f"{len(df)}"
    )

    print(
        f"Unique acquisitions : "
        f"{len(unique_acquisitions)}"
    )

    print(
        f"BEFORE records : "
        f"{before_count}"
    )

    print(
        f"AFTER records : "
        f"{after_count}"
    )

    print(
        f"\nNew MongoDB records : "
        f"{inserted}"
    )

    print(
        f"Updated records : "
        f"{updated}"
    )

    print(
        f"\nCollection : "
        f"{COLLECTION_NAME}"
    )


    print(
        "\nAcquisition times:"
    )

    for timestamp in unique_acquisitions:

        print(
            f"  {timestamp}"
        )


    print(
        "\n" + "=" * 70
    )

    print(
        "✅ Sentinel-1 metadata "
        "saved to MongoDB."
    )

    client.close()


if __name__ == "__main__":
    main()