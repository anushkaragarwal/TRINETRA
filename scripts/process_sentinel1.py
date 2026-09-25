import os
import re
import requests
import numpy as np
import rasterio
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB", "trinetra")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

DOWNLOAD_BASE = "https://download.dataspace.copernicus.eu/odata/v1"

START = datetime(2026, 8, 19, tzinfo=timezone.utc)
END = datetime(2026, 9, 19, 23, 59, 59, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 9, 1, tzinfo=timezone.utc)


def get_token():
    username = os.getenv("COPERNICUS_USERNAME")
    password = os.getenv("COPERNICUS_PASSWORD")

    r = requests.post(
        TOKEN_URL,
        data={
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def get_db():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB]


def parse_time(doc):
    t = doc.get("acquisition_time_utc") or doc.get("_time")

    if isinstance(t, datetime):
        return t

    if isinstance(t, str):
        t = t.replace("Z", "+00:00")
        return datetime.fromisoformat(t)

    return None


def select_scenes(collection):
    docs = list(collection.find({}))

    scenes = []

    for d in docs:
        t = parse_time(d)

        if not t:
            continue

        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)

        if START <= t <= END:
            scenes.append((t, d))

    scenes.sort(key=lambda x: x[0])

    before = [x for x in scenes if x[0] < CUTOFF]
    after = [x for x in scenes if x[0] >= CUTOFF]

    if not before:
        raise RuntimeError("No Sentinel-1 BEFORE scenes found")

    if not after:
        raise RuntimeError("No Sentinel-1 AFTER scenes found")

    # Use latest scene before cutoff and earliest after cutoff
    before_scene = before[-1][1]
    after_scene = after[0][1]

    return before_scene, after_scene, len(before), len(after)


def get_nodes(session, product_id, node_path=None):
    url = f"{DOWNLOAD_BASE}/Products({product_id})"

    if node_path:
        parts = [p for p in node_path.split("/") if p]

        for part in parts:
            url += f"/Nodes({part})"

    url += "/Nodes"

    r = session.get(url, timeout=120)
    r.raise_for_status()

    return r.json().get("result", [])


def find_vv_node(session, product_id):
    found = []

    def walk(path=""):
        nodes = get_nodes(session, product_id, path)

        for node in nodes:
            name = node.get("Name", "")
            full_path = f"{path}/{name}" if path else name

            children = node.get("ChildrenNumber", 0)

            lower = name.lower()

            # Sentinel-1 GRD VV measurement
            if (
                children == 0
                and (
                    "vv" in lower
                    or re.search(r"[-_]vv[-_.]", lower)
                )
                and lower.endswith((".tiff", ".tif"))
            ):
                found.append(full_path)

            if children and children > 0:
                walk(full_path)

    walk()

    if not found:
        raise RuntimeError("Could not find Sentinel-1 VV TIFF")

    # Prefer measurement VV file
    found.sort(
        key=lambda x: (
            "measurement" not in x.lower(),
            "vv" not in x.lower(),
            len(x),
        )
    )

    return found[0]


def download_node(session, product_id, node_path, output_path):
    parts = [p for p in node_path.split("/") if p]

    url = f"{DOWNLOAD_BASE}/Products({product_id})"

    for part in parts:
        url += f"/Nodes({part})"

    url += "/$value"

    print("\n⬇️ Downloading:")
    print(node_path)

    r = session.get(
        url,
        stream=True,
        timeout=600,
        allow_redirects=True,
    )

    r.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    print(f"✅ Saved: {output_path}")


