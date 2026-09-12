"""
TRINETRA - Final Relocation Planner
Member 2: Population / Relocation AI

Purpose
-------
Combines:
1. Population master
2. Settlement coordinates
3. Safe-site master
4. Trained relocation AI model

The AI model scores ALL geographically verified safe sites for every
source settlement.

The allocator then uses those AI rankings while respecting destination
capacity.

IMPORTANT
---------
- Does NOT modify or retrain the relocation model.
- Does NOT modify DEM / landslide outputs.
- Does NOT invent coordinates.
- Facilities without verified coordinates are excluded from geographic
  relocation allocation.
- Settlements without coordinates remain unresolved.
"""

from pathlib import Path
import pickle
import math

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

POPULATION_FILE = ROOT / "data" / "features" / "population_master.csv"
COORDINATE_FILE = (
    ROOT
    / "data"
    / "features"
    / "settlement_coordinates_final_master.csv"
)
SAFE_SITE_FILE = ROOT / "data" / "features" / "safe_sites.csv"
MODEL_FILE = ROOT / "models" / "relocation_model.pkl"

OUTPUT_PLAN = (
    ROOT
    / "data"
    / "features"
    / "final_relocation_plan.csv"
)

OUTPUT_SUMMARY = (
    ROOT
    / "data"
    / "features"
    / "final_relocation_summary.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Minimum number of people a destination must be able to receive.
MIN_SITE_CAPACITY = 1

# Keep every geographically valid site.
USE_ALL_GEOGRAPHIC_SITES = True


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates, required=True):
    """
    Find the first matching column from a list of candidates.
    Matching is case-insensitive.
    """

    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    if required:
        raise KeyError(
            f"Could not find any of these columns: {candidates}\n"
            f"Available columns:\n{list(df.columns)}"
        )

    return None


