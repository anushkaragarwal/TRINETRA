import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "trinetra")


def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DB]


def refresh_rainfall():
    db = get_db()
    collection = db["rainfall_hazard"]

    output_file = (
        BASE_DIR
        / "data"
        / "rainfall"
        / "processed"
        / "rainfall_hybrid_hazard.csv"
    )

    if not output_file.exists():
        return {
            "status": "error",
            "message": "rainfall_hybrid_hazard.csv not found"
        }

    df = pd.read_csv(output_file)

    if df.empty:
        return {
            "status": "ok",
            "records": 0
        }

    records = df.to_dict(orient="records")

    collection.delete_many({})
    collection.insert_many(records)

    return {
        "status": "ok",
        "source": "existing rainfall pipeline output",
        "collection": "rainfall_hazard",
        "records": len(records)
    }


def get_latest_rainfall():
    db = get_db()

    return list(
        db["rainfall_hazard"]
        .find({}, {"_id": 0})
        .limit(20)
    )