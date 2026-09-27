import os
import csv
from pathlib import Path

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
        with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                cleaned = {}
                for key, value in row.items():
                    if key is None:
                        continue
                    value = value.strip() if isinstance(value, str) else value
                    if value == "":
                        cleaned[key] = None
                        continue
                    try:
                        cleaned[key] = float(value)
                    except (ValueError, TypeError):
                        cleaned[key] = value
                rows.append(cleaned)
            return rows
    except Exception:
        return []



def refresh_terrain():
    db = get_db()
    collection = db["terrain_hazard"]

    output_file = (
        BASE_DIR
        / "data"
        / "features"
        / "dem_integrated_features.csv"
    )

    if not output_file.exists():
        return {
            "status": "error",
            "message": "dem_integrated_features.csv not found"
        }

    MAX_RECORDS = 5000
    records = []

    with open(
        output_file,
        "r",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for i, row in enumerate(reader):

            if i >= MAX_RECORDS:
                break

            clean_row = {}

            for key, value in row.items():

                if key is None:
                    continue

                value = value.strip() if isinstance(value, str) else value

                if value == "":
                    clean_row[key] = None
                    continue

                try:
                    clean_row[key] = float(value)
                except (ValueError, TypeError):
                    clean_row[key] = value

            records.append(clean_row)

    collection.delete_many({})

    if records:
        collection.insert_many(records, ordered=False)

    return {
        "status": "ok",
        "source": "DEM integrated terrain features",
        "collection": "terrain_hazard",
        "records": len(records)
    }


def get_latest_terrain():
    db = get_db()


    records = list(
        db["terrain_hazard"]
        .find({}, {"_id": 0})
        .limit(20)
    )

    if records:
        return records

    fallback_path = (
        BASE_DIR
        / "data"
        / "features"
        / "dem_integrated_features.csv"
    )
    fallback_records = _fallback_csv_records(fallback_path)
    return fallback_records[:20] if fallback_records else []

