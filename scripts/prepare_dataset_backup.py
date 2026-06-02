from pathlib import Path
import pandas as pd
import re

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "race_results_clean.csv"


NON_FINISH_STATUSES = {
    "DNF",
    "DNS",
    "DSQ",
    "NC",
    "RET",
    "RETIRED",
    "WITHDRAWN",
}


def clean_position(value):
    """
    Convert position values like:
    - "1"
    - "P1"
    - "1st"
    - "2nd"
    into integer values.

    If the value is DNF, DNS, RET, etc., return None.
    """
    if pd.isna(value):
        return None

    value_str = str(value).strip().upper()

    if value_str in NON_FINISH_STATUSES:
        return None

    # Remove common prefixes/suffixes
    value_str = value_str.replace("P", "")
    value_str = value_str.replace("ST", "")
    value_str = value_str.replace("ND", "")
    value_str = value_str.replace("RD", "")
    value_str = value_str.replace("TH", "")

    # Extract first number from the string
    match = re.search(r"\d+", value_str)

    if match:
        return int(match.group())

    return None


def detect_status(position_value):
    """
    Detect whether a rider finished or had a non-finish result.
    """
    if pd.isna(position_value):
        return "Unknown"

    value_str = str(position_value).strip().upper()

    if value_str in NON_FINISH_STATUSES:
        return value_str

    return "Finished"


def load_race_data():
    """
    Load Race.csv from data/raw.
    """
    race_file = RAW_DIR / "Race.csv"

    if not race_file.exists():
        raise FileNotFoundError(
            "Race.csv was not found in data/raw. "
            "Make sure the Kaggle dataset is downloaded and unzipped."
        )

    df = pd.read_csv(race_file)
    print(f"Loaded {race_file.name}")
    print(f"Original shape: {df.shape}")

    return df


def prepare_dataset():
    df = load_race_data()

    print("\nAvailable classes:")
    print(df["class"].value_counts(dropna=False))

    print("\nAvailable sessions:")
    print(df["session"].value_counts(dropna=False))

    # Filter only MotoGP for MVP
    df = df[df["class"].astype(str).str.lower() == "motogp"].copy()

    print("\nAfter filtering MotoGP only:")
    print(f"Shape: {df.shape}")

    # Create standardized schema
    clean_df = pd.DataFrame()

    clean_df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    clean_df["series"] = df["class"].astype(str).str.strip()
    clean_df["event_name"] = df["event"].astype(str).str.strip()
    clean_df["session_type"] = df["session"].astype(str).str.strip()
    clean_df["circuit"] = df["event"].astype(str).str.strip()

    clean_df["rider"] = df["rider"].astype(str).str.strip()
    clean_df["team"] = df["Team"].astype(str).str.strip()

    # Race.csv does not contain grid position, so we keep it empty for now.
    clean_df["grid_position"] = pd.NA

    clean_df["finish_position"] = df["pos."].apply(clean_position)
    clean_df["points"] = pd.to_numeric(df["pts"], errors="coerce").fillna(0)

    clean_df["status"] = df["pos."].apply(detect_status)

    # Optional useful columns
    clean_df["number"] = df["no"]
    clean_df["time_gap"] = df["time / gap"]

    # Clean empty strings
    clean_df = clean_df.replace("", pd.NA)

    # Remove rows with no rider name
    clean_df = clean_df.dropna(subset=["rider"])

    # Sort for readability
    clean_df = clean_df.sort_values(
        by=["year", "event_name", "session_type", "finish_position"],
        na_position="last"
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUTPUT_FILE, index=False)

    print("\nClean dataset saved successfully.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Final shape: {clean_df.shape}")

    print("\nSummary:")
    print(f"Rows: {len(clean_df)}")
    print(f"Years covered: {sorted(clean_df['year'].dropna().unique().tolist())}")
    print(f"Unique riders: {clean_df['rider'].nunique()}")
    print(f"Unique teams: {clean_df['team'].nunique()}")
    print(f"Unique events: {clean_df['event_name'].nunique()}")
    print(f"Session types: {clean_df['session_type'].unique().tolist()}")

    print("\nTop riders by total points:")
    print(
        clean_df.groupby("rider")["points"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    print("\nMissing values:")
    print(clean_df.isna().sum())


if __name__ == "__main__":
    prepare_dataset()