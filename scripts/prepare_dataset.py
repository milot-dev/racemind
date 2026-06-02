from pathlib import Path
import re
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_PATH = PROCESSED_DIR / "race_results_clean.csv"

RACE_FILE = RAW_DIR / "Race.csv"
QUALIFYING_FILE = RAW_DIR / "Qualifying.csv"


DNF_STATUSES = {"DNF", "DNS", "DSQ", "NC", "RET", "RETIRED", "WITHDRAWN"}


def normalize_column_name(col: str) -> str:
    return (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
        .replace("/", "_")
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        normalized = normalize_column_name(col)
        if normalized in df.columns:
            return normalized
    return None


def parse_position(value):
    if pd.isna(value):
        return None

    text = str(value).strip().upper()

    if not text:
        return None

    if text in DNF_STATUSES:
        return None

    # Handles values like P1, 1st, 2nd, 3rd, 10th
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())

    return None


def normalize_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return None

    return text


def detect_status(row, finish_position_col: str | None, status_col: str | None):
    if status_col and pd.notna(row.get(status_col)):
        raw_status = str(row.get(status_col)).strip().upper()

        if raw_status in DNF_STATUSES:
            return raw_status

        if raw_status:
            return raw_status

    if finish_position_col and pd.notna(row.get(finish_position_col)):
        raw_pos = str(row.get(finish_position_col)).strip().upper()

        if raw_pos in DNF_STATUSES:
            return raw_pos

    return "Finished"


def standardize_race_results(race_df: pd.DataFrame) -> pd.DataFrame:
    race_df = normalize_columns(race_df)

    year_col = first_existing_column(race_df, ["year", "season"])
    series_col = first_existing_column(race_df, ["series", "class", "category"])
    event_col = first_existing_column(race_df, ["event_name", "event", "grand_prix", "gp", "race_name"])
    circuit_col = first_existing_column(race_df, ["circuit", "track", "venue"])
    rider_col = first_existing_column(race_df, ["rider", "rider_name", "name"])
    team_col = first_existing_column(race_df, ["team", "constructor", "bike_team"])
    finish_col = first_existing_column(race_df, ["finish_position", "position", "pos", "rank", "classified_position"])
    points_col = first_existing_column(race_df, ["points", "pts"])
    status_col = first_existing_column(race_df, ["status", "result_status", "classified", "time_retired"])
    number_col = first_existing_column(race_df, ["number", "rider_number", "no"])
    time_gap_col = first_existing_column(race_df, ["time_gap", "gap", "time"])

    missing_required = []
    for label, col in {
        "year": year_col,
        "series/class": series_col,
        "event": event_col,
        "rider": rider_col,
        "team": team_col,
        "finish position": finish_col,
        "points": points_col,
    }.items():
        if col is None:
            missing_required.append(label)

    if missing_required:
        raise ValueError(f"Missing required Race.csv columns: {missing_required}")

    clean = pd.DataFrame()

    clean["year"] = pd.to_numeric(race_df[year_col], errors="coerce").astype("Int64")
    clean["series"] = race_df[series_col].apply(normalize_text)
    clean["event_name"] = race_df[event_col].apply(normalize_text)
    clean["session_type"] = "Race"
    clean["circuit"] = race_df[circuit_col].apply(normalize_text) if circuit_col else clean["event_name"]
    clean["rider"] = race_df[rider_col].apply(normalize_text)
    clean["team"] = race_df[team_col].apply(normalize_text)

    clean["finish_position"] = race_df[finish_col].apply(parse_position)
    clean["points"] = pd.to_numeric(race_df[points_col], errors="coerce").fillna(0)

    clean["status"] = race_df.apply(
        lambda row: detect_status(row, finish_col, status_col),
        axis=1,
    )

    clean["number"] = race_df[number_col].apply(normalize_text) if number_col else None
    clean["time_gap"] = race_df[time_gap_col].apply(normalize_text) if time_gap_col else None

    return clean


