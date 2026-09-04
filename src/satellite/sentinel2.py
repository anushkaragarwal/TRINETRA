import requests
from datetime import datetime, timedelta, timezone

from config import (
    CATALOGUE_URL,
    REGION_NAME,
    AOI,
    MAX_CLOUD_COVER,
    SEARCH_DAYS,
    MAX_PRODUCTS,
)
from dotenv import load_dotenv

load_dotenv()

CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Our selected TRINETRA region
AOI = (
    "POLYGON(("
    "78.60 30.95,"
    "78.85 30.95,"
    "78.85 31.20,"
    "78.60 31.20,"
    "78.60 30.95"
    "))"
)


def search_sentinel2():

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=SEARCH_DAYS)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    print("🔎 Searching Sentinel-2...")
    print(f"📍 Region: {REGION_NAME}")
    print(f"📅 Dates: {start_str[:10]} → {end_str[:10]}")

    query = (
        f"Collection/Name eq 'SENTINEL-2' "
        f"and Attributes/OData.CSC.StringAttribute/any("
        f"att:att/Name eq 'productType' "
        f"and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A'"
        f") "
        f"and Attributes/OData.CSC.DoubleAttribute/any("
        f"att:att/Name eq 'cloudCover' "
        f"and att/OData.CSC.DoubleAttribute/Value le {MAX_CLOUD_COVER}"
        f") "
        f"and OData.CSC.Intersects("
        f"area=geography'SRID=4326;{AOI}'"
        f") "
        f"and ContentDate/Start ge {start_str} "
        f"and ContentDate/Start le {end_str}"
    )

    params = {
        "$filter": query,
        "$orderby": "ContentDate/Start desc",
        "$top": MAX_PRODUCTS,
        "$select": "Id,Name,ContentDate,GeoFootprint",
    }

    try:
       response = requests.get(
        CATALOGUE_URL,
        params=params,
        timeout=(10, 120)
      )

    except requests.exceptions.Timeout:
        print("\n❌ Copernicus request timed out.")
        print("The catalogue is taking too long to respond.")
        print("Please run the command again in a few seconds.")
        return

    except requests.exceptions.RequestException as e:
        print("\n❌ Network error while contacting Copernicus:")
        print(e)
        return 

    if not response.ok:
        print("\n❌ Copernicus API Error")
        print(response.status_code)
        print(response.text)
        return

    data = response.json()
    products = data.get("value", [])

    print(f"\n✅ Found {len(products)} Sentinel-2 products\n")

    for i, product in enumerate(products, 1):
        print(f"{i}. {product['Name']}")
        print(f"   ID: {product['Id']}")
        print(f"   Time: {product['ContentDate']['Start']}")
        print()


if __name__ == "__main__":
    search_sentinel2()