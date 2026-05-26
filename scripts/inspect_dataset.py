from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")


def main():
    csv_files = list(RAW_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw.")
        print("Download the Kaggle dataset first and place the CSV files inside data/raw.")
        return

    print(f"Found {len(csv_files)} CSV file(s).")

    for file in csv_files:
        print("=" * 100)
        print(f"FILE: {file.name}")

        try:
            df = pd.read_csv(file)
        except Exception as e:
            print(f"Could not read {file.name}: {e}")
            continue

        print(f"\nShape: {df.shape}")

        print("\nColumns:")
        for col in df.columns:
            print(f"- {col}")

        print("\nFirst 5 rows:")
        print(df.head())

        print("\nMissing values:")
        print(df.isna().sum())


if __name__ == "__main__":
    main()