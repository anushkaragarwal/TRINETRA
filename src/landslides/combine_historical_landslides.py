import geopandas as gpd
import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
LANDSLIDE_2014 = Path(
    "data/features/mvp_landslides_2014.gpkg"
)

LANDSLIDE_2017 = Path(
    "data/features/landslides_2017_polygons.gpkg"
)

OUTPUT = Path(
    "data/features/historical_landslides_2014_2017.gpkg"
)

# -----------------------------
# Load datasets
# -----------------------------
print("Loading 2014 landslides...")
g2014 = gpd.read_file(LANDSLIDE_2014)

print("Loading 2017 landslides...")
g2017 = gpd.read_file(LANDSLIDE_2017)

print("2014 rows:", len(g2014))
print("2017 rows:", len(g2017))

# -----------------------------
# Keep only geometry
# -----------------------------
g2014 = g2014[["geometry"]].copy()
g2017 = g2017[["geometry"]].copy()

g2014["year"] = 2014
g2017["year"] = 2017

# -----------------------------
# Reproject to common CRS
# -----------------------------
g2014 = g2014.to_crs("EPSG:4326")
g2017 = g2017.to_crs("EPSG:4326")

# -----------------------------
# Combine
# -----------------------------
combined = gpd.GeoDataFrame(
    pd.concat([g2014, g2017], ignore_index=True),
    crs="EPSG:4326"
)

# Remove empty geometries
combined = combined[
    combined.geometry.notna()
    & ~combined.geometry.is_empty
].copy()

# Add unique ID
combined.insert(
    0,
    "landslide_id",
    [
        f"LS_{i+1:03d}"
        for i in range(len(combined))
    ]
)

# -----------------------------
# Save
# -----------------------------
OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

combined.to_file(
    OUTPUT,
    driver="GPKG"
)

print("\n" + "=" * 55)
print("HISTORICAL LANDSLIDES COMBINED")
print("=" * 55)
print("2014 features:", len(g2014))
print("2017 features:", len(g2017))
print("Total features:", len(combined))
print("CRS:", combined.crs)
print("Saved:")
print(OUTPUT)