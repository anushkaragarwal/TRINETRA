from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "data" / "population" / "population.csv"
dst = ROOT / "data" / "population" / "population_habitations.csv"

df = pd.read_csv(src)

# 1) Sirf villages + town level rows
hab = df[df["LEVEL"].isin(["VILLAGE", "TOWN"])].copy()

# 2) Normalised name (join ke liye)
hab["NAME_CLEAN"] = (
    hab["NAME"]
    .str.strip()
    .str.upper()
)

print("Habitations shape:", hab.shape)
print(hab.head())

dst.parent.mkdir(parents=True, exist_ok=True)
hab.to_csv(dst, index=False)
print("Saved:", dst)