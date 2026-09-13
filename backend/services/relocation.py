import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pandas.errors import EmptyDataError

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")


def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB]


def load_csv(collection_name, file_path):
    db = get_db()
    collection = db[collection_name]

    if not file_path.exists():
        return {
            "status": "skipped",
            "collection": collection_name,
            "records": 0,
            "message": f"{file_path.name} not found"
        }

    if file_path.stat().st_size == 0:
        collection.delete_many({})
        return {
            "status": "ok",
            "collection": collection_name,
            "records": 0,
            "message": "empty file"
        }

    try:
        df = pd.read_csv(file_path)
    except EmptyDataError:
        collection.delete_many({})
        return {
            "status": "ok",
            "collection": collection_name,
            "records": 0,
            "message": "empty CSV"
        }

    if df.empty:
        collection.delete_many({})
        return {
            "status": "ok",
            "collection": collection_name,
            "records": 0
        }

    # Convert NaN/NaT to None for MongoDB
    df = df.astype(object).where(pd.notna(df), None)

    records = df.to_dict(orient="records")

    collection.delete_many({})

    if records:
        collection.insert_many(records, ordered=False)

    return {
        "status": "ok",
        "collection": collection_name,
        "records": len(records),
        "source": file_path.name
    }


def refresh_relocation_data():
    datasets = [
        ("population", BASE_DIR / "data/features/population_master.csv"),
        ("safe_sites", BASE_DIR / "data/features/safe_sites.csv"),
        ("relocation_assignments", BASE_DIR / "data/features/relocation_assignments.csv"),
        ("relocation_recommendations", BASE_DIR / "data/features/relocation_recommendations.csv"),
        ("final_relocation_plan", BASE_DIR / "data/features/final_relocation_plan.csv"),
        ("roads", BASE_DIR / "data/infrastructure/roads.csv"),
        ("bridges", BASE_DIR / "data/infrastructure/bridges.csv"),
        ("shelters", BASE_DIR / "data/infrastructure/shelters.csv"),
        ("hospitals", BASE_DIR / "data/health/health_facilities_final.csv")
        
    ]

    results = [
        load_csv(collection_name, file_path)
        for collection_name, file_path in datasets
    ]

    return {
        "status": "ok",
        "datasets": results
    }


def get_relocation_summary():
    db = get_db()

    return {
        "population": db["population"].count_documents({}),
        "safe_sites": db["safe_sites"].count_documents({}),
        "relocation_assignments": db["relocation_assignments"].count_documents({}),
        "relocation_recommendations": db["relocation_recommendations"].count_documents({}),
        "final_relocation_plan": db["final_relocation_plan"].count_documents({}),
        "roads": db["roads"].count_documents({}),
        "bridges": db["bridges"].count_documents({}),
        "shelters": db["shelters"].count_documents({}),
        "hospitals": db["hospitals"].count_documents({}),
        "emergency_capabilities": db["emergency_capabilities"].count_documents({}),
    }
def get_top_relocations(limit=20):
    db = get_db()

    records = list(
        db["final_relocation_plan"]
        .find(
            {"allocation_status": "ALLOCATED"},
            {"_id": 0}
        )
        .sort("ai_score", -1)
        .limit(limit)
    )

    return {
        "status": "ok",
        "count": len(records),
        "relocations": records
    }

import math


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def nearest_facility(db, collection_name, lat, lon):
    facilities = db[collection_name].find(
        {},
        {"_id": 0}
    )

    best = None
    best_distance = float("inf")

    for item in facilities:
        facility_lat = item.get("latitude", item.get("lat"))
        facility_lon = item.get("longitude", item.get("lon"))

        if facility_lat is None or facility_lon is None:
            continue

        try:
            distance = haversine_km(
                lat, lon,
                float(facility_lat),
                float(facility_lon)
            )
        except (ValueError, TypeError):
            continue

        if distance < best_distance:
            best_distance = distance
            best = item

    if best is None:
        return None

    return {
        "distance_km": round(best_distance, 2),
        "facility": best
    }


def get_relocation_decisions(limit=20):
    db = get_db()

    relocations = list(
        db["final_relocation_plan"]
        .find(
            {"allocation_status": "ALLOCATED"},
            {"_id": 0}
        )
        .sort("ai_score", -1)
        .limit(limit)
    )

    results = []

    for item in relocations:
        lat = item.get("destination_latitude")
        lon = item.get("destination_longitude")

        if lat is None or lon is None:
            continue

        road = nearest_facility(db, "roads", lat, lon)
        bridge = nearest_facility(db, "bridges", lat, lon)
        hospital = nearest_facility(db, "hospitals", lat, lon)
        emergency = nearest_facility(
            db,
            "emergency_capabilities",
            lat,
            lon
        )

        item["emergency_access"] = {
            "nearest_road_km": road["distance_km"] if road else None,
            "nearest_bridge_km": bridge["distance_km"] if bridge else None,
            "nearest_hospital_km": hospital["distance_km"] if hospital else None,
            "nearest_emergency_facility_km": (
                emergency["distance_km"] if emergency else None
            )
        }

        # Simple emergency accessibility assessment
        road_ok = road is not None and road["distance_km"] <= 2
        hospital_ok = hospital is not None and hospital["distance_km"] <= 25
        bridge_ok = bridge is not None and bridge["distance_km"] <= 10

        if road_ok and hospital_ok:
            access_status = "GOOD"
        elif road_ok or hospital_ok:
            access_status = "MODERATE"
        else:
            access_status = "LIMITED"

        item["emergency_access"]["status"] = access_status

        if access_status == "LIMITED":
            item["recommended_action"] = (
                "REVIEW ROUTE BEFORE RELOCATION"
            )
        else:
            item["recommended_action"] = (
                "RELOCATION ROUTE FEASIBLE"
            )

        results.append(item)

    return {
        "status": "ok",
        "count": len(results),
        "relocations": results
    }