def standardize_qualifying_results(qualifying_df: pd.DataFrame) -> pd.DataFrame:
    qualifying_df = normalize_columns(qualifying_df)

    year_col = first_existing_column(qualifying_df, ["year", "season"])
    series_col = first_existing_column(qualifying_df, ["series", "class", "category"])
    event_col = first_existing_column(qualifying_df, ["event_name", "event", "grand_prix", "gp", "race_name"])
    rider_col = first_existing_column(qualifying_df, ["rider", "rider_name", "name"])
    position_col = first_existing_column(
        qualifying_df,
        [
            "grid_position",
            "qualifying_position",
            "q_position",
            "position",
            "pos",
            "rank",
            "classified_position",
        ],
    )

    missing_required = []
    for label, col in {
        "year": year_col,
        "series/class": series_col,
        "event": event_col,
        "rider": rider_col,
        "qualifying position": position_col,
    }.items():
        if col is None:
            missing_required.append(label)

    if missing_required:
        raise ValueError(f"Missing required Qualifying.csv columns: {missing_required}")

    quali = pd.DataFrame()

    quali["year"] = pd.to_numeric(qualifying_df[year_col], errors="coerce").astype("Int64")
    quali["series"] = qualifying_df[series_col].apply(normalize_text)
    quali["event_name"] = qualifying_df[event_col].apply(normalize_text)
    quali["rider"] = qualifying_df[rider_col].apply(normalize_text)
    quali["grid_position"] = qualifying_df[position_col].apply(parse_position)

    return quali


def normalize_join_key(value):
    if pd.isna(value):
        return ""

    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.replace(".", "")
    return text


def add_join_keys(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["_year_key"] = df["year"].astype(str)
    df["_series_key"] = df["series"].apply(normalize_join_key)
    df["_event_key"] = df["event_name"].apply(normalize_join_key)
    df["_rider_key"] = df["rider"].apply(normalize_join_key)

    return df


def filter_motogp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "series" not in df.columns:
        return df

    return df[df["series"].astype(str).str.lower().str.contains("motogp", na=False)]


def main():
    if not RACE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {RACE_FILE}")

    if not QUALIFYING_FILE.exists():
        raise FileNotFoundError(f"Missing file: {QUALIFYING_FILE}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading raw files...")
    race_raw = pd.read_csv(RACE_FILE)
    qualifying_raw = pd.read_csv(QUALIFYING_FILE)

    print(f"Race.csv shape: {race_raw.shape}")
    print(f"Qualifying.csv shape: {qualifying_raw.shape}")

    print("\nStandardizing race results...")
    race_clean = standardize_race_results(race_raw)
    race_clean = filter_motogp(race_clean)

    print("\nStandardizing qualifying results...")
    qualifying_clean = standardize_qualifying_results(qualifying_raw)
    qualifying_clean = filter_motogp(qualifying_clean)

    print("\nJoining Race.csv with Qualifying.csv to populate grid_position...")

    race_with_keys = add_join_keys(race_clean)
    qualifying_with_keys = add_join_keys(qualifying_clean)

    qualifying_for_join = qualifying_with_keys[
        ["_year_key", "_series_key", "_event_key", "_rider_key", "grid_position"]
    ].drop_duplicates(
        subset=["_year_key", "_series_key", "_event_key", "_rider_key"]
    )

    merged = race_with_keys.merge(
        qualifying_for_join,
        on=["_year_key", "_series_key", "_event_key", "_rider_key"],
        how="left",
    )

    merged = merged.drop(columns=["_year_key", "_series_key", "_event_key", "_rider_key"])

    final_columns = [
        "year",
        "series",
        "event_name",
        "session_type",
        "circuit",
        "rider",
        "team",
        "grid_position",
        "finish_position",
        "points",
        "status",
        "number",
        "time_gap",
    ]

    for col in final_columns:
        if col not in merged.columns:
            merged[col] = None

    merged = merged[final_columns]

    merged.to_csv(OUTPUT_PATH, index=False)

    print("\nSaved clean dataset:")
    print(OUTPUT_PATH)

    print("\nSummary:")
    print(f"Rows: {len(merged)}")
    print(f"Years covered: {sorted(merged['year'].dropna().unique().tolist())}")
    print(f"Unique riders: {merged['rider'].nunique()}")
    print(f"Unique teams: {merged['team'].nunique()}")
    print(f"Unique events: {merged['event_name'].nunique()}")
    print("\nSession types:")
    print(merged["session_type"].value_counts(dropna=False))

    print("\nGrid position coverage:")
    total_rows = len(merged)
    grid_rows = merged["grid_position"].notna().sum()
    coverage = (grid_rows / total_rows * 100) if total_rows else 0
    print(f"Rows with grid_position: {grid_rows}/{total_rows} ({coverage:.2f}%)")

    print("\nMissing values:")
    print(merged.isna().sum())


if __name__ == "__main__":
    main()