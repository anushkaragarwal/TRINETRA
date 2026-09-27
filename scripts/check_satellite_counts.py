import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

client = MongoClient(
    os.getenv("MONGODB_URI")
)

db = client[
    os.getenv("MONGODB_DB", "trinetra")
]

START = datetime(
    2026, 8, 19,
    tzinfo=timezone.utc
)

END = datetime(
    2026, 9, 19, 23, 59, 59,
    tzinfo=timezone.utc
)


print("\n========================================")
print("TRINETRA SATELLITE RECORD CHECK")
print("19 Aug 2026 → 19 Sep 2026")
print("========================================")


# -----------------------------------------
# SENTINEL-2
# -----------------------------------------

s2 = db.sentinel2_metadata

s2_records = list(
    s2.find({
        "acquisition_time_utc": {
            "$gte": START.isoformat(),
            "$lte": END.isoformat()
        }
    })
)

print(
    f"\nSentinel-2 product records: "
    f"{len(s2_records)}"
)

s2_times = sorted(
    set(
        doc.get("acquisition_time_utc")
        for doc in s2_records
        if doc.get("acquisition_time_utc")
    )
)

print(
    f"Sentinel-2 unique acquisitions: "
    f"{len(s2_times)}"
)

print("\nS2 acquisitions:")

for time in s2_times:
    print(" ", time)


# -----------------------------------------
# SENTINEL-1
# -----------------------------------------

s1 = db.sentinel1_metadata

s1_records = list(
    s1.find({
        "acquisition_time_utc": {
            "$gte": START,
"$lte": END
        }
    })
)

print(
    f"\nSentinel-1 product records: "
    f"{len(s1_records)}"
)

s1_times = sorted(
    set(
        doc.get("acquisition_time_utc")
        for doc in s1_records
        if doc.get("acquisition_time_utc")
    )
)

print(
    f"Sentinel-1 unique acquisitions: "
    f"{len(s1_times)}"
)

print("\nS1 acquisitions:")

for time in s1_times:
    print(" ", time)


# -----------------------------------------
# TOTAL
# -----------------------------------------

print("\n========================================")

print(
    f"TOTAL S1 + S2 product records: "
    f"{len(s1_records) + len(s2_records)}"
)

print(
    f"TOTAL unique acquisitions: "
    f"{len(s1_times) + len(s2_times)}"
)

print("========================================")

client.close()