from pathlib import Path
from datetime import datetime, timezone
import os
import sys

import numpy as np
import requests
import rasterio
from dotenv import load_dotenv
from pymongo import MongoClient


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

OUTPUT_DIR = (
    ROOT
    / "data"
    / "satellite"
    / "raw"
    / "sentinel2"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# COPERNICUS
# =========================================================

USERNAME = os.getenv(
    "COPERNICUS_USERNAME"
)

PASSWORD = os.getenv(
    "COPERNICUS_PASSWORD"
)

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

DOWNLOAD_BASE = (
    "https://download.dataspace.copernicus.eu"
)


# =========================================================
# MONGODB
# =========================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI"
)

MONGODB_DB = os.getenv(
    "MONGODB_DB",
    "trinetra"
)


# =========================================================
# TRINETRA AOI
# =========================================================

AOI_MIN_LON = 79.40
AOI_MAX_LON = 79.75
AOI_MIN_LAT = 30.50
AOI_MAX_LAT = 30.80


# =========================================================
# AUTHENTICATION
# =========================================================

def get_access_token():

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

    token = response.json().get(
        "access_token"
    )

    if not token:
        raise RuntimeError(
            "Copernicus access token not returned."
        )

    return token


# =========================================================
# MONGODB
# =========================================================

def get_collection():

    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
    )

    client.admin.command("ping")

    collection = client[
        MONGODB_DB
    ][
        "sentinel2_metadata"
    ]

    return client, collection


# =========================================================
# DOWNLOAD NODE
# =========================================================

def download_node(
    session,
    product_id,
    node_path,
    output_path,
):
    """
    Download a single file from a CDSE OData product node.

    The node path is split component-by-component because
    CDSE expects nested Nodes(...) calls.
    """

    base_url = (
        "https://download.dataspace.copernicus.eu"
        f"/odata/v1/Products({product_id})"
    )

    parts = [
        part
        for part in node_path.split("/")
        if part
    ]

    if not parts:
        raise ValueError(
            "Empty Sentinel-2 node path."
        )

    url = base_url

    # Build:
    # Products(ID)/Nodes(folder)/Nodes(folder)/...
    #
    # The final component is the actual JP2 file.
    for part in parts:
        url += f"/Nodes({part})"

    # $value must be requested from the final node.
    url += "/$value"

    print(
        "\n⬇️ Downloading:"
    )

    print(
        f"   {node_path}"
    )

    response = session.get(
        url,
        stream=True,
        timeout=600,
    )

    if response.status_code != 200:

        print(
            "\n❌ CDSE download failed"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "URL:",
            url
        )

        print(
            "Response:",
            response.text[:1000]
        )

    response.raise_for_status()

    with open(
        output_path,
        "wb"
    ) as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                file.write(chunk)

    print(
        f"   ✅ Saved: "
        f"{output_path.name}"
    )

    return output_path

    url = (
        f"{DOWNLOAD_BASE}/odata/v1/"
        f"Products({product_id})/"
        f"Nodes({node_path})/$value"
    )

    print(
        f"\n⬇️ Downloading:"
    )

    print(
        f"   {node_path}"
    )

    response = session.get(
        url,
        stream=True,
        timeout=300,
    )

    response.raise_for_status()

    with open(
        output_path,
        "wb"
    ) as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                file.write(chunk)

    print(
        f"   Saved: {output_path.name}"
    )

    return output_path


# =========================================================
# GET PRODUCT NODES
# =========================================================

def get_nodes(
    session,
    product_id,
    node_path=None,
):
    """
    List children of a Sentinel-2 product/folder.

    CDSE OData requires each path component to be passed
    through a separate Nodes(...) level.
    """

    base_url = (
        f"https://download.dataspace.copernicus.eu"
        f"/odata/v1/Products({product_id})"
    )

    if node_path:
        parts = [
            part
            for part in node_path.split("/")
            if part
        ]

        url = base_url

        for part in parts:
            url += f"/Nodes({part})"

        url += "/Nodes"

    else:
        url = (
            base_url
            + "/Nodes"
        )

    response = session.get(
        url,
        timeout=120,
    )

    if response.status_code != 200:

        print(
            "\n❌ CDSE node request failed"
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "URL:",
            url
        )

        print(
            "Response:",
            response.text[:1000]
        )

    response.raise_for_status()

    return response.json().get(
        "result",
        []
    )

    if node_path:

        url = (
            f"{DOWNLOAD_BASE}/odata/v1/"
            f"Products({product_id})/"
            f"Nodes({node_path})/Nodes"
        )

    else:

        url = (
            f"{DOWNLOAD_BASE}/odata/v1/"
            f"Products({product_id})/Nodes"
        )

    response = session.get(
        url,
        timeout=120,
    )

    response.raise_for_status()

    return response.json().get(
        "result",
        []
    )


