from functools import lru_cache
from pathlib import Path
import pandas as pd
import math

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

    text_columns = [
        "series",
        "event_name",
        "session_type",
        "circuit",
        "rider",
        "team",
        "status",
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    return df


def get_all_riders():
    df = load_race_results()

    riders = df["rider"].dropna().astype(str).str.strip()

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
        events.append(
            {
                "year": int(row["year"]) if not pd.isna(row["year"]) else None,
                "event_name": row["event_name"],
                "circuit": row["circuit"],
                "label": (
                    f"{int(row['year'])} - {row['event_name']}"
                    if not pd.isna(row["year"])
                    else row["event_name"]
                ),
            }
        )

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
        "years_covered": sorted(
            [int(y) for y in df["year"].dropna().unique().tolist()]
        ),
        "total_rows": int(len(df)),
        "session_types": sorted(df["session_type"].dropna().unique().tolist()),
        "top_points_riders": [
            {"rider": row["rider"], "points": float(row["points"])}
            for _, row in top_points.iterrows()
        ],
        "top_winners": [
            {"rider": row["rider"], "wins": int(row["wins"])}
            for _, row in wins.iterrows()
        ],
        "podium_leaders": [
            {"rider": row["rider"], "podiums": int(row["podiums"])}
            for _, row in podiums.iterrows()
        ],
        "average_finish_leaders": [
            {
                "rider": row["rider"],
                "average_finish": round(float(row["average_finish"]), 2),
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
        return {"error": True, "message": f"No rider found matching '{rider_name}'."}

    finished_df = rider_df[rider_df["finish_position"].notna()].copy()

    actual_rider_name = rider_df["rider"].mode().iloc[0]

    wins = int((rider_df["finish_position"] == 1).sum())
    podiums = int(rider_df["finish_position"].between(1, 3, inclusive="both").sum())
    top_10s = int(rider_df["finish_position"].between(1, 10, inclusive="both").sum())

    dnfs = int(rider_df["status"].astype(str).str.upper().isin(DNF_STATUSES).sum())

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
        "average_finish": (
            round(float(finished_df["finish_position"].mean()), 2)
            if not finished_df.empty
            else None
        ),
        "average_grid": None,
        "total_points": float(rider_df["points"].sum()),
        "best_finish": (
            int(finished_df["finish_position"].min()) if not finished_df.empty else None
        ),
        "worst_finish": (
            int(finished_df["finish_position"].max()) if not finished_df.empty else None
        ),
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

    consistency_a = (
        stats_a["average_finish"] if stats_a["average_finish"] is not None else 999
    )
    consistency_b = (
        stats_b["average_finish"] if stats_b["average_finish"] is not None else 999
    )

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


def get_rider_trends(rider_name: str):
    df = load_race_results()

    rider_df = df[df["rider"].astype(str).str.lower() == rider_name.lower()].copy()

    if rider_df.empty:
        return {"error": f"Rider '{rider_name}' was not found."}

    rider_df["finish_position"] = pd.to_numeric(
        rider_df["finish_position"], errors="coerce"
    )

    rider_df["points"] = pd.to_numeric(rider_df["points"], errors="coerce").fillna(0)

    rider_df["grid_position"] = pd.to_numeric(
        rider_df["grid_position"], errors="coerce"
    )

    yearly = []

    for year, group in rider_df.groupby("year"):
        valid_finishes = group.dropna(subset=["finish_position"])

        avg_finish = (
            float(valid_finishes["finish_position"].mean())
            if not valid_finishes.empty
            else None
        )

        avg_grid = (
            float(group["grid_position"].mean())
            if group["grid_position"].notna().any()
            else None
        )

        yearly.append(
            {
                "year": int(year),
                "entries": int(len(group)),
                "wins": int((group["finish_position"] == 1).sum()),
                "podiums": int((group["finish_position"] <= 3).sum()),
                "top_10s": int((group["finish_position"] <= 10).sum()),
                "dnfs": int(
                    group["status"]
                    .astype(str)
                    .str.upper()
                    .isin(["DNF", "DNS", "RET", "DSQ", "NC", "RETIRED"])
                    .sum()
                ),
                "total_points": float(group["points"].sum()),
                "average_finish": to_json_safe(avg_finish),
                "average_grid": to_json_safe(avg_grid),
            }
        )

    yearly = sorted(yearly, key=lambda item: item["year"])

    team_history = (
        rider_df[["year", "team"]]
        .dropna()
        .drop_duplicates()
        .sort_values(["year", "team"])
        .to_dict(orient="records")
    )

    recent = rider_df.sort_values(["year", "event_name"], ascending=[False, True]).head(
        15
    )

    recent_results = recent[
        [
            "year",
            "event_name",
            "session_type",
            "team",
            "grid_position",
            "finish_position",
            "points",
            "status",
        ]
    ].copy()

    recent_results = recent_results.where(pd.notna(recent_results), None)

    recent_results = recent_results.to_dict(orient="records")

    # Final safety pass: remove any remaining NaN values
    for row in recent_results:
        for key, value in row.items():
            row[key] = to_json_safe(value)

    for row in team_history:
        for key, value in row.items():
            row[key] = to_json_safe(value)

    return {
        "rider": rider_df["rider"].iloc[0],
        "team_history": team_history,
        "yearly_trends": yearly,
        "recent_results": recent_results,
    }

def get_race_detail(year: int, event_name: str):
    df = load_race_results().copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["finish_position"] = pd.to_numeric(df["finish_position"], errors="coerce")
    df["grid_position"] = pd.to_numeric(df["grid_position"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)

    event_name_normalized = event_name.lower().replace("-", " ").strip()

    race_df = df[
        (df["year"] == year)
        & (
            df["event_name"]
            .astype(str)
            .str.lower()
            .str.replace("-", " ", regex=False)
            .str.contains(event_name_normalized, na=False)
        )
    ].copy()

    if race_df.empty:
        return {"error": f"No race data found for {year} {event_name}."}

    result_columns = [
        "year",
        "event_name",
        "session_type",
        "circuit",
        "rider",
        "team",
        "grid_position",
        "finish_position",
        "points",
        "status",
    ]

    results_df = race_df.sort_values(
        ["session_type", "finish_position"],
        na_position="last",
    )[result_columns].copy()

    results_df = results_df.where(pd.notna(results_df), None)
    results = results_df.to_dict(orient="records")

    for row in results:
        for key, value in row.items():
            row[key] = to_json_safe(value)

    podium_df = race_df[
        race_df["finish_position"].isin([1, 2, 3])
    ].sort_values("finish_position")

    podium_df = podium_df[
        [
            "finish_position",
            "rider",
            "team",
            "points",
            "session_type",
        ]
    ].copy()

    podium_df = podium_df.where(pd.notna(podium_df), None)
    podium = podium_df.to_dict(orient="records")

    for row in podium:
        for key, value in row.items():
            row[key] = to_json_safe(value)

    session_summary = []

    for session_type, group in race_df.groupby("session_type"):
        winner = (
            group.sort_values("finish_position").iloc[0]["rider"]
            if group["finish_position"].notna().any()
            else None
        )

        session_summary.append(
            {
                "session_type": to_json_safe(session_type),
                "entries": int(len(group)),
                "points_awarded": to_json_safe(float(group["points"].sum())),
                "winner": to_json_safe(winner),
            }
        )

    team_points_df = (
        race_df.groupby("team", dropna=True)["points"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"points": "total_points"})
    )

    team_points_df = team_points_df.where(pd.notna(team_points_df), None)
    team_points = team_points_df.to_dict(orient="records")

    for row in team_points:
        for key, value in row.items():
            row[key] = to_json_safe(value)

    event_display_name = to_json_safe(race_df["event_name"].iloc[0])

    circuit = (
        race_df["circuit"].dropna().iloc[0]
        if race_df["circuit"].notna().any()
        else None
    )
    circuit = to_json_safe(circuit)

    winner_rows = race_df[race_df["finish_position"] == 1]
    winners = winner_rows["rider"].dropna().unique().tolist()
    winners = [to_json_safe(winner) for winner in winners if to_json_safe(winner)]

    ai_summary = (
        f"The {year} {event_display_name} event included "
        f"{len(race_df)} recorded rider results across "
        f"{race_df['session_type'].nunique()} session type(s). "
    )

    if winners:
        ai_summary += f"Winner entries include: {', '.join(winners[:3])}. "

    ai_summary += "This summary is generated from the cleaned RaceMind AI dataset."

    return {
        "year": int(year),
        "event_name": event_display_name,
        "circuit": circuit,
        "results": results,
        "podium": podium,
        "session_summary": session_summary,
        "team_points": team_points,
        "ai_summary": ai_summary,
    }

def get_all_races():
    df = load_race_results().copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    race_columns = ["year", "event_name", "circuit"]

    races_df = (
        df[race_columns]
        .dropna(subset=["year", "event_name"])
        .drop_duplicates()
        .sort_values(["year", "event_name"], ascending=[False, True])
    )

    races = races_df.to_dict(orient="records")

    for row in races:
        for key, value in row.items():
            row[key] = to_json_safe(value)

        if row.get("year") is not None:
            row["year"] = int(row["year"])

    return {
        "races": races,
        "count": len(races),
    }