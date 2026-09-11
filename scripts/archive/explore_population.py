from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

RAW_PATH = (
    ROOT
    / "data"
    / "population"
    / "population.csv"
)

HABITATION_PATH = (
    ROOT
    / "data"
    / "population"
    / "population_habitations.csv"
)


def main():
    raw = pd.read_csv(RAW_PATH)
    hab = pd.read_csv(HABITATION_PATH)

    print("=== RAW CENSUS SUBSET ===")
    print("Shape:", raw.shape)

    official_total = raw[
        (raw["LEVEL"] == "SUB-DISTRICT")
        & (raw["TRU"] == "Total")
    ]["TOT_P"].iloc[0]

    print("Official Joshimath sub-district total:", official_total)

    print("\n=== HABITATION DATASET ===")
    print("Shape:", hab.shape)

    print("\nLevel counts:")
    print(hab["LEVEL"].value_counts().to_string())

    print("\nPopulation total from village + town totals:")
    print(hab["TOT_P"].sum())

    print("\nExpected total should equal:")
    print(official_total)

    print("\nPopulation totals by level:")
    print(
        hab.groupby("LEVEL")["TOT_P"]
        .sum()
        .to_string()
    )

    print("\nTop 10 highest-population habitations:")
    print(
        hab.sort_values(
            by="TOT_P",
            ascending=False,
        )[
            [
                "NAME",
                "LEVEL",
                "TRU",
                "NO_HH",
                "TOT_P",
                "TOT_M",
                "TOT_F",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()