# =========================================================
# FIND REQUIRED FILES
# =========================================================

def find_band_nodes(
    session,
    product_id,
):
    """
    Recursively search the Sentinel-2 product tree
    for B03, B11 and SCL JP2 files.
    """

    found = {}

    def walk(
        current_path=None
    ):

        nodes = get_nodes(
            session,
            product_id,
            current_path,
        )

        for node in nodes:

            name = node.get(
                "Name",
                ""
            )

            if not name:
                continue

            if current_path:
                path = (
                    f"{current_path}/{name}"
                )
            else:
                path = name

            lower = name.lower()

            # ---------------------------------------------
            # B03 = Green
            # ---------------------------------------------

            if (
                "_b03_20m.jp2"
                in lower
            ):
                found["B03"] = path

                print(
                    "✅ Found B03:",
                    path
                )

            # ---------------------------------------------
            # B11 = SWIR
            # ---------------------------------------------

            if (
                "_b11_20m.jp2"
                in lower
            ):
                found["B11"] = path

                print(
                    "✅ Found B11:",
                    path
                )

            # ---------------------------------------------
            # SCL = Scene Classification Layer
            # ---------------------------------------------

            if (
                "_scl_20m.jp2"
                in lower
            ):
                found["SCL"] = path

                print(
                    "✅ Found SCL:",
                    path
                )

            # ---------------------------------------------
            # Folder
            # ---------------------------------------------

            children = node.get(
                "ChildrenNumber",
                0
            )

            if children and children > 0:

                walk(path)

            # ---------------------------------------------
            # Stop once required bands found
            # ---------------------------------------------

            if (
                "B03" in found
                and
                "B11" in found
                and
                "SCL" in found
            ):
                return

    walk()

    return found

    found = {}

    def walk(
        current_path=None
    ):

        nodes = get_nodes(
            session,
            product_id,
            current_path,
        )

        for node in nodes:

            name = node.get(
                "Name",
                ""
            )

            if current_path:

                path = (
                    f"{current_path}/{name}"
                )

            else:

                path = name


            lower = name.lower()


            # ---------------------------------------------
            # Sentinel-2 Green band
            # ---------------------------------------------

            if (
                "_b03_20m.jp2"
                in lower
            ):

                found["B03"] = path


            # ---------------------------------------------
            # Sentinel-2 SWIR band
            # ---------------------------------------------

            if (
                "_b11_20m.jp2"
                in lower
            ):

                found["B11"] = path


            # ---------------------------------------------
            # Scene Classification Layer
            # ---------------------------------------------

            if (
                "_scl_20m.jp2"
                in lower
            ):

                found["SCL"] = path


            # ---------------------------------------------
            # Folder → recurse
            # ---------------------------------------------

            if node.get(
                "ChildrenNumber",
                0
            ) > 0:

                walk(path)


    walk()

    return found


# =========================================================
# SELECT BEST BEFORE / AFTER
# =========================================================

def select_products(
    collection
):

    documents = list(
        collection.find({
            "satellite": "Sentinel-2"
        })
    )

    if not documents:

        raise RuntimeError(
            "No Sentinel-2 records found in MongoDB."
        )


    # ---------------------------------------------
    # Parse dates
    # ---------------------------------------------

    for document in documents:

        value = document.get(
            "acquisition_time_utc"
        )

        if isinstance(
            value,
            str
        ):

            document[
                "_time"
            ] = datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00"
                )
            )

        else:

            document[
                "_time"
            ] = value


    # ---------------------------------------------
    # Remove duplicate tiles/products by
    # acquisition timestamp.
    # ---------------------------------------------

    unique = {}

    for document in documents:

        timestamp = document[
            "_time"
        ]

        if timestamp not in unique:

            unique[timestamp] = document

        else:

            # Keep the lower-cloud product
            # as representative metadata.

            old_cloud = (
                unique[timestamp]
                .get("cloud_cover")
            )

            new_cloud = (
                document
                .get("cloud_cover")
            )

            if (
                new_cloud is not None
                and
                (
                    old_cloud is None
                    or
                    new_cloud < old_cloud
                )
            ):

                unique[timestamp] = document


    acquisitions = list(
        unique.values()
    )


    cutoff = datetime(
        2026,
        9,
        1,
        tzinfo=timezone.utc,
    )


    before = [
        x for x in acquisitions
        if x["_time"] < cutoff
    ]

    after = [
        x for x in acquisitions
        if x["_time"] >= cutoff
    ]


    if not before:
        raise RuntimeError(
            "No BEFORE Sentinel-2 acquisition."
        )

    if not after:
        raise RuntimeError(
            "No AFTER Sentinel-2 acquisition."
        )


    # Best cloud-cover acquisition
    # on each side.

    before = sorted(
        before,
        key=lambda x:
        (
            x.get("cloud_cover")
            if x.get("cloud_cover")
            is not None
            else 999
        )
    )

    after = sorted(
        after,
        key=lambda x:
        (
            x.get("cloud_cover")
            if x.get("cloud_cover")
            is not None
            else 999
        )
    )


    return before[0], after[0]


