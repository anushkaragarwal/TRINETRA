from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "data" / "population" / "population_habitations.csv"
dst = ROOT / "data" / "population" / "population_habitations_2026.csv"

ANNUAL_GROWTH_RATE = 0.011  # ~1.1% per year (Uttarakhand projections)

hab = pd.read_csv(src)

years = 15  # 2011 -> 2026
factor = (1 + ANNUAL_GROWTH_RATE) ** years

hab["POP_2011"] = hab["TOT_P"]
hab["POP_2026_EST"] = (hab["TOT_P"] * factor).round().astype(int)

print("Growth factor 2011->2026:", round(factor, 3))
print(hab[["NAME", "LEVEL", "POP_2011", "POP_2026_EST"]].head())

dst.parent.mkdir(parents=True, exist_ok=True)
hab.to_csv(dst, index=False)
print("Saved:", dst)