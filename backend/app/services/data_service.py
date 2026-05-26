from functools import lru_cache
from pathlib import Path
import pandas as pd

from app.config import DATA_PATH


DNF_STATUSES = {"DNF", "DNS", "DSQ", "NC", "RET", "RETIRED", "WITHDRAWN"}


def to_json_safe(value):
    """
    Convert pandas/numpy values into JSON-safe Python values.
    """
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


@lru_cache(maxsize=1)
def load_race_results() -> pd.DataFrame:
    """
    Load the cleaned MotoGP race results CSV.
    The result is cached so every API request does not reload the file.
    """
    path = Path(DATA_PATH)

    if not path.exists():
        raise FileNotFoundError(
            f"Clean dataset not found at: {path}. "
            "Run python scripts/prepare_dataset.py from the project root first."
        )

    df = pd.read_csv(path)

    numeric_columns = ["year", "grid_position", "finish_position", "points", "number"]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    text_columns = ["series", "event_name", "session_type", "circuit", "rider", "team", "status"]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def get_all_riders():
    df = load_race_results()

    riders = (
        df["rider"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    riders = sorted(riders[riders != ""].unique().tolist())

    return riders


def get_all_events():
    df = load_race_results()

    events_df = (
        df[["year", "event_name", "circuit"]]
        .drop_duplicates()
        .sort_values(["year", "event_name"])
    )

    events = []

    for _, row in events_df.iterrows():
        events.append({
            "year": int(row["year"]) if not pd.isna(row["year"]) else None,
            "event_name": row["event_name"],
            "circuit": row["circuit"],
            "label": f"{int(row['year'])} - {row['event_name']}" if not pd.isna(row["year"]) else row["event_name"]
        })

    return events


def get_dashboard_summary():
    df = load_race_results()

    finished_df = df[df["finish_position"].notna()].copy()

    top_points = (
        df.groupby("rider", as_index=False)["points"]
        .sum()
        .sort_values("points", ascending=False)
        .head(10)
    )

    wins = (
        df[df["finish_position"] == 1]
        .groupby("rider", as_index=False)
        .size()
        .rename(columns={"size": "wins"})
        .sort_values("wins", ascending=False)
        .head(10)
    )

    podiums = (
        df[df["finish_position"].between(1, 3, inclusive="both")]
        .groupby("rider", as_index=False)
        .size()
        .rename(columns={"size": "podiums"})
        .sort_values("podiums", ascending=False)
        .head(10)
    )

    average_finish = (
        finished_df.groupby("rider", as_index=False)["finish_position"]
        .mean()
        .rename(columns={"finish_position": "average_finish"})
        .sort_values("average_finish", ascending=True)
        .head(10)
    )

    return {
        "total_riders": int(df["rider"].nunique()),
        "total_events": int(df[["year", "event_name"]].drop_duplicates().shape[0]),
        "total_teams": int(df["team"].nunique()),
        "years_covered": sorted([int(y) for y in df["year"].dropna().unique().tolist()]),
        "total_rows": int(len(df)),
        "session_types": sorted(df["session_type"].dropna().unique().tolist()),
        "top_points_riders": [
            {
                "rider": row["rider"],
                "points": float(row["points"])
            }
            for _, row in top_points.iterrows()
        ],
        "top_winners": [
            {
                "rider": row["rider"],
                "wins": int(row["wins"])
            }
            for _, row in wins.iterrows()
        ],
        "podium_leaders": [
            {
                "rider": row["rider"],
                "podiums": int(row["podiums"])
            }
            for _, row in podiums.iterrows()
        ],
        "average_finish_leaders": [
            {
                "rider": row["rider"],
                "average_finish": round(float(row["average_finish"]), 2)
            }
            for _, row in average_finish.iterrows()
        ],
    }


def find_rider_rows(rider_name: str) -> pd.DataFrame:
    df = load_race_results()

    rider_name_lower = rider_name.strip().lower()

    exact_match = df[df["rider"].str.lower() == rider_name_lower]

    if not exact_match.empty:
        return exact_match

    partial_match = df[df["rider"].str.lower().str.contains(rider_name_lower, na=False)]

    return partial_match


def get_rider_stats(rider_name: str):
    rider_df = find_rider_rows(rider_name)

    if rider_df.empty:
        return {
            "error": True,
            "message": f"No rider found matching '{rider_name}'."
        }

    finished_df = rider_df[rider_df["finish_position"].notna()].copy()

    actual_rider_name = rider_df["rider"].mode().iloc[0]

    wins = int((rider_df["finish_position"] == 1).sum())
    podiums = int(rider_df["finish_position"].between(1, 3, inclusive="both").sum())
    top_10s = int(rider_df["finish_position"].between(1, 10, inclusive="both").sum())

    dnfs = int(
        rider_df["status"]
        .astype(str)
        .str.upper()
        .isin(DNF_STATUSES)
        .sum()
    )

    best_event = None

    if not finished_df.empty:
        best_row = finished_df.sort_values("finish_position").iloc[0]
        best_event = {
            "year": int(best_row["year"]),
            "event_name": best_row["event_name"],
            "session_type": best_row["session_type"],
            "finish_position": int(best_row["finish_position"]),
        }

    return {
        "rider": actual_rider_name,
        "team_names": sorted(rider_df["team"].dropna().unique().tolist()),
        "total_entries": int(len(rider_df)),
        "race_entries": int((rider_df["session_type"].str.lower() == "race").sum()),
        "sprint_entries": int((rider_df["session_type"].str.lower() == "sprint").sum()),
        "wins": wins,
        "podiums": podiums,
        "top_10s": top_10s,
        "dnfs": dnfs,
        "average_finish": round(float(finished_df["finish_position"].mean()), 2) if not finished_df.empty else None,
        "average_grid": None,
        "total_points": float(rider_df["points"].sum()),
        "best_finish": int(finished_df["finish_position"].min()) if not finished_df.empty else None,
        "worst_finish": int(finished_df["finish_position"].max()) if not finished_df.empty else None,
        "best_event": best_event,
    }


def compare_riders(rider_a: str, rider_b: str):
    stats_a = get_rider_stats(rider_a)
    stats_b = get_rider_stats(rider_b)

    if stats_a.get("error"):
        return stats_a

    if stats_b.get("error"):
        return stats_b

    def higher(metric, lower_is_better=False):
        value_a = stats_a.get(metric)
        value_b = stats_b.get(metric)

        if value_a is None and value_b is None:
            return "tie"

        if value_a is None:
            return stats_b["rider"]

        if value_b is None:
            return stats_a["rider"]

        if value_a == value_b:
            return "tie"

        if lower_is_better:
            return stats_a["rider"] if value_a < value_b else stats_b["rider"]

        return stats_a["rider"] if value_a > value_b else stats_b["rider"]

    insights = {
        "higher_points": higher("total_points"),
        "more_wins": higher("wins"),
        "more_podiums": higher("podiums"),
        "better_average_finish": higher("average_finish", lower_is_better=True),
        "fewer_dnfs": higher("dnfs", lower_is_better=True),
    }

    consistency_a = stats_a["average_finish"] if stats_a["average_finish"] is not None else 999
    consistency_b = stats_b["average_finish"] if stats_b["average_finish"] is not None else 999

    if consistency_a == consistency_b:
        more_consistent = "tie"
    elif consistency_a < consistency_b:
        more_consistent = stats_a["rider"]
    else:
        more_consistent = stats_b["rider"]

    insights["more_consistent_rider"] = more_consistent

    return {
        "rider_a": stats_a,
        "rider_b": stats_b,
        "insights": insights,
    }