def numeric_series(df, column, default=0.0):
    """
    Safely convert a dataframe column to numeric.
    """

    if column is None:
        return pd.Series(default, index=df.index, dtype=float)

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(default)


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance in kilometres.
    """

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 6371.0 * 2 * math.asin(math.sqrt(a))


def normalize_distance(distance_km):
    """
    Convert distance into a decreasing score.

    0 km      -> 1.0
    larger km -> approaches 0
    """

    return 1.0 / (1.0 + max(float(distance_km), 0.0) / 10.0)


def clean_string(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("TRINETRA - FINAL RELOCATION PLANNER")
print("=" * 70)

print("\nLoading population data...")

population = pd.read_csv(POPULATION_FILE)

print(f"Population settlements loaded: {len(population)}")


print("\nLoading coordinate data...")

coordinates = pd.read_csv(COORDINATE_FILE)

print(f"Coordinate records loaded: {len(coordinates)}")


print("\nLoading safe-site data...")

safe_sites = pd.read_csv(SAFE_SITE_FILE)

print(f"Safe-site records loaded: {len(safe_sites)}")


print("\nLoading trained relocation model...")

with open(MODEL_FILE, "rb") as f:
    model_artifact = pickle.load(f)

# The training script stores the trained model inside a dictionary.
if isinstance(model_artifact, dict):

    if "model" in model_artifact:
        model = model_artifact["model"]

    elif "relocation_model" in model_artifact:
        model = model_artifact["relocation_model"]

    else:
        raise KeyError(
            "The relocation model pickle is a dictionary, but no "
            "'model' or 'relocation_model' key was found.\n"
            f"Available keys: {list(model_artifact.keys())}"
        )

else:
    # Also support a pickle containing the model directly.
    model = model_artifact

if not hasattr(model, "predict"):
    raise TypeError(
        "Loaded relocation model does not have a predict() method.\n"
        f"Loaded object type: {type(model)}"
    )

print(f"Model loaded: {MODEL_FILE}")
print(f"Model object type: {type(model).__name__}")


# ============================================================
# IDENTIFY POPULATION COLUMNS
# ============================================================

population_id_col = find_column(
    population,
    [
        "settlement_id",
        "id",
        "source_id",
    ]
)

population_name_col = find_column(
    population,
    [
        "settlement_name",
        "name",
        "NAME_CLEAN",
        "NAME",
    ]
)

population_value_col = find_column(
    population,
    [
        "population",
        "POP_2026_EST",
        "population_2026",
    ]
)

population_district_col = find_column(
    population,
    [
        "DISTRICT",
        "district",
    ],
    required=False
)


# ============================================================
# IDENTIFY COORDINATE COLUMNS
# ============================================================

coordinate_id_col = find_column(
    coordinates,
    [
        "settlement_id",
        "source_id",
        "id",
    ]
)

coordinate_lat_col = find_column(
    coordinates,
    [
        "latitude",
        "lat",
    ]
)

coordinate_lon_col = find_column(
    coordinates,
    [
        "longitude",
        "lon",
        "lng",
    ]
)

coordinate_status_col = find_column(
    coordinates,
    [
        "coordinate_status",
        "resolution_status",
        "verification_status",
    ],
    required=False
)


# ============================================================
# IDENTIFY SAFE-SITE COLUMNS
# ============================================================

site_id_col = find_column(
    safe_sites,
    [
        "site_id",
        "safe_site_id",
        "facility_id",
        "pseudocode",
        "id",
    ]
)

site_name_col = find_column(
    safe_sites,
    [
        "site_village",
        "site_name",
        "facility_name",
        "village_name",
        "name",
    ],
    required=False
)

site_capacity_col = find_column(
    safe_sites,
    [
        "temporary_capacity",
        "available_capacity",
        "capacity",
        "safe_capacity",
    ]
)

site_safe_score_col = find_column(
    safe_sites,
    [
        "safe_site_score",
        "safety_score",
        "site_safe_score",
    ]
)

site_accessibility_col = find_column(
    safe_sites,
    [
        "accessibility_score",
        "site_accessibility",
        "accessibility",
    ],
    required=False
)

site_infrastructure_col = find_column(
    safe_sites,
    [
        "infrastructure_score",
        "site_infrastructure",
        "infrastructure",
    ],
    required=False
)

site_lat_col = find_column(
    safe_sites,
    [
        "latitude",
        "lat",
    ]
)

site_lon_col = find_column(
    safe_sites,
    [
        "longitude",
        "lon",
        "lng",
    ]
)

site_district_col = find_column(
    safe_sites,
    [
        "district",
        "DISTRICT",
    ],
    required=False
)


# ============================================================
# NORMALIZE POPULATION DATA
# ============================================================

population_work = pd.DataFrame()

population_work["source_id"] = (
    population[population_id_col].astype(str).str.strip()
)

population_work["source_name"] = (
    population[population_name_col]
    .astype(str)
    .str.strip()
)

population_work["source_population"] = numeric_series(
    population,
    population_value_col,
    default=0
)

if population_district_col:
    population_work["source_district"] = (
        population[population_district_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
else:
    population_work["source_district"] = ""


population_work = (
    population_work
    .drop_duplicates(subset=["source_id"])
    .reset_index(drop=True)
)


# ============================================================
# NORMALIZE COORDINATES
# ============================================================

coordinate_work = pd.DataFrame()

coordinate_work["source_id"] = (
    coordinates[coordinate_id_col]
    .astype(str)
    .str.strip()
)

coordinate_work["source_latitude"] = numeric_series(
    coordinates,
    coordinate_lat_col,
    default=np.nan
)

coordinate_work["source_longitude"] = numeric_series(
    coordinates,
    coordinate_lon_col,
    default=np.nan
)

if coordinate_status_col:
    coordinate_work["coordinate_status"] = (
        coordinates[coordinate_status_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
else:
    coordinate_work["coordinate_status"] = ""


# Keep only one coordinate record per settlement.
coordinate_work = (
    coordinate_work
    .drop_duplicates(subset=["source_id"])
    .reset_index(drop=True)
)


# ============================================================
# MERGE POPULATION + COORDINATES
# ============================================================

sources = population_work.merge(
    coordinate_work,
    on="source_id",
    how="left"
)


sources["has_coordinates"] = (
    sources["source_latitude"].notna()
    & sources["source_longitude"].notna()
)


print("\nPopulation / coordinate coverage")
print("-" * 70)

print(
    f"Total settlements: "
    f"{len(sources)}"
)

print(
    f"Settlements with coordinates: "
    f"{sources['has_coordinates'].sum()}"
)

print(
    f"Settlements without coordinates: "
    f"{(~sources['has_coordinates']).sum()}"
)

print(
    f"Total population: "
    f"{sources['source_population'].sum():,.0f}"
)


# ============================================================
# NORMALIZE SAFE SITES
# ============================================================

sites = pd.DataFrame()

sites["site_id"] = (
    safe_sites[site_id_col]
    .astype(str)
    .str.strip()
)

if site_name_col:
    sites["site_name"] = (
        safe_sites[site_name_col]
        .fillna("Educational Facility")
        .astype(str)
        .str.strip()
    )
else:
    sites["site_name"] = "Educational Facility"


sites["site_capacity"] = numeric_series(
    safe_sites,
    site_capacity_col,
    default=0
).clip(lower=0)


sites["site_safe_score"] = numeric_series(
    safe_sites,
    site_safe_score_col,
    default=0
)


sites["site_accessibility"] = numeric_series(
    safe_sites,
    site_accessibility_col,
    default=0
)


sites["site_infrastructure"] = numeric_series(
    safe_sites,
    site_infrastructure_col,
    default=0
)


sites["site_latitude"] = numeric_series(
    safe_sites,
    site_lat_col,
    default=np.nan
)


sites["site_longitude"] = numeric_series(
    safe_sites,
    site_lon_col,
    default=np.nan
)


if site_district_col:
    sites["site_district"] = (
        safe_sites[site_district_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
else:
    sites["site_district"] = ""


# Remove duplicate site IDs.
sites = (
    sites
    .drop_duplicates(subset=["site_id"])
    .reset_index(drop=True)
)


# ============================================================
# GEOGRAPHICALLY VALID SAFE SITES
# ============================================================

sites["has_coordinates"] = (
    sites["site_latitude"].notna()
    & sites["site_longitude"].notna()
)


sites = sites[
    sites["has_coordinates"]
    & (sites["site_capacity"] >= MIN_SITE_CAPACITY)
].copy()


sites["site_capacity"] = np.floor(
    sites["site_capacity"]
).astype(int)


sites = sites[
    sites["site_capacity"] > 0
].reset_index(drop=True)


print("\nSafe-site geographic coverage")
print("-" * 70)

print(
    f"Geographically usable safe sites: "
    f"{len(sites)}"
)

print(
    f"Geographic capacity: "
    f"{sites['site_capacity'].sum():,.0f}"
)


# ============================================================
# CAPACITY NORMALIZATION
# ============================================================

max_capacity = sites["site_capacity"].max()

if max_capacity <= 0:
    max_capacity = 1

sites["site_capacity_normalized"] = (
    sites["site_capacity"] / max_capacity
)


# ============================================================
# MODEL FEATURE SCHEMA
# ============================================================

MODEL_FEATURES = [
    "source_population",
    "source_latitude",
    "source_longitude",
    "site_safe_score",
    "site_capacity",
    "site_capacity_normalized",
    "site_accessibility",
    "site_infrastructure",
    "site_latitude",
    "site_longitude",
    "distance_km",
    "distance_score",
    "same_district",
]


print("\nModel feature schema")
print("-" * 70)

print(MODEL_FEATURES)


# ============================================================
# GENERATE AI SCORES FOR ALL SOURCE-SITE PAIRS
# ============================================================

print("\nGenerating AI scores for ALL geographically valid sites...")

candidate_rows = []

geographic_sources = sources[
    sources["has_coordinates"]
].copy()


for _, source in geographic_sources.iterrows():

    source_id = source["source_id"]
    source_name = source["source_name"]

    source_lat = float(source["source_latitude"])
    source_lon = float(source["source_longitude"])

    source_population = float(
        source["source_population"]
    )

    source_district = clean_string(
        source["source_district"]
    ).lower()


    for _, site in sites.iterrows():

        site_id = site["site_id"]

        site_lat = float(site["site_latitude"])
        site_lon = float(site["site_longitude"])

        distance = haversine_km(
            source_lat,
            source_lon,
            site_lat,
            site_lon
        )

        distance_score = normalize_distance(distance)

        site_district = clean_string(
            site["site_district"]
        ).lower()

        same_district = int(
            bool(source_district)
            and bool(site_district)
            and source_district == site_district
        )


        row = {
            "source_population": source_population,
            "source_latitude": source_lat,
            "source_longitude": source_lon,
            "site_safe_score": float(
                site["site_safe_score"]
            ),
            "site_capacity": float(
                site["site_capacity"]
            ),
            "site_capacity_normalized": float(
                site["site_capacity_normalized"]
            ),
            "site_accessibility": float(
                site["site_accessibility"]
            ),
            "site_infrastructure": float(
                site["site_infrastructure"]
            ),
            "site_latitude": site_lat,
            "site_longitude": site_lon,
            "distance_km": distance,
            "distance_score": distance_score,
            "same_district": same_district,
        }

        candidate_rows.append(
            {
                "source_id": source_id,
                "source_name": source_name,
                "site_id": site_id,
                "site_name": site["site_name"],
                "site_capacity": int(
                    site["site_capacity"]
                ),
                "site_safe_score": float(
                    site["site_safe_score"]
                ),
                "site_accessibility": float(
                    site["site_accessibility"]
                ),
                "site_infrastructure": float(
                    site["site_infrastructure"]
                ),
                "site_latitude": site_lat,
                "site_longitude": site_lon,
                "site_district": site_district,
                "distance_km": distance,
                "distance_score": distance_score,
                "same_district": same_district,
                "model_features": row,
            }
        )


print(
    f"Total source-site pairs generated: "
    f"{len(candidate_rows):,}"
)


# ============================================================
# AI PREDICTION
# ============================================================

prediction_frame = pd.DataFrame(
    [
        item["model_features"]
        for item in candidate_rows
    ]
)

prediction_frame = prediction_frame[
    MODEL_FEATURES
]


ai_scores = model.predict(
    prediction_frame
)


for item, score in zip(candidate_rows, ai_scores):
    item["ai_score"] = float(score)


candidates = pd.DataFrame(
    [
        {
            key: value
            for key, value in item.items()
            if key != "model_features"
        }
        for item in candidate_rows
    ]
)


# ============================================================
# RANK ALL SITES
# ============================================================

candidates = candidates.sort_values(
    by=[
        "source_id",
        "ai_score",
        "site_safe_score",
        "distance_km",
    ],
    ascending=[
        True,
        False,
        False,
        True,
    ]
).reset_index(drop=True)


# Rank each destination for each source.
candidates["ai_rank"] = (
    candidates
    .groupby("source_id")
    .cumcount()
    + 1
)


print("\nAI ranking")
print("-" * 70)

print(
    f"Total scored pairs: "
    f"{len(candidates):,}"
)

print(
    f"Unique source settlements: "
    f"{candidates['source_id'].nunique()}"
)

print(
    f"Unique safe sites considered: "
    f"{candidates['site_id'].nunique()}"
)

print(
    f"AI score minimum: "
    f"{candidates['ai_score'].min():.3f}"
)

print(
    f"AI score maximum: "
    f"{candidates['ai_score'].max():.3f}"
)

print(
    f"AI score mean: "
    f"{candidates['ai_score'].mean():.3f}"
)


# ============================================================
# CAPACITY-CONSTRAINED ALLOCATION
# ============================================================

print("\nRunning capacity-constrained allocation...")
print("Using complete AI ranking, not TOP_K.")


remaining_capacity = {
    str(row["site_id"]): int(row["site_capacity"])
    for _, row in sites.iterrows()
}


allocation_rows = []

allocated_by_source = {
    str(source_id): 0
    for source_id in sources["source_id"]
}


# Process sources in descending population order.
#
# Larger settlements are handled first so that available
# emergency capacity is not consumed entirely by small
# settlements.
source_order = geographic_sources.sort_values(
    by="source_population",
    ascending=False
)


for _, source in source_order.iterrows():

    source_id = str(source["source_id"])
    source_name = source["source_name"]

    source_population = int(
        round(source["source_population"])
    )

    if source_population <= 0:
        continue


    source_candidates = candidates[
        candidates["source_id"].astype(str) == source_id
    ].sort_values(
        by=[
            "ai_score",
            "site_safe_score",
            "distance_km",
        ],
        ascending=[
            False,
            False,
            True,
        ]
    )


    remaining_people = source_population


    for _, candidate in source_candidates.iterrows():

        if remaining_people <= 0:
            break


        site_id = str(candidate["site_id"])

        available = int(
            remaining_capacity.get(
                site_id,
                0
            )
        )


        if available <= 0:
            continue


        allocation = min(
            remaining_people,
            available
        )


        if allocation <= 0:
            continue


        remaining_capacity[site_id] -= allocation
        remaining_people -= allocation

        allocated_by_source[source_id] += allocation


        allocation_rows.append(
            {
                "source_settlement_id": source_id,
                "source_settlement": source_name,
                "source_population_2026_est": source_population,

                "destination_site_id": site_id,
                "destination_site": candidate["site_name"],

                "allocated_people": int(allocation),

                "ai_score": round(
                    float(candidate["ai_score"]),
                    3
                ),

                "ai_rank": int(
                    candidate["ai_rank"]
                ),

                "distance_km": round(
                    float(candidate["distance_km"]),
                    3
                ),

                "site_safe_score": round(
                    float(candidate["site_safe_score"]),
                    3
                ),

                "site_accessibility": round(
                    float(candidate["site_accessibility"]),
                    3
                ),

                "site_infrastructure": round(
                    float(candidate["site_infrastructure"]),
                    3
                ),

                "site_capacity_original": int(
                    candidate["site_capacity"]
                ),

                "site_capacity_remaining_after": int(
                    remaining_capacity[site_id]
                ),

                "destination_latitude": float(
                    candidate["site_latitude"]
                ),

                "destination_longitude": float(
                    candidate["site_longitude"]
                ),

                "allocation_status": "ALLOCATED",

                "allocation_reason": (
                    "AI-ranked geographically verified "
                    "safe site with available capacity"
                ),
            }
        )


# ============================================================
# UNRESOLVED / UNALLOCATED SOURCES
# ============================================================

for _, source in sources.iterrows():

    source_id = str(source["source_id"])
    source_name = source["source_name"]

    source_population = int(
        round(source["source_population"])
    )

    allocated = int(
        allocated_by_source.get(
            source_id,
            0
        )
    )

    unallocated = max(
        source_population - allocated,
        0
    )


    if not source["has_coordinates"]:

        allocation_rows.append(
            {
                "source_settlement_id": source_id,
                "source_settlement": source_name,
                "source_population_2026_est": source_population,

                "destination_site_id": "",
                "destination_site": "",

                "allocated_people": 0,

                "ai_score": np.nan,
                "ai_rank": np.nan,
                "distance_km": np.nan,

                "site_safe_score": np.nan,
                "site_accessibility": np.nan,
                "site_infrastructure": np.nan,

                "site_capacity_original": 0,
                "site_capacity_remaining_after": 0,

                "destination_latitude": np.nan,
                "destination_longitude": np.nan,

                "allocation_status": "UNRESOLVED",

                "allocation_reason": (
                    "SOURCE_COORDINATES_UNAVAILABLE"
                ),
            }
        )

        continue


    if unallocated > 0:

        allocation_rows.append(
            {
                "source_settlement_id": source_id,
                "source_settlement": source_name,
                "source_population_2026_est": source_population,

                "destination_site_id": "",
                "destination_site": "",

                "allocated_people": 0,

                "ai_score": np.nan,
                "ai_rank": np.nan,
                "distance_km": np.nan,

                "site_safe_score": np.nan,
                "site_accessibility": np.nan,
                "site_infrastructure": np.nan,

                "site_capacity_original": 0,
                "site_capacity_remaining_after": 0,

                "destination_latitude": np.nan,
                "destination_longitude": np.nan,

                "allocation_status": "UNALLOCATED",

                "allocation_reason": (
                    "INSUFFICIENT_GEOGRAPHIC_CAPACITY"
                ),
            }
        )


# ============================================================
# SAVE FINAL PLAN
# ============================================================

final_plan = pd.DataFrame(
    allocation_rows
)


final_plan.to_csv(
    OUTPUT_PLAN,
    index=False
)


# ============================================================
# BUILD SUMMARY
# ============================================================

total_population = int(
    round(
        sources["source_population"].sum()
    )
)

total_allocated = int(
    final_plan["allocated_people"].sum()
)

total_unallocated = (
    total_population
    - total_allocated
)


allocation_rate = (
    total_allocated / total_population * 100
    if total_population > 0
    else 0
)


fully_allocated = 0
partially_allocated = 0
unresolved = 0


for _, source in sources.iterrows():

    source_id = str(source["source_id"])

    population_value = int(
        round(source["source_population"])
    )

    allocated = int(
        allocated_by_source.get(
            source_id,
            0
        )
    )

    if not source["has_coordinates"]:
        unresolved += 1

    elif allocated >= population_value:
        fully_allocated += 1

    elif allocated > 0:
        partially_allocated += 1


remaining_geographic_capacity = int(
    sum(remaining_capacity.values())
)


summary_rows = [
    {
        "metric": "population_settlements",
        "value": len(sources),
    },
    {
        "metric": "total_population_2026_est",
        "value": total_population,
    },
    {
        "metric": "safe_sites_with_verified_coordinates",
        "value": len(sites),
    },
    {
        "metric": "geographic_safe_site_capacity",
        "value": int(
            sites["site_capacity"].sum()
        ),
    },
    {
        "metric": "remaining_safe_site_capacity",
        "value": remaining_geographic_capacity,
    },
    {
        "metric": "settlements_with_coordinates",
        "value": int(
            sources["has_coordinates"].sum()
        ),
    },
    {
        "metric": "settlements_without_coordinates",
        "value": int(
            (~sources["has_coordinates"]).sum()
        ),
    },
    {
        "metric": "ai_source_site_pairs",
        "value": len(candidates),
    },
    {
        "metric": "unique_ai_ranked_sites",
        "value": candidates["site_id"].nunique(),
    },
    {
        "metric": "allocated_population",
        "value": total_allocated,
    },
    {
        "metric": "unallocated_population",
        "value": total_unallocated,
    },
    {
        "metric": "allocation_rate_percent",
        "value": round(
            allocation_rate,
            2
        ),
    },
    {
        "metric": "fully_allocated_settlements",
        "value": fully_allocated,
    },
    {
        "metric": "partially_allocated_settlements",
        "value": partially_allocated,
    },
    {
        "metric": "unresolved_settlements",
        "value": unresolved,
    },
]


summary = pd.DataFrame(
    summary_rows
)


summary.to_csv(
    OUTPUT_SUMMARY,
    index=False
)


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL RELOCATION RESULTS")
print("=" * 70)

print(
    f"Population settlements: "
    f"{len(sources)}"
)

print(
    f"Total population: "
    f"{total_population:,}"
)

print(
    f"Geographically verified safe sites: "
    f"{len(sites)}"
)

print(
    f"Geographic capacity: "
    f"{int(sites['site_capacity'].sum()):,}"
)

print(
    f"AI source-site pairs: "
    f"{len(candidates):,}"
)

print(
    f"Unique AI-ranked sites: "
    f"{candidates['site_id'].nunique()}"
)

print(
    f"Allocated population: "
    f"{total_allocated:,}"
)

print(
    f"Unallocated population: "
    f"{total_unallocated:,}"
)

print(
    f"Allocation rate: "
    f"{allocation_rate:.2f}%"
)

print(
    f"Fully allocated settlements: "
    f"{fully_allocated}"
)

print(
    f"Partially allocated settlements: "
    f"{partially_allocated}"
)

print(
    f"Unresolved settlements: "
    f"{unresolved}"
)

print(
    f"Remaining geographic capacity: "
    f"{remaining_geographic_capacity:,}"
)


# ============================================================
# TOP ALLOCATIONS
# ============================================================

allocated_rows = final_plan[
    final_plan["allocation_status"] == "ALLOCATED"
].copy()


if not allocated_rows.empty:

    print("\nTop allocations:")
    print("-" * 70)

    display_columns = [
        "source_settlement",
        "destination_site",
        "allocated_people",
        "ai_score",
        "distance_km",
    ]

    print(
        allocated_rows[
            display_columns
        ]
        .head(15)
        .to_string(index=False)
    )


# ============================================================
# OUTPUT PATHS
# ============================================================

print("\n" + "=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print(f"Final plan:")
print(OUTPUT_PLAN)

print(f"\nFinal summary:")
print(OUTPUT_SUMMARY)

print("\nDone.")