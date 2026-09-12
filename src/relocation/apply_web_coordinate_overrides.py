from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT = BASE_DIR / "data" / "features" / "settlement_coordinates_resolved.csv"
OUTPUT = BASE_DIR / "data" / "features" / "settlement_coordinates_web_verified.csv"
REVIEW = BASE_DIR / "data" / "features" / "coordinate_web_review.csv"

OVERRIDES = {'khiron': (30.686187, 79.482644, 'PaintMaps Chamoli map', 'MEDIUM'), 'arurhi paturi': (30.648057, 79.532948, 'PaintMaps Chamoli map', 'MEDIUM'), 'pandukaswar': (30.633418, 79.548607, 'PaintMaps Chamoli map', 'MEDIUM'), 'pulana chak bhyudar': (30.634643, 79.572274, 'PaintMaps Chamoli map', 'MEDIUM'), 'toli laga chiae': (30.584483, 79.546531, 'PaintMaps Chamoli map; matched spelling Toli Laga Chaie', 'MEDIUM'), 'chaien': (30.566174, 79.538058, 'PaintMaps Chamoli map', 'MEDIUM'), 'bharkichak-urgam': (30.548262, 79.462068, 'PaintMaps Chamoli map; matched spelling Bharki Chak Urgam', 'MEDIUM'), 'bheta chak urgam': (30.540621, 79.469825, 'PaintMaps Chamoli map', 'MEDIUM'), 'lyari thana': (30.529839, 79.471426, 'PaintMaps Chamoli map', 'MEDIUM'), 'salna chak urgam': (30.530055, 79.492736, 'PaintMaps Chamoli map', 'MEDIUM'), 'hailang': (30.525162, 79.500225, 'PaintMaps Chamoli map', 'MEDIUM'), 'paini': (30.528091, 79.521383, 'PaintMaps Chamoli map; Joshimath-area occurrence', 'MEDIUM'), 'sailang': (30.539261, 79.528345, 'PaintMaps Chamoli map', 'MEDIUM'), 'gaunkh laga sailang': (30.545382, 79.542532, 'PaintMaps Chamoli map', 'MEDIUM'), 'auli laga joshimath': (30.532778, 79.568611, 'Wikidata/Census-linked Auli coordinate', 'MEDIUM'), 'auli laga salud dugra': (30.525709, 79.569699, 'PaintMaps Chamoli map', 'MEDIUM'), 'salud dugra': (30.510883, 79.523146, 'PaintMaps Chamoli map', 'MEDIUM'), 'uchougaur': (30.503089, 79.431598, 'PaintMaps Chamoli map', 'MEDIUM'), 'jakhola': (30.507425, 79.460068, 'PaintMaps Chamoli map', 'MEDIUM'), 'pokhani urf pokhari': (30.476002, 79.433276, 'PaintMaps Chamoli map', 'MEDIUM'), 'tapon': (30.494761, 79.473569, 'PaintMaps Chamoli map', 'MEDIUM'), 'tangni talli': (30.477567, 79.463872, 'PaintMaps Chamoli map', 'MEDIUM'), 'tangni malli': (30.476768, 79.472709, 'PaintMaps Chamoli map', 'MEDIUM'), 'jalgwar': (30.465385, 79.451459, 'PaintMaps Chamoli map', 'MEDIUM'), 'marwadi chak pakhi': (30.461114, 79.44693, 'PaintMaps Chamoli map', 'MEDIUM'), 'noligwar': (30.480475, 79.493199, 'PaintMaps Chamoli map', 'MEDIUM'), 'bhalgaon': (30.519004, 79.732875, 'PaintMaps Chamoli map', 'MEDIUM'), 'longsagari': (30.596568, 79.785626, 'PaintMaps Chamoli map', 'MEDIUM'), 'fagti': (30.55631, 79.775609, 'PaintMaps Chamoli map', 'MEDIUM'), 'pagrasu': (30.550788, 79.754937, 'PaintMaps Chamoli map', 'MEDIUM'), 'sukhi': (30.520034, 79.728758, 'PaintMaps Chamoli map', 'MEDIUM'), 'khancha talla': (30.536987, 79.597058, 'PaintMaps Chamoli map', 'MEDIUM'), 'khancha malla': (30.53591, 79.593152, 'PaintMaps Chamoli map', 'MEDIUM'), 'merag': (30.528207, 79.596253, 'PaintMaps Chamoli map; matched alias Mirag/Merag', 'MEDIUM'), 'bara gaon': (30.521287, 79.600341, 'PaintMaps Chamoli map', 'MEDIUM'), 'payya chormi': (30.517371, 79.608799, 'PaintMaps Chamoli map', 'MEDIUM'), 'kundikhola': (30.499528, 79.609174, 'PaintMaps Chamoli map', 'MEDIUM'), 'raigari': (30.477774, 79.612045, 'PaintMaps Chamoli map', 'MEDIUM'), 'bilagar': (30.495604, 79.61983, 'PaintMaps Chamoli map', 'MEDIUM'), 'topovan': (30.4861, 79.4639, 'IIT Roorkee river-gauging station named Topovan; proxy only', 'LOW_PROXY'), 'gahar': (30.501148, 79.625009, 'PaintMaps Chamoli map', 'MEDIUM'), 'karachhon': (30.47768, 79.619269, 'PaintMaps Chamoli map; matched spelling Karchhon', 'MEDIUM'), 'jugaju chak lata': (30.490226, 79.691506, 'PaintMaps Chamoli map', 'MEDIUM'), 'raini chak lata': (30.488322, 79.694825, 'PaintMaps Chamoli map', 'MEDIUM'), 'morana chak subhai': (30.46927, 79.703664, 'PaintMaps Chamoli map', 'MEDIUM'), 'subhai': (30.479065, 79.676862, 'PaintMaps Chamoli map', 'MEDIUM'), 'raini chak subhai': (30.48615, 79.691402, 'PaintMaps Chamoli map', 'MEDIUM'), 'gurguti': (30.711087, 79.843565, 'PaintMaps Chamoli map', 'MEDIUM'), 'kailashpur': (30.706927, 79.876135, 'PaintMaps Chamoli map; supported by Niti Valley field-study location', 'MEDIUM'), 'jalam': (30.638213, 79.825207, 'PaintMaps Chamoli map', 'MEDIUM'), 'kaga laga dronagiri': (30.612136, 79.823992, 'PaintMaps Chamoli map', 'MEDIUM'), 'badrinathpuri (np)': (30.743, 79.494, 'Geocountries Badrinathpuri map', 'MEDIUM'), 'joshimath  (npp)': (30.5529, 79.563216, 'PaintMaps Chamoli map', 'MEDIUM')}