def calculate_change(before_file, after_file):
    print("\n🧮 Calculating Sentinel-1 VV change...")

    with rasterio.open(before_file) as src1:
        before = src1.read(1).astype("float32")
        profile = src1.profile

    with rasterio.open(after_file) as src2:
        after = src2.read(1).astype("float32")

    # Make arrays compatible
    h = min(before.shape[0], after.shape[0])
    w = min(before.shape[1], after.shape[1])

    before = before[:h, :w]
    after = after[:h, :w]

    valid = (
        np.isfinite(before)
        & np.isfinite(after)
        & (before != 0)
        & (after != 0)
    )

    if valid.sum() == 0:
        raise RuntimeError("No valid VV pixels found")

    delta = after - before

    mean_change = float(np.mean(delta[valid]))

    # Water/inundation candidate:
    # substantial negative VV change.
    candidate_mask = valid & (delta <= -1.5)

    candidate_pixels = int(candidate_mask.sum())

    pixel_size_x = abs(profile["transform"].a)
    pixel_size_y = abs(profile["transform"].e)

    pixel_area_m2 = pixel_size_x * pixel_size_y

    candidate_area_ha = (
        candidate_pixels * pixel_area_m2 / 10000.0
    )

    print(f"\n📡 Mean VV change: {mean_change:.6f} dB")
    print(f"🌊 Candidate new water: {candidate_area_ha:.6f} ha")

    return mean_change, candidate_area_ha


def main():

    print("=" * 70)
    print("🚀 TRINETRA SENTINEL-1 ACTUAL DATA PROCESSING")
    print("19 Aug 2026 → 19 Sep 2026")
    print("=" * 70)

    db = get_db()
    collection = db["sentinel1_metadata"]

    before_doc, after_doc, before_count, after_count = select_scenes(
        collection
    )

    before_time = parse_time(before_doc)
    after_time = parse_time(after_doc)

    print("\n⭐ SELECTED S1 ACQUISITIONS")

    print("\nBEFORE")
    print(before_doc.get("product_name") or before_doc.get("Name"))
    print("Time:", before_time)

    print("\nAFTER")
    print(after_doc.get("product_name") or after_doc.get("Name"))
    print("Time:", after_time)

    before_id = (
        before_doc.get("product_id")
        or before_doc.get("Id")
    )

    after_id = (
        after_doc.get("product_id")
        or after_doc.get("Id")
    )

    if not before_id or not after_id:
        raise RuntimeError("Product UUID missing from MongoDB")

    token = get_token()

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}"
    })

    os.makedirs("data/satellite/s1_processed", exist_ok=True)

    # ---------------- BEFORE ----------------

    print("\n" + "=" * 70)
    print("📡 PROCESSING BEFORE")
    print("=" * 70)

    print("\nProduct ID:")
    print(before_id)

    print("\n🔎 Finding VV band...")

    before_vv = find_vv_node(session, before_id)

    print("✅ Found VV:")
    print(before_vv)

    before_file = "data/satellite/s1_processed/before_VV.tiff"

    download_node(
        session,
        before_id,
        before_vv,
        before_file,
    )

    # ---------------- AFTER ----------------

    print("\n" + "=" * 70)
    print("📡 PROCESSING AFTER")
    print("=" * 70)

    print("\nProduct ID:")
    print(after_id)

    print("\n🔎 Finding VV band...")

    after_vv = find_vv_node(session, after_id)

    print("✅ Found VV:")
    print(after_vv)

    after_file = "data/satellite/s1_processed/after_VV.tiff"

    download_node(
        session,
        after_id,
        after_vv,
        after_file,
    )

    # ---------------- METRICS ----------------

    mean_vv_change, candidate_new_water = calculate_change(
        before_file,
        after_file,
    )

    metrics = {
        "analysis_period": "2026-08-19_to_2026-09-19",

        "sentinel1_before_scene_count": before_count,
        "sentinel1_after_scene_count": after_count,

        "sentinel1_before_acquisition":
            before_time,

        "sentinel1_after_acquisition":
            after_time,

        "sentinel1_before_product_id":
            before_id,

        "sentinel1_after_product_id":
            after_id,

        "sentinel1_mean_vv_change_db":
            mean_vv_change,

        "sentinel1_candidate_new_water_ha":
            candidate_new_water,

        "sentinel1_status":
            "ACTUAL_DATA_PROCESSED",

        "updated_at":
            datetime.now(timezone.utc),
    }

    db["satellite_metrics"].update_one(
        {
            "analysis_period":
                "2026-08-19_to_2026-09-19"
        },
        {
            "$set": metrics
        },
        upsert=True,
    )

    print("\n💾 Metrics saved to MongoDB")
    print("Collection: satellite_metrics")

    print("\n" + "=" * 70)
    print("✅ SENTINEL-1 ACTUAL PROCESSING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()