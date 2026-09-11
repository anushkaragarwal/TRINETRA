import rasterio
import numpy as np
import pandas as pd
from pathlib import Path
from rasterio.transform import xy


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_PATH = Path("data/processed/dem")
OUTPUT_PATH = Path("data/features")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


files = {
    "elevation": BASE_PATH / "dem_utm44n.tif",
    "slope": BASE_PATH / "slope_utm44n.tif",
    "aspect": BASE_PATH / "aspect_utm44n.tif",
    "curvature": BASE_PATH / "curvature_utm44n_aligned.tif",
    "flow_accumulation": BASE_PATH / "flow_accumulation_utm44n.tif",
}


# ---------------------------------------------------------
# READ RASTERS
# ---------------------------------------------------------

rasters = {}

for name, path in files.items():

    print(f"Loading {name}...")

    with rasterio.open(path) as src:

        rasters[name] = {
            "data": src.read(1),
            "crs": src.crs,
            "transform": src.transform,
            "shape": src.shape,
            "nodata": src.nodata,
        }


# ---------------------------------------------------------
# REFERENCE RASTER
# ---------------------------------------------------------

reference = rasters["elevation"]

height, width = reference["shape"]

print("\n========== RASTER INFORMATION ==========")

print(f"Rows: {height}")
print(f"Columns: {width}")
print(f"Total cells: {height * width:,}")
print(f"CRS: {reference['crs']}")
print(f"Resolution: {reference['transform'].a} m")


# ---------------------------------------------------------
# CHECK SHAPE + CRS
# ---------------------------------------------------------

print("\n========== ALIGNMENT CHECK ==========")

for name, raster in rasters.items():

    same_shape = raster["shape"] == reference["shape"]
    same_crs = raster["crs"] == reference["crs"]

    print(
        f"{name}: "
        f"Shape={same_shape}, "
        f"CRS={same_crs}"
    )

    if not same_shape:
        raise ValueError(f"{name} has different shape.")

    if not same_crs:
        raise ValueError(f"{name} has different CRS.")


# ---------------------------------------------------------
# CREATE VALID DATA MASK
# ---------------------------------------------------------

print("\nCreating valid-data mask...")

mask = np.ones((height, width), dtype=bool)

for name, raster in rasters.items():

    data = raster["data"]

    nodata = raster["nodata"]

    # Remove NaN / infinite values
    mask &= np.isfinite(data)

    # Remove explicit NoData values
    if nodata is not None:
        mask &= data != nodata


print(f"Valid cells: {mask.sum():,}")
print(f"Removed cells: {(~mask).sum():,}")


# ---------------------------------------------------------
# GET CELL ROW/COLUMN
# ---------------------------------------------------------

rows, cols = np.where(mask)


# ---------------------------------------------------------
# GET CELL CENTRE COORDINATES
# ---------------------------------------------------------

xs, ys = xy(
    reference["transform"],
    rows,
    cols,
    offset="center"
)

xs = np.asarray(xs)
ys = np.asarray(ys)


# ---------------------------------------------------------
# CONVERT UTM → LAT/LON
# ---------------------------------------------------------

from rasterio.warp import transform

lon, lat = transform(
    reference["crs"],
    "EPSG:4326",
    xs.tolist(),
    ys.tolist()
)

lon = np.asarray(lon)
lat = np.asarray(lat)


# ---------------------------------------------------------
# BUILD FEATURE TABLE
# ---------------------------------------------------------

print("\nBuilding terrain feature table...")

df = pd.DataFrame({

    "cell_id": [
        f"cell_{r}_{c}"
        for r, c in zip(rows, cols)
    ],

    "lat": lat,

    "lon": lon,

    "elevation": rasters["elevation"]["data"][rows, cols],

    "slope": rasters["slope"]["data"][rows, cols],

    "aspect": rasters["aspect"]["data"][rows, cols],

    "curvature": rasters["curvature"]["data"][rows, cols],

    "flow_accumulation":
        rasters["flow_accumulation"]["data"][rows, cols],
})


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

output_file = OUTPUT_PATH / "terrain_features.csv"

df.to_csv(output_file, index=False)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n========== TERRAIN FEATURES ==========")

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")

for column in df.columns:
    print(f" - {column}")

print("\nFirst 5 rows:")
print(df.head())

print("\nSaved to:")
print(output_file)

print("\n========== DONE ==========")