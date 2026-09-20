import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.features import rasterize


# =========================================================
# PATHS
# =========================================================

DEM_PATH = (
    "data/processed/dem/dem_utm44n.tif"
)

LANDSLIDE_PATH = (
    "data/features/historical_landslides_2014_2017.gpkg"
)

TERRAIN_PATH = (
    "data/features/terrain_features.csv"
)

OUTPUT_PATH = (
    "data/features/terrain_features_labeled_2014_2017.csv"
)


# =========================================================
# 1. LOAD DEM GRID
# =========================================================

print("Loading DEM grid...")

with rasterio.open(DEM_PATH) as src:

    transform = src.transform
    crs = src.crs
    dem_shape = src.shape

print("DEM shape:", dem_shape)
print("DEM CRS:", crs)
print("Resolution:", src.res)


# =========================================================
# 2. LOAD HISTORICAL LANDSLIDES
# =========================================================

print("\nLoading historical landslides...")

landslides = gpd.read_file(
    LANDSLIDE_PATH
)

print("Landslide polygons:", len(landslides))
print("Columns:", landslides.columns.tolist())
print("Original CRS:", landslides.crs)


# =========================================================
# 3. VALIDATE REQUIRED COLUMNS
# =========================================================

required_columns = [
    "landslide_id",
    "year",
    "geometry"
]

missing = [
    column
    for column in required_columns
    if column not in landslides.columns
]

if missing:
    raise ValueError(
        f"Missing required landslide columns: {missing}"
    )


# =========================================================
# 4. REPROJECT TO DEM CRS
# =========================================================

landslides = landslides.to_crs(crs)

print("Reprojected CRS:", landslides.crs)


# =========================================================
# 5. REMOVE INVALID GEOMETRIES
# =========================================================

landslides = landslides[
    landslides.geometry.notna()
    & ~landslides.geometry.is_empty
].copy()


# =========================================================
# 6. CREATE UNIQUE RASTER VALUE FOR EACH LANDSLIDE
# =========================================================

# Raster values:
#
# 0 = no mapped historical landslide
# 1 = LS_001
# 2 = LS_002
# 3 = LS_003
# ...
#
# This lets us preserve the event identity.

landslides = landslides.reset_index(drop=True)

landslides["raster_id"] = (
    np.arange(len(landslides)) + 1
)


# =========================================================
# 7. RASTERIZE LANDSLIDES
# =========================================================

print("\nRasterizing landslides...")

shapes = [
    (row.geometry, int(row.raster_id))
    for _, row in landslides.iterrows()
]

landslide_id_raster = rasterize(
    shapes=shapes,
    out_shape=dem_shape,
    transform=transform,
    fill=0,
    dtype="int16",
    all_touched=True
)


# =========================================================
# 8. LOAD TERRAIN FEATURES
# =========================================================

print("\nLoading terrain features...")

terrain = pd.read_csv(
    TERRAIN_PATH
)

print("Terrain rows:", len(terrain))


# =========================================================
# 9. EXTRACT ROW/COLUMN FROM CELL ID
# =========================================================

parts = terrain["cell_id"].str.extract(
    r"cell_(\d+)_(\d+)"
)

if parts.isna().any().any():

    bad = terrain.loc[
        parts.isna().any(axis=1),
        "cell_id"
    ].head(10)

    print(
        "ERROR: Invalid cell_id values:"
    )

    print(
        bad.to_list()
    )

    raise ValueError(
        "Invalid cell_id format found."
    )


terrain["row"] = (
    parts[0].astype(int)
)

terrain["col"] = (
    parts[1].astype(int)
)


# =========================================================
# 10. ASSIGN RASTER LANDSLIDE ID
# =========================================================

terrain["landslide_raster_id"] = (
    landslide_id_raster[
        terrain["row"].values,
        terrain["col"].values
    ]
)


# =========================================================
# 11. CREATE HISTORICAL LANDSLIDE LABEL
# =========================================================

terrain["historical_landslide"] = (
    terrain["landslide_raster_id"] > 0
).astype("uint8")


# =========================================================
# 12. MAP RASTER ID → ACTUAL LANDSLIDE ID/YEAR
# =========================================================

landslide_lookup = (
    landslides[
        [
            "raster_id",
            "landslide_id",
            "year"
        ]
    ]
    .set_index("raster_id")
)


terrain["landslide_id"] = (
    terrain["landslide_raster_id"]
    .map(
        landslide_lookup["landslide_id"]
    )
)

terrain["landslide_year"] = (
    terrain["landslide_raster_id"]
    .map(
        landslide_lookup["year"]
    )
)


# =========================================================
# 13. CLEAN TEMPORARY COLUMNS
# =========================================================

terrain.drop(
    columns=[
        "row",
        "col",
        "landslide_raster_id"
    ],
    inplace=True
)


# =========================================================
# 14. SUMMARY
# =========================================================

total = len(terrain)

positive = int(
    terrain["historical_landslide"].sum()
)

negative = (
    total - positive
)

print("\n" + "=" * 60)
print("LANDSLIDE TERRAIN LABELING COMPLETE")
print("=" * 60)

print(
    "Total terrain cells:",
    total
)

print(
    "Historical landslide cells:",
    positive
)

print(
    "Non-landslide cells:",
    negative
)

print(
    "Positive percentage:",
    round(
        positive / total * 100,
        6
    ),
    "%"
)


# =========================================================
# 15. LANDSLIDE CELL DISTRIBUTION
# =========================================================

print("\nCells per landslide:")

print(
    terrain[
        terrain["historical_landslide"] == 1
    ]["landslide_id"]
    .value_counts()
    .sort_index()
)


# =========================================================
# 16. SAVE
# =========================================================

terrain.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved:")
print(OUTPUT_PATH)

print("\nFinal columns:")

for column in terrain.columns:
    print("-", column)