# =========================================================
# MNDWI
# =========================================================

def calculate_mndwi(
    green_path,
    swir_path,
    scl_path=None,
):

    print(
        "\n🧮 Calculating MNDWI..."
    )

    with rasterio.open(
        green_path
    ) as green_src:

        green = (
            green_src
            .read(1)
            .astype(np.float32)
        )

        profile = (
            green_src.profile.copy()
        )

        transform = (
            green_src.transform
        )

        pixel_width = abs(
            transform.a
        )

        pixel_height = abs(
            transform.e
        )


    with rasterio.open(
        swir_path
    ) as swir_src:

        swir = (
            swir_src
            .read(1)
            .astype(np.float32)
        )


    # Sentinel-2 reflectance scaling
    green /= 10000.0
    swir /= 10000.0


    denominator = (
        green + swir
    )


    mndwi = np.where(
        denominator != 0,
        (
            green - swir
        ) / denominator,
        np.nan,
    )


    # -----------------------------------------------------
    # Basic valid-pixel mask
    # -----------------------------------------------------

    valid = (
        np.isfinite(mndwi)
        &
        (green > 0)
        &
        (swir > 0)
    )


    # -----------------------------------------------------
    # Optional SCL cloud masking
    # -----------------------------------------------------

    if scl_path:

        with rasterio.open(
            scl_path
        ) as scl_src:

            scl = (
                scl_src
                .read(1)
            )

        # SCL classes to reject:
        #
        # 3  = cloud shadow
        # 8  = medium probability cloud
        # 9  = high probability cloud
        # 10 = cirrus
        # 11 = snow/ice

        invalid_scl = np.isin(
            scl,
            [
                3,
                8,
                9,
                10,
                11,
            ]
        )

        valid &= ~invalid_scl


    water = (
        mndwi > 0.0
    ) & valid


    pixel_area_m2 = (
        pixel_width
        * pixel_height
    )


    water_pixels = int(
        np.count_nonzero(
            water
        )
    )


    valid_pixels = int(
        np.count_nonzero(
            valid
        )
    )


    water_area_ha = (
        water_pixels
        * pixel_area_m2
        / 10000.0
    )


    return (
        mndwi,
        valid,
        water,
        water_area_ha,
        valid_pixels,
    )


# =========================================================
# MAIN PROCESSING
# =========================================================

