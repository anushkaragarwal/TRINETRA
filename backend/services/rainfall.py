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



def _fallback_csv_records(path: Path):
    if not path.exists():
        return []

    try:
        df = pd.read_csv(path)
    except Exception:
        return []

    if df.empty:
        return []

    df = df.astype(object).where(pd.notna(df), None)
    return df.to_dict(orient="records")



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


    records = list(
        db["rainfall_hazard"]
        .find({}, {"_id": 0})
        .limit(20)
    )

    if records:
        return records

    fallback_path = (
        BASE_DIR
        / "data"
        / "rainfall"
        / "processed"
        / "rainfall_hybrid_hazard.csv"
    )
    fallback_records = _fallback_csv_records(fallback_path)
    return fallback_records[:20] if fallback_records else []

