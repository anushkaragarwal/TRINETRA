import requests
import pandas as pd
from pathlib import Path
import time

# ============================================================
# TRINETRA - OpenStreetMap Infrastructure Data
# AOI: Joshimath–Vishnuprayag–Badrinath Corridor
# ============================================================

MIN_LAT = 30.50
MAX_LAT = 30.80
MIN_LON = 79.40
MAX_LON = 79.75

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OUTPUT_DIR = Path("data/infrastructure")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "TRINETRA/1.0 (disaster monitoring research project)",
    "Accept": "application/json",
    "Content-Type": "text/plain; charset=utf-8",
}


def fetch_osm_data(query, output_file):
    """Fetch OSM data from Overpass API and save as CSV."""

    print(f"\n🌐 Fetching {output_file}...")

    try:
        response = requests.post(
            OVERPASS_URL,
            data=query.encode("utf-8"),
            headers=HEADERS,
            timeout=180
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {response.text[:500]}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    rows = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        # Nodes have lat/lon directly.
        # Ways have coordinates under "center".
        latitude = element.get("lat")
        longitude = element.get("lon")

        if latitude is None:
            latitude = element.get("center", {}).get("lat")

        if longitude is None:
            longitude = element.get("center", {}).get("lon")

        rows.append({
            "id": element.get("id"),
            "type": element.get("type"),
            "latitude": latitude,
            "longitude": longitude,
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "healthcare": tags.get("healthcare"),
            "highway": tags.get("highway"),
            "bridge": tags.get("bridge"),
            "building": tags.get("building"),
        })

    df = pd.DataFrame(rows)

    output_path = OUTPUT_DIR / output_file
    df.to_csv(output_path, index=False)

    print(f"✅ {output_file}: {len(df)} records")
    print(f"📁 Saved to: {output_path}")

    return True


# ============================================================
# 1. ROADS
# ============================================================

roads_query = f"""
[out:json][timeout:120];

way["highway"]
(
    {MIN_LAT},
    {MIN_LON},
    {MAX_LAT},
    {MAX_LON}
);

out center tags;
"""

fetch_osm_data(
    roads_query,
    "roads.csv"
)

time.sleep(5)


# ============================================================
# 2. BRIDGES
# ============================================================

bridges_query = f"""
[out:json][timeout:120];

way["bridge"]
(
    {MIN_LAT},
    {MIN_LON},
    {MAX_LAT},
    {MAX_LON}
);

out center tags;
"""

fetch_osm_data(
    bridges_query,
    "bridges.csv"
)

time.sleep(5)


# ============================================================
# 3. SCHOOLS
#    Candidate evacuation shelters
# ============================================================

print("\n🏫 Searching for schools...")

shelters_query = f"""
[out:json][timeout:60];

(
    node["amenity"="school"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    way["amenity"="school"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});
);

out center tags;
"""

fetch_osm_data(
    shelters_query,
    "shelters.csv"
)

time.sleep(5)


# ============================================================
# 4. COMMUNITY CENTRES
#    Additional possible evacuation locations
# ============================================================

print("\n🏢 Searching for community centres...")

community_query = f"""
[out:json][timeout:60];

(
    node["amenity"="community_centre"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    way["amenity"="community_centre"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});
);

out center tags;
"""

fetch_osm_data(
    community_query,
    "community_centres.csv"
)

time.sleep(5)


# ============================================================
# 5. HOSPITALS
# ============================================================

print("\n🏥 Searching for hospitals...")

hospitals_query = f"""
[out:json][timeout:60];

(
    node["amenity"="hospital"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    way["amenity"="hospital"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});
);

out center tags;
"""

fetch_osm_data(
    hospitals_query,
    "hospitals.csv"
)

time.sleep(5)


# ============================================================
# 6. CLINICS / HEALTH CENTRES
# ============================================================

print("\n🩺 Searching for clinics and health centres...")

health_query = f"""
[out:json][timeout:60];

(
    node["amenity"="clinic"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    way["amenity"="clinic"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    node["healthcare"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});

    way["healthcare"]
    ({MIN_LAT},{MIN_LON},{MAX_LAT},{MAX_LON});
);

out center tags;
"""

fetch_osm_data(
    health_query,
    "health_centres.csv"
)


# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 60)
print("🎯 TRINETRA OSM DATA COLLECTION COMPLETE")
print("=" * 60)

print("\n📂 Files:")
print("   • data/infrastructure/roads.csv")
print("   • data/infrastructure/bridges.csv")
print("   • data/infrastructure/shelters.csv")
print("   • data/infrastructure/community_centres.csv")
print("   • data/infrastructure/hospitals.csv")
print("   • data/infrastructure/health_centres.csv")

print("\n🚨 These layers will support:")
print("   → Evacuation routing")
print("   → Candidate safe locations")
print("   → Emergency medical access")