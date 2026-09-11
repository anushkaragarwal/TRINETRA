import rasterio
import numpy as np

BASE_PATH = "data/processed/dem/"

files = {
    "elevation": "data/processed/dem/dem_utm44n.tif",
    "slope": "data/processed/dem/slope_utm44n.tif",
    "aspect": "data/processed/dem/aspect_utm44n.tif",
    "curvature": "data/processed/dem/curvature_utm44n_aligned.tif",
}

rasters = {}

for name, path in files.items():

    with rasterio.open(path) as src:

        data = src.read(1, masked=True)

        rasters[name] = {
            "data": data,
            "crs": src.crs,
            "transform": src.transform,
            "width": src.width,
            "height": src.height,
            "resolution": src.res
        }

        print(f"\n{name.upper()}")
        print("-" * 30)

        print("Shape:", data.shape)
        print("CRS:", src.crs)
        print("Resolution:", src.res)

        print("Minimum:", np.nanmin(data))
        print("Maximum:", np.nanmax(data))
        print("Mean:", np.nanmean(data))


print("\n========== ALIGNMENT CHECK ==========")

reference = rasters["elevation"]

for name, raster in rasters.items():

    same_shape = (
        raster["width"] == reference["width"]
        and raster["height"] == reference["height"]
    )

    same_crs = raster["crs"] == reference["crs"]
    same_resolution = raster["resolution"] == reference["resolution"]
    same_transform = raster["transform"] == reference["transform"]

    print(f"\n{name}")
    print("Same shape:", same_shape)
    print("Same CRS:", same_crs)
    print("Same resolution:", same_resolution)
    print("Same transform:", same_transform)