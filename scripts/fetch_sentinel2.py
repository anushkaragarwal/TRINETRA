import os
import sys
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from pymongo import MongoClient


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")


# =========================================================
# COPERNICUS
# =========================================================

USERNAME = os.getenv("COPERNICUS_USERNAME")
PASSWORD = os.getenv("COPERNICUS_PASSWORD")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

CATALOGUE_URL = (
    "https://catalogue.dataspace.copernicus.eu/"
    "odata/v1/Products"
)


# =========================================================
# MONGODB
# =========================================================

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")

MONGO_COLLECTION = "sentinel2_metadata"


# =========================================================
# ANALYSIS WINDOW
# =========================================================

START_DATE = "2026-08-19T00:00:00.000Z"
END_DATE = "2026-09-19T23:59:59.999Z"


# =========================================================
# TRINETRA AOI
# =========================================================

AOI = (
    "POLYGON(("
    "79.40 30.50,"
    "79.75 30.50,"
    "79.75 30.80,"
    "79.40 30.80,"
    "79.40 30.50"
    "))"
)


# =========================================================
# SETTINGS
# =========================================================

MAX_CLOUD_COVER = 80.0

PRODUCT_TYPE = "S2MSI2A"

TOP = 100


# =========================================================
# COPERNICUS TOKEN
# =========================================================

def get_access_token():

    if not USERNAME or not PASSWORD:
        raise ValueError(
            "COPERNICUS_USERNAME or "
            "COPERNICUS_PASSWORD missing in .env"
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": "cdse-public",
            "username": USERNAME,
            "password": PASSWORD,
            "grant_type": "password",
        },
        timeout=60,
    )

    response.raise_for_status()

    token = response.json().get("access_token")

    if not token:
        raise RuntimeError(
            "Copernicus access token missing."
        )

    return token


# =========================================================
# MONGODB
# =========================================================

def get_mongo_collection():

    if not MONGODB_URI:
        raise ValueError(
            "MONGODB_URI missing in .env"
        )

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    )

    client.admin.command("ping")

    collection = client[
        MONGODB_DB
    ][
        MONGO_COLLECTION
    ]

    return client, collection


# =========================================================
# BUILD QUERY
# =========================================================

def build_query():

    query = (
        "Collection/Name eq 'SENTINEL-2' "

        "and "
        "Attributes/"
        "OData.CSC.StringAttribute/"
        "any("
        "att:att/Name eq 'productType' "
        "and "
        "att/OData.CSC.StringAttribute/Value "
        f"eq '{PRODUCT_TYPE}'"
        ") "

        "and "
        "OData.CSC.Intersects("
        "area=geography"
        f"'SRID=4326;{AOI}'"
        ") "

        "and "
        "ContentDate/Start gt "
        f"{START_DATE} "

        "and "
        "ContentDate/Start lt "
        f"{END_DATE}"
    )

    return {
        "$filter": query,
        "$orderby": "ContentDate/Start asc",
        "$top": TOP,
        "$expand": "Attributes",
    }


# =========================================================
# FETCH PRODUCTS
# =========================================================

def fetch_products():

    print(
        "\n📡 Searching Copernicus "
        "Sentinel-2 catalogue..."
    )

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        CATALOGUE_URL,
        headers=headers,
        params=build_query(),
        timeout=120,
    )

    response.raise_for_status()

    return response.json().get(
        "value",
        []
    )


# =========================================================
# EXTRACT ATTRIBUTE
# =========================================================

def get_attribute_value(
    product,
    attribute_name,
):

    attributes = product.get(
        "Attributes",
        []
    )

    for attribute in attributes:

        if attribute.get("Name") == attribute_name:

            return attribute.get(
                "Value"
            )

    return None


# =========================================================
# PARSE DATE
# =========================================================

