from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PATH = (
    ROOT
    / "data"
    / "population"
    / "population_habitations_2026.csv"
)


def main():
    df = pd.read_csv(PATH)

    print("Shape:", df.shape)

    print("\nPopulation totals:")
    print("2011 Census population:", df["POP_2011"].sum())
    print("Estimated 2026 population:", df["POP_2026_EST"].sum())

    print("\nTop 10 highest-exposure habitations:")
    print(
        df.sort_values(
            by="POP_2026_EST",
            ascending=False,
        )[
            [
                "NAME",
                "LEVEL",
                "NO_HH",
                "POP_2011",
                "POP_2026_EST",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()