import io
from pathlib import Path

import pandas as pd
import requests
import truststore


# Use Windows/system trusted certificates
truststore.inject_into_ssl()


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

CENSUS_URL = (
    "https://censusindia.gov.in/nada/index.php/catalog/6248/"
    "download/9325/DDW_PCA0502_2011_MDDS%20with%20UI.xlsx"
)

OUTPUT_DIR = Path("data/population")
OUTPUT_FILE = OUTPUT_DIR / "population.csv"


# --------------------------------------------------
# DOWNLOAD OFFICIAL CENSUS DATA
# --------------------------------------------------

print("🌐 Fetching official Census 2011 data...")

response = requests.get(
    CENSUS_URL,
    timeout=120
)

response.raise_for_status()

print("✅ Census file fetched")
print(f"📦 Downloaded: {len(response.content) / 1024:.1f} KB")


# --------------------------------------------------
# READ EXCEL FROM MEMORY
# --------------------------------------------------

print("📊 Reading Census Excel...")

excel_data = io.BytesIO(response.content)

df = pd.read_excel(
    excel_data,
    sheet_name="EB-0502",
    header=0
)

print("📐 Data shape:", df.shape)


# --------------------------------------------------
# CLEAN COLUMN NAMES
# --------------------------------------------------

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.upper()
)

print("👥 Population column: TOT_P")


# --------------------------------------------------
# FILTER JOSHIMATH SUB-DISTRICT
# --------------------------------------------------

print("📍 Filtering Joshimath sub-district...")

joshimath = df[
    (pd.to_numeric(df["DISTRICT"], errors="coerce") == 57) &
    (pd.to_numeric(df["SUBDISTT"], errors="coerce") == 284)
].copy()

print(f"✅ Joshimath records found: {len(joshimath)}")


# --------------------------------------------------
# KEEP IMPORTANT POPULATION FIELDS
if joshimath.empty:
    raise RuntimeError(
        "❌ No Joshimath records found. Check Census codes."
    )

population = joshimath[
    [
        "STATE",
        "DISTRICT",
        "SUBDISTT",
        "TOWN/VILLAGE",
        "WARD",
        "LEVEL",
        "NAME",
        "TRU",
        "NO_HH",
        "TOT_P",
        "TOT_M",
        "TOT_F"
    ]
].copy()


# --------------------------------------------------
# ADD METADATA
# --------------------------------------------------

population["POPULATION_YEAR"] = 2011
population["SOURCE"] = "Census of India - Population Census 2011"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

population.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Population data saved:")
print(OUTPUT_FILE)

print("\n📊 Sample:")
print(population.head(10).to_string(index=False))

print("\n🎯 Done!")