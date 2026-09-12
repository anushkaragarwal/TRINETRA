import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.features import rasterize


# =========================================================
# PATHS
# =========================================================

dem_path = "data/processed/dem/dem_utm44n.tif"

landslide_path = "data/features/historical_landslides_2014_2017.gpkg"

terrain_path = "data/features/terrain_features.csv"

output_path = "data/features/terrain_features_labeled_2014_2017.csv"


# =========================================================
# 1. LOAD DEM GRID
# =========================================================

print("Loading DEM grid...")

with rasterio.open(dem_path) as src:

    dem = src.read(1)

    transform = src.transform
    crs = src.crs
    shape_dem = src.shape

print("DEM shape:", shape_dem)
print("DEM CRS:", crs)
print("Resolution:", transform.a, transform.e)


# =========================================================
# 2. LOAD LANDSLIDE POLYGONS
# =========================================================

print("\nLoading landslides...")

landslides = gpd.read_file(landslide_path)

print("Landslides:", len(landslides))
print("Original CRS:", landslides.crs)


# =========================================================
# 3. REPROJECT TO DEM CRS
# =========================================================

landslides = landslides.to_crs(crs)

print("Reprojected CRS:", landslides.crs)


# =========================================================
# 4. RASTERIZE LANDSLIDES
# =========================================================

print("\nRasterizing landslides...")

shapes = [
    (geom, 1)
    for geom in landslides.geometry
    if geom is not None and not geom.is_empty
]

landslide_mask = rasterize(
    shapes=shapes,
    out_shape=shape_dem,
    transform=transform,
    fill=0,
    dtype="uint8",
    all_touched=True
)

print("Landslide cells:", int(landslide_mask.sum()))


# =========================================================
# 5. LOAD TERRAIN CSV
# =========================================================

print("\nLoading terrain features...")

terrain = pd.read_csv(terrain_path)

print("Terrain rows:", len(terrain))


# =========================================================
# 6. GET ROW/COLUMN FROM CELL ID
# =========================================================

parts = terrain["cell_id"].str.extract(
    r"cell_(\d+)_(\d+)"
)

# Check that every cell_id was parsed
if parts.isna().any().any():
    bad = terrain.loc[parts.isna().any(axis=1), "cell_id"].head(10)

    print("ERROR: Some cell_id values could not be parsed:")
    print(bad.to_list())

    raise ValueError("Invalid cell_id format found.")

terrain["row"] = parts[0].astype(int)
terrain["col"] = parts[1].astype(int)

# =========================================================
# 7. ASSIGN HISTORICAL LANDSLIDE LABEL
# =========================================================

terrain["historical_landslide"] = landslide_mask[
    terrain["row"].values,
    terrain["col"].values
]


# =========================================================
# 8. REMOVE TEMPORARY ROW/COL
# =========================================================

terrain.drop(
    columns=["row", "col"],
    inplace=True
)


# =========================================================
# 9. SUMMARY
# =========================================================

total = len(terrain)

positive = int(
    terrain["historical_landslide"].sum()
)

negative = total - positive

print("\n========================================")
print("LABELING COMPLETE")
print("========================================")

print("Total terrain cells:", total)
print("Historical landslide cells:", positive)
print("Non-landslide cells:", negative)

print(
    "Positive percentage:",
    round((positive / total) * 100, 6),
    "%"
)


# =========================================================
# 10. SAVE
# =========================================================

terrain.to_csv(
    output_path,
    index=False
)

print("\nSaved:")
print(output_path)

print("\nColumns:")

for col in terrain.columns:
    print("-", col)