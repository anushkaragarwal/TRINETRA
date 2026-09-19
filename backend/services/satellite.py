import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# =========================
# MongoDB
# =========================

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")

CATALOGUE_URL = (
    "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
)

# =========================
# TRINETRA AOI
# =========================

MIN_LAT = 30.50
MAX_LAT = 30.80
MIN_LON = 79.40
MAX_LON = 79.75

# =========================
# FIXED DATE RANGE
# 19 August 2026 -> 19 September 2026
# =========================

START_DATE = datetime(
    2026, 8, 19, 0, 0, 0, tzinfo=timezone.utc
)

END_DATE = datetime(
    2026, 9, 19, 23, 59, 59, tzinfo=timezone.utc
)

# =========================
# HELPERS
# =========================

def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB]


def get_polygon():
    return (
        f"POLYGON(("
        f"{MIN_LON} {MIN_LAT},"
        f"{MAX_LON} {MIN_LAT},"
        f"{MAX_LON} {MAX_LAT},"
        f"{MIN_LON} {MAX_LAT},"
        f"{MIN_LON} {MIN_LAT}"
        f"))"
    )


def get_date_filter():
    start = START_DATE.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end = END_DATE.strftime("%Y-%m-%dT%H:%M:%S.999Z")

    return (
        f"ContentDate/Start ge {start} "
        f"and ContentDate/Start le {end}"
    )


def fetch_products(filter_query, top=1000):
    params = {
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$top": top,
        "$select": (
            "Id,"
            "Name,"
            "PublicationDate,"
            "ContentDate,"
            "GeoFootprint"
        ),
    }

    response = requests.get(
        CATALOGUE_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json().get("value", [])


# =========================
# SENTINEL-1
# =========================

def fetch_sentinel1():

    polygon = get_polygon()
    date_filter = get_date_filter()

    filter_query = (
        "Collection/Name eq 'SENTINEL-1' "
        "and contains(Name,'IW_GRDH') "
        f"and OData.CSC.Intersects("
        f"area=geography'SRID=4326;{polygon}') "
        f"and {date_filter}"
    )

    products = fetch_products(
        filter_query,
        top=1000
    )

    # ---------------------------------
    # Remove duplicate product variants
    # ---------------------------------
    # Copernicus may return SAFE + COG
    # for the same acquisition.
    #
    # We keep only one record per
    # acquisition start time.
    # ---------------------------------

    unique = {}

    for product in products:

        content_date = product.get("ContentDate", {})
        acquisition = content_date.get("Start")

        if acquisition:
            key = acquisition
        else:
            key = product.get("Id")

        if key not in unique:
            product["sensor"] = "Sentinel-1"
            product["collection"] = "SENTINEL-1"
            product["acquisition_date"] = acquisition

            unique[key] = product

    return list(unique.values())


# =========================
# SENTINEL-2
# =========================

def fetch_sentinel2():

    polygon = get_polygon()
    date_filter = get_date_filter()

    filter_query = (
        "Collection/Name eq 'SENTINEL-2' "
        f"and OData.CSC.Intersects("
        f"area=geography'SRID=4326;{polygon}') "
        f"and {date_filter}"
    )

    products = fetch_products(
        filter_query,
        top=1000
    )

    # ---------------------------------
    # Add Sentinel-2 metadata
    # ---------------------------------

    for product in products:

        product["sensor"] = "Sentinel-2"
        product["collection"] = "SENTINEL-2"

        content_date = product.get("ContentDate", {})

        product["acquisition_date"] = (
            content_date.get("Start")
        )

        # Try to get cloud cover
        # from product metadata if present.
        product["cloud_cover"] = None

    return products


# =========================
# REFRESH ALL SATELLITE DATA
# =========================

def refresh_satellite():

    print("\n====================================")
    print("TRINETRA SATELLITE DATA REFRESH")
    print("====================================")

    print(
        "Date range:",
        START_DATE.isoformat(),
        "->",
        END_DATE.isoformat()
    )

    # ---------------------------------
    # Fetch
    # ---------------------------------

    print("\nFetching Sentinel-1...")
    sentinel1 = fetch_sentinel1()

    print(
        "Sentinel-1 acquisitions:",
        len(sentinel1)
    )

    print("\nFetching Sentinel-2...")
    sentinel2 = fetch_sentinel2()

    print(
        "Sentinel-2 products:",
        len(sentinel2)
    )

    # ---------------------------------
    # MongoDB
    # ---------------------------------

    db = get_db()

    s1_collection = db["satellite_s1"]
    s2_collection = db["satellite_s2"]

    # Replace this fixed date-range snapshot
    s1_collection.delete_many({})
    s2_collection.delete_many({})

    # ---------------------------------
    # Insert
    # ---------------------------------

    if sentinel1:
        s1_collection.insert_many(
            sentinel1
        )

    if sentinel2:
        s2_collection.insert_many(
            sentinel2
        )

    # ---------------------------------
    # Create indexes
    # ---------------------------------

    s1_collection.create_index(
        "acquisition_date"
    )

    s2_collection.create_index(
        "acquisition_date"
    )

    print("\n====================================")
    print("SATELLITE REFRESH COMPLETE")
    print("====================================")

    print(
        "Sentinel-1:",
        len(sentinel1)
    )

    print(
        "Sentinel-2:",
        len(sentinel2)
    )

    return {
        "status": "ok",
        "date_range": {
            "start": START_DATE.isoformat(),
            "end": END_DATE.isoformat()
        },
        "sentinel1": {
            "collection": "satellite_s1",
            "records": len(sentinel1)
        },
        "sentinel2": {
            "collection": "satellite_s2",
            "records": len(sentinel2)
        }
    }


# =========================
# GET LATEST SATELLITE DATA
# =========================

def get_latest_satellite():

    db = get_db()

    s1 = list(
        db["satellite_s1"]
        .find(
            {},
            {"_id": 0}
        )
        .sort(
            "acquisition_date",
            -1
        )
    )

    s2 = list(
        db["satellite_s2"]
        .find(
            {},
            {"_id": 0}
        )
        .sort(
            "acquisition_date",
            -1
        )
    )

    # Keep existing API structure usable
    return s1 + s2


# =========================
# OPTIONAL SEPARATE GETTERS
# =========================

def get_sentinel1():

    db = get_db()

    return list(
        db["satellite_s1"]
        .find(
            {},
            {"_id": 0}
        )
        .sort(
            "acquisition_date",
            -1
        )
    )


def get_sentinel2():

    db = get_db()

    return list(
        db["satellite_s2"]
        .find(
            {},
            {"_id": 0}
        )
        .sort(
            "acquisition_date",
            -1
        )
    )