def norm(x):
    return " ".join(str(x).strip().lower().split())

def main():
    df = pd.read_csv(INPUT)
    if "settlement_name" not in df.columns:
        raise ValueError("settlement_name column missing.")
    if "latitude" not in df.columns or "longitude" not in df.columns:
        raise ValueError("latitude/longitude columns missing.")

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    review = []
    for i, row in df.iterrows():
        name = str(row["settlement_name"]).strip()
        key = norm(name)
        if key in OVERRIDES and (pd.isna(row["latitude"]) or pd.isna(row["longitude"])):
            lat, lon, source, confidence = OVERRIDES[key]
            df.at[i, "latitude"] = lat
            df.at[i, "longitude"] = lon
            df.at[i, "coordinate_source"] = source
            df.at[i, "coordinate_confidence"] = confidence
            df.at[i, "resolution_status"] = "WEB_RESEARCHED"
            review.append({"settlement_name": name, "latitude": lat, "longitude": lon,
                           "source": source, "confidence": confidence, "status": "FILLED"})
        elif pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            review.append({"settlement_name": name, "latitude": None, "longitude": None,
                           "source": "No defensible coordinate found in researched sources",
                           "confidence": "MISSING", "status": "UNRESOLVED"})
        else:
            review.append({"settlement_name": name, "latitude": row["latitude"], "longitude": row["longitude"],
                           "source": row.get("coordinate_source","EXISTING"), "confidence": row.get("coordinate_confidence","EXISTING"),
                           "status": "PRESERVED"})

    df.to_csv(OUTPUT, index=False)
    pd.DataFrame(review).to_csv(REVIEW, index=False)

    valid = df["latitude"].notna() & df["longitude"].notna()
    print("="*70)
    print("TRINETRA - WEB-VERIFIED SETTLEMENT COORDINATES")
    print("="*70)
    print(f"Total settlements : {len(df)}")
    print(f"Usable coordinates: {valid.sum()}")
    print(f"Still missing     : {(~valid).sum()}")
    print(f"\nOutput : {OUTPUT}")
    print(f"Review : {REVIEW}")
    if (~valid).sum():
        print("\nStill unresolved:")
        print(df.loc[~valid, ["settlement_id","settlement_name"]].to_string(index=False))

if __name__ == "__main__":
    main()