def main():

    print(
        "\n🚀 TRINETRA Sentinel-2 "
        "ACTUAL DATA PROCESSING"
    )

    print(
        "19 Aug 2026 → 19 Sep 2026"
    )


    # -----------------------------------------------------
    # MongoDB
    # -----------------------------------------------------

    client, collection = (
        get_collection()
    )


    try:

        before, after = (
            select_products(
                collection
            )
        )


        print(
            "\n⭐ SELECTED S2 ACQUISITIONS"
        )

        print(
            "\nBEFORE"
        )

        print(
            before["product_name"]
        )

        print(
            "Time:",
            before["_time"]
        )

        print(
            "Cloud:",
            before.get(
                "cloud_cover"
            )
        )


        print(
            "\nAFTER"
        )

        print(
            after["product_name"]
        )

        print(
            "Time:",
            after["_time"]
        )

        print(
            "Cloud:",
            after.get(
                "cloud_cover"
            )
        )


        # -------------------------------------------------
        # Authentication
        # -------------------------------------------------

        token = get_access_token()

        session = requests.Session()

        session.headers.update({
            "Authorization":
                f"Bearer {token}"
        })


        # -------------------------------------------------
        # Process BEFORE and AFTER
        # -------------------------------------------------

        results = {}


        for label, document in [
            ("before", before),
            ("after", after),
        ]:

            print(
                "\n" + "=" * 70
            )

            print(
                f"📡 PROCESSING {label.upper()}"
            )

            print(
                "=" * 70
            )


            product_id = document[
                "product_id"
            ]


            print(
                "\nProduct ID:"
            )

            print(
                product_id
            )


            print(
                "\n🔎 Finding bands..."
            )


            bands = find_band_nodes(
                session,
                product_id,
            )


            print(
                "\nFound:"
            )

            for key, value in bands.items():

                print(
                    f"{key}: {value}"
                )


            required = [
                "B03",
                "B11",
            ]


            for band in required:

                if band not in bands:

                    raise RuntimeError(
                        f"{band} not found "
                        "inside Sentinel-2 product."
                    )


            local_files = {}


            for band in [
                "B03",
                "B11",
                "SCL",
            ]:

                if band not in bands:
                    continue


                filename = (
                    f"{label}_{band}.jp2"
                )


                output_path = (
                    OUTPUT_DIR
                    / filename
                )


                if output_path.exists():

                    print(
                        f"\n♻️ Already downloaded:"
                        f" {filename}"
                    )

                else:

                    download_node(
                        session,
                        product_id,
                        bands[band],
                        output_path,
                    )


                local_files[
                    band
                ] = output_path


            # -------------------------------------------------
            # MNDWI
            # -------------------------------------------------

            (
                mndwi,
                valid,
                water,
                water_area_ha,
                valid_pixels,
            ) = calculate_mndwi(
                local_files["B03"],
                local_files["B11"],
                local_files.get("SCL"),
            )


            results[
                label
            ] = {
                "water_area_ha":
                    water_area_ha,

                "valid_pixels":
                    valid_pixels,

                "water_mask":
                    water,
            }


            print(
                "\n💧 Water area:"
            )

            print(
                f"{water_area_ha:.4f} ha"
            )


        # =================================================
        # CHANGE METRICS
        # =================================================

        before_water = (
            results["before"]
            ["water_area_ha"]
        )

        after_water = (
            results["after"]
            ["water_area_ha"]
        )


        net_change = (
            after_water
            - before_water
        )


        # Conservative candidate-new-water
        # estimate based on total positive
        # area change.

        candidate_new_water = max(
            net_change,
            0.0
        )


        print(
            "\n" + "=" * 70
        )

        print(
            "🌊 SENTINEL-2 WATER CHANGE"
        )

        print(
            "=" * 70
        )

        print(
            f"\nBefore water area : "
            f"{before_water:.4f} ha"
        )

        print(
            f"After water area  : "
            f"{after_water:.4f} ha"
        )

        print(
            f"Net water change  : "
            f"{net_change:.4f} ha"
        )

        print(
            f"Candidate new water : "
            f"{candidate_new_water:.4f} ha"
        )


        # =================================================
        # SAVE METRICS TO MONGODB
        # =================================================

        metrics = {

            "analysis_window": {
                "start":
                    "2026-08-19T00:00:00Z",

                "end":
                    "2026-09-19T23:59:59Z",
            },

            "satellite":
                "Sentinel-2",

            "before": {
                "product_id":
                    before["product_id"],

                "product_name":
                    before["product_name"],

                "acquisition_time_utc":
                    before["_time"],

                "water_area_ha":
                    before_water,
            },

            "after": {
                "product_id":
                    after["product_id"],

                "product_name":
                    after["product_name"],

                "acquisition_time_utc":
                    after["_time"],

                "water_area_ha":
                    after_water,
            },

            "sentinel2_candidate_new_water_ha":
                candidate_new_water,

            "sentinel2_net_water_change_ha":
                net_change,

            "updated_at":
                datetime.now(
                    timezone.utc
                ),
        }


        collection.update_one(
            {
                "document_type":
                    "derived_metrics",

                "analysis_start":
                    "2026-08-19",
            },

            {
                "$set":
                    metrics
            },

            upsert=True,
        )


        print(
            "\n💾 Metrics saved to MongoDB."
        )

        print(
            "Collection: sentinel2_metadata"
        )


        print(
            "\n✅ Sentinel-2 actual "
            "processing completed."
        )


    finally:

        client.close()


if __name__ == "__main__":
    main()