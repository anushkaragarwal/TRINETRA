import os
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")

CATALOGUE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Chamoli MVP AOI
MIN_LAT = 30.50
MAX_LAT = 30.80
MIN_LON = 79.40
MAX_LON = 79.75


def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB]


def refresh_satellite():

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)

    polygon = (
        f"POLYGON(({MIN_LON} {MIN_LAT},"
        f"{MAX_LON} {MIN_LAT},"
        f"{MAX_LON} {MAX_LAT},"
        f"{MIN_LON} {MAX_LAT},"
        f"{MIN_LON} {MIN_LAT}))"
    )

    start = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    filter_query = (
        "Collection/Name eq 'SENTINEL-1' "
        "and contains(Name,'IW_GRDH') "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{polygon}') "
        f"and ContentDate/Start ge {start} "
        f"and ContentDate/Start le {end}"
    )

    params = {
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$top": 50,
        "$select": "Id,Name,ContentDate,PublicationDate,GeoFootprint"
    }

    response = requests.get(
        CATALOGUE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    products = data.get("value", [])

    db = get_db()
    collection = db["satellite_products"]

    collection.delete_many({})

    if products:
        collection.insert_many(products)

    return {
        "status": "ok",
        "source": "Copernicus Sentinel-1 OData",
        "collection": "satellite_products",
        "records": len(products)
    }


def get_latest_satellite():

    db = get_db()

    return list(
        db["satellite_products"]
        .find({}, {"_id": 0})
        .sort("ContentDate.Start", -1)
        .limit(20)
    )