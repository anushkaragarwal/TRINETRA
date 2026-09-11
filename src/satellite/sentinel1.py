from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

try:
    from .config import (
        CATALOGUE_URL,
        REGION_NAME,
        AOI,
        SEARCH_DAYS,
        MAX_PRODUCTS,
    )
except ImportError:
    from config import (
        CATALOGUE_URL,
        REGION_NAME,
        AOI,
        SEARCH_DAYS,
        MAX_PRODUCTS,
    )


ROOT = Path(__file__).resolve().parents[2]

OUTPUT_PATH = (
    ROOT
    / "data"
    / "satellite"
    / "sentinel1_metadata.csv"
)


def search_sentinel1():
    """
    Search and clean Sentinel-1 IW GRD product metadata for
    the configured TRINETRA monitoring corridor.

    This script searches metadata only; it does not download
    satellite image products.
    """

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=SEARCH_DAYS)

    start_str = start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    print("🔎 Searching Sentinel-1 SAR product metadata...")
    print(f"📍 Region: {REGION_NAME}")
    print(f"📅 Dates: {start_str[:10]} → {end_str[:10]}")

    query = (
        "Collection/Name eq 'SENTINEL-1' "
        "and Attributes/OData.CSC.StringAttribute/any("
        "att:att/Name eq 'productType' "
        "and att/OData.CSC.StringAttribute/Value eq 'IW_GRDH_1S'"
        ") "
        "and OData.CSC.Intersects("
        f"area=geography'SRID=4326;{AOI}'"
        ") "
        f"and ContentDate/Start ge {start_str} "
        f"and ContentDate/Start le {end_str}"
    )

    params = {
        "$filter": query,
        "$orderby": "ContentDate/Start desc",
        "$top": MAX_PRODUCTS,
        "$select": (
            "Id,Name,ContentDate,S3Path,GeoFootprint"
        ),
    }

    try:
        response = requests.get(
            CATALOGUE_URL,
            params=params,
            timeout=(10, 120),
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        print("\n❌ Sentinel-1 request timed out.")
        print("Please retry after a few seconds.")
        return pd.DataFrame()

    except requests.exceptions.RequestException as error:
        print("\n❌ Network/API error while searching Sentinel-1:")
        print(error)
        return pd.DataFrame()

    products = response.json().get("value", [])

    if not products:
        print("\n⚠️ No Sentinel-1 products found.")
        return pd.DataFrame()

    rows = []

    for product in products:
        content_date = product.get("ContentDate", {})

        rows.append({
            "product_id": product.get("Id"),
            "product_name": product.get("Name"),
            "acquisition_time_utc": content_date.get("Start"),
            "completion_time_utc": content_date.get("End"),
            "s3_path": product.get("S3Path"),
            "geo_footprint": product.get("GeoFootprint"),
            "collection": "SENTINEL-1",
            "product_type": "IW_GRDH_1S",
            "region_name": REGION_NAME,
            "search_timestamp_utc": (
                datetime.now(timezone.utc)
                .strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
        })

    df = pd.DataFrame(rows)

    # ----------------------------
    # CLEANING
    # ----------------------------

    # Convert timestamp columns to valid UTC datetime values.
    df["acquisition_time_utc"] = pd.to_datetime(
        df["acquisition_time_utc"],
        errors="coerce",
        utc=True,
    )

    df["completion_time_utc"] = pd.to_datetime(
        df["completion_time_utc"],
        errors="coerce",
        utc=True,
    )

    # Remove unusable / duplicate scene metadata.
    df = df.dropna(
        subset=[
            "product_id",
            "product_name",
            "acquisition_time_utc",
        ]
    )

    df = df.drop_duplicates(
        subset=["product_id"]
    )

    # Add fields that help scene-pair selection later.
    df["acquisition_date"] = (
        df["acquisition_time_utc"]
        .dt.date
    )

    df["acquisition_hour_utc"] = (
        df["acquisition_time_utc"]
        .dt.hour
    )

    # Oldest → newest is easier for before/after pairing.
    df = df.sort_values(
        by="acquisition_time_utc",
        ascending=True,
    ).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"\n✅ Clean Sentinel-1 scenes saved: {len(df)}")

    print("\n📋 Scene summary:")
    print(
        df[
            [
                "product_name",
                "acquisition_time_utc",
                "acquisition_date",
                "product_type",
            ]
        ]
        .tail(10)
        .to_string(index=False)
    )

    print(
        f"\n💾 Saved clean Sentinel-1 metadata to:\n"
        f"{OUTPUT_PATH}"
    )

    return df


if __name__ == "__main__":
    search_sentinel1()