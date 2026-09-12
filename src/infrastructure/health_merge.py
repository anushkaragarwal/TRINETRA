import csv
from pathlib import Path

FACILITY_FILE = Path("data/health/health_facilities.csv")
CAPABILITY_FILE = Path("data/health/emergency_capabilities.csv")
OUTPUT_FILE = Path("data/health/health_facilities_final.csv")


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


print("🏥 Loading health facility data...")

facilities = read_csv(FACILITY_FILE)
capabilities = read_csv(CAPABILITY_FILE)

capability_map = {
    row["facility_type"].strip().lower(): row
    for row in capabilities
}

final_rows = []

for facility in facilities:

    facility_type = facility["facility_type"].strip()

    capability = capability_map.get(
        facility_type.lower(),
        {}
    )

    facility["emergency_available"] = capability.get(
        "emergency_available", "Unknown"
    )

    facility["ambulance_available"] = capability.get(
        "ambulance_available", "Unknown"
    )

    facility["referral_facility"] = capability.get(
        "referral_facility", "Unknown"
    )

    final_rows.append(facility)


fieldnames = [
    "facility_name",
    "facility_type",
    "district",
    "location",
    "pincode",
    "phone",
    "latitude",
    "longitude",
    "emergency_available",
    "ambulance_available",
    "referral_facility",
    "source"
]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(final_rows)


print("\n🎉 Health dataset created!")
print(f"🏥 Facilities: {len(final_rows)}")
print(f"💾 Saved: {OUTPUT_FILE}")