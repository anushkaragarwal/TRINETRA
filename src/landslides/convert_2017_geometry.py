import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection

INPUT = "data/features/landslides_2017_aoi.gpkg"
OUTPUT = "data/features/landslides_2017_polygons.gpkg"


print("Loading 2017 landslides...")

gdf = gpd.read_file(INPUT)

print("Input rows:", len(gdf))
print("Input CRS:", gdf.crs)

polygon_rows = []

for _, row in gdf.iterrows():

    geom = row.geometry

    if geom is None or geom.is_empty:
        continue

    parts = []

    if isinstance(geom, GeometryCollection):
        parts = list(geom.geoms)

    elif isinstance(geom, (Polygon, MultiPolygon)):
        parts = [geom]

    for part in parts:

        if isinstance(part, Polygon):
            new_row = row.drop(labels=["geometry"]).to_dict()
            new_row["geometry"] = part
            polygon_rows.append(new_row)

        elif isinstance(part, MultiPolygon):
            for polygon in part.geoms:
                new_row = row.drop(labels=["geometry"]).to_dict()
                new_row["geometry"] = polygon
                polygon_rows.append(new_row)


if not polygon_rows:
    raise ValueError("No polygon geometries found.")

out = gpd.GeoDataFrame(
    polygon_rows,
    geometry="geometry",
    crs=gdf.crs
)

out.to_file(
    OUTPUT,
    driver="GPKG"
)

print()
print("=" * 50)
print("CONVERSION COMPLETE")
print("=" * 50)
print("Input rows:", len(gdf))
print("Polygon rows:", len(out))
print("Geometry types:")
print(out.geometry.geom_type.value_counts().to_dict())
print()
print("Saved:")
print(OUTPUT)