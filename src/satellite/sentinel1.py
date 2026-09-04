import requests
from datetime import datetime, timedelta

CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Chamoli, Uttarakhand - initial monitoring area
MIN_LON = 79.0
MIN_LAT = 30.1
MAX_LON = 79.7
MAX_LAT = 30.6


def search_sentinel1(start_date, end_date, top=20):
    """
    Search Sentinel-1 IW GRDH products over our monitoring region.
    """

    footprint = (
        f"POLYGON(({MIN_LON} {MIN_LAT},"
        f"{MAX_LON} {MIN_LAT},"
        f"{MAX_LON} {MAX_LAT},"
        f"{MIN_LON} {MAX_LAT},"
        f"{MIN_LON} {MIN_LAT}))"
    )

    filter_query = (
        "Collection/Name eq 'SENTINEL-1' "
        "and Attributes/OData.CSC.StringAttribute/any("
        "att:att/Name eq 'productType' "
        "and att/OData.CSC.StringAttribute/Value eq 'IW_GRDH_1S') "
        f"and ContentDate/Start ge {start_date}T00:00:00.000Z "
        f"and ContentDate/Start le {end_date}T23:59:59.999Z "
        f"and OData.CSC.Intersects(Footprint, geography'SRID=4326;{footprint}')"
    )

    params = {
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$top": top,
        "$select": "Id,Name,ContentDate,S3Path,GeoFootprint"
    }

    response = requests.get(CATALOGUE_URL, params=params, timeout=60)
    response.raise_for_status()

    return response.json().get("value", [])


if __name__ == "__main__":

    # Search the last 40 days
    end = datetime.utcnow().date()
    start = end - timedelta(days=40)

    print("🔎 Searching Sentinel-1...")
    print(f"📍 Region: Chamoli, Uttarakhand")
    print(f"📅 Dates: {start} → {end}")
    print()

    products = search_sentinel1(
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d")
    )

    if not products:
        print("❌ No Sentinel-1 products found.")
    else:
        print(f"✅ Found {len(products)} products\n")

        for i, product in enumerate(products, 1):
            print(f"{i}. {product['Name']}")
            print(f"   ID: {product['Id']}")
            print(f"   Time: {product['ContentDate']['Start']}")
            print()