def parse_datetime(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except Exception:
        return None


# =========================================================
# CREATE MONGO DOCUMENT
# =========================================================

def make_document(product):

    content_date = product.get(
        "ContentDate",
        {}
    )

    acquisition_time = (
        content_date.get("Start")
    )

    completion_time = (
        content_date.get("End")
    )

    acquisition_dt = parse_datetime(
        acquisition_time
    )

    # ---------------------------------------------
    # BEFORE / AFTER
    # ---------------------------------------------

    analysis_period = None

    if acquisition_dt:

        cutoff = datetime(
            2026,
            9,
            1,
            tzinfo=timezone.utc,
        )

        analysis_period = (
            "BEFORE"
            if acquisition_dt < cutoff
            else "AFTER"
        )

    cloud_cover = get_attribute_value(
        product,
        "cloudCover"
    )

    # ---------------------------------------------
    # MongoDB document
    # ---------------------------------------------

    return {
        "source":
            "Copernicus Data Space",

        "satellite":
            "Sentinel-2",

        "product_id":
            product.get("Id"),

        "product_name":
            product.get("Name"),

        "product_type":
            PRODUCT_TYPE,

        "collection":
            "SENTINEL-2",

        "acquisition_time_utc":
            acquisition_time,

        "completion_time_utc":
            completion_time,

        "cloud_cover":
            cloud_cover,

        "s3_path":
            product.get("S3Path"),

        "geo_footprint":
            product.get("GeoFootprint"),

        "online":
            product.get("Online"),

        "analysis_period":
            analysis_period,

        "analysis_window": {
            "start": START_DATE,
            "end": END_DATE,
        },

        "aoi":
            AOI,

        "created_at":
            datetime.now(timezone.utc),
    }


# =========================================================
# SAVE TO MONGODB
# =========================================================

def save_to_mongodb(documents):

    client, collection = (
        get_mongo_collection()
    )

    try:

        inserted = 0
        updated = 0

        for document in documents:

            product_id = document.get(
                "product_id"
            )

            if not product_id:
                continue

            result = collection.update_one(
                {
                    "product_id":
                        product_id
                },
                {
                    "$set":
                        document
                },
                upsert=True,
            )

            if result.upserted_id:
                inserted += 1
            else:
                updated += 1

        collection.create_index(
            "product_id",
            unique=True,
        )

        collection.create_index(
            "acquisition_time_utc"
        )

        collection.create_index(
            "analysis_period"
        )

        print(
            "\n💾 MongoDB save completed."
        )

        print(
            f"New products : {inserted}"
        )

        print(
            f"Updated       : {updated}"
        )

        print(
            f"Collection    : {MONGO_COLLECTION}"
        )

    finally:

        client.close()


# =========================================================
# UNIQUE ACQUISITION SCENES
# =========================================================

def get_unique_acquisitions(
    documents
):

    unique = {}

    for document in documents:

        time = document.get(
            "acquisition_time_utc"
        )

        if not time:
            continue

        # Same timestamp = same acquisition,
        # even if multiple tiles exist.

        key = time

        if key not in unique:

            unique[key] = document

    return list(
        unique.values()
    )


# =========================================================
# SUMMARY
# =========================================================

def print_summary(documents):

    unique = get_unique_acquisitions(
        documents
    )

    before = [
        d for d in unique
        if d["analysis_period"]
        == "BEFORE"
    ]

    after = [
        d for d in unique
        if d["analysis_period"]
        == "AFTER"
    ]

    print(
        "\n" + "=" * 70
    )

    print(
        "🛰️ SENTINEL-2 SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"\nProducts/tiles found : "
        f"{len(documents)}"
    )

    print(
        f"Unique acquisitions  : "
        f"{len(unique)}"
    )

    print(
        f"BEFORE acquisitions  : "
        f"{len(before)}"
    )

    print(
        f"AFTER acquisitions   : "
        f"{len(after)}"
    )

    for document in documents:

        print(
            "\n----------------------------------------"
        )

        print(
            f"Product : "
            f"{document['product_name']}"
        )

        print(
            f"Time    : "
            f"{document['acquisition_time_utc']}"
        )

        print(
            f"Cloud   : "
            f"{document['cloud_cover']}"
        )

        print(
            f"Period  : "
            f"{document['analysis_period']}"
        )

    print(
        "\n" + "=" * 70
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n🚀 TRINETRA Sentinel-2 pipeline"
    )

    print(
        "19 Aug 2026 → 19 Sep 2026"
    )

    try:

        products = fetch_products()

        if not products:

            print(
                "\n⚠️ No Sentinel-2 products found."
            )

            return

        documents = [
            make_document(product)
            for product in products
        ]

        print_summary(
            documents
        )

        save_to_mongodb(
            documents
        )

        print(
            "\n✅ Sentinel-2 metadata "
            "pipeline completed."
        )

        print(
            "\n📦 MongoDB:"
        )

        print(
            "sentinel2_metadata"
        )

        print(
            "\nNext step:"
        )

        print(
            "S2 bands → MNDWI → "
            "water-area change."
        )

    except Exception as error:

        print(
            "\n❌ Pipeline failed:"
        )

        print(
            str(error)
        )

        sys.exit(1)


if __name__ == "__main__":
    main()