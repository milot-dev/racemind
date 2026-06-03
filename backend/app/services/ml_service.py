from pathlib import Path
from functools import lru_cache
from typing import Any
import joblib
import pandas as pd
import json


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "model.pkl"
METRICS_PATH = PROJECT_ROOT / "ml" / "model_metrics.json"

FEATURE_COLUMNS = [
    "year",
    "event_name",
    "circuit",
    "rider",
    "team",
    "grid_position",
    "session_type",
]


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        return None

    return joblib.load(MODEL_PATH)

@lru_cache(maxsize=1)
def load_model_metrics():
    if not METRICS_PATH.exists():
        return {}

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def build_prediction_explanation(input_data, prediction, confidence, probabilities):
    metrics = load_model_metrics()

    importance_data = metrics.get("feature_importance", {})

    if isinstance(importance_data, dict):
        feature_importance = importance_data.get("grouped", [])
    else:
        # Backward compatibility with old list format
        feature_importance = importance_data

    top_features = feature_importance[:5]

    readable_features = []

    for item in top_features:
        feature_name = item.get("feature", "")

        if feature_name == "rider" or feature_name.startswith("rider_"):
            readable_features.append("rider history")
        elif feature_name == "team" or feature_name.startswith("team_"):
            readable_features.append("team")
        elif feature_name == "event_name" or feature_name.startswith("event_name_"):
            readable_features.append("event")
        elif feature_name == "circuit" or feature_name.startswith("circuit_"):
            readable_features.append("circuit")
        elif feature_name == "session_type" or feature_name.startswith("session_type_"):
            readable_features.append("session type")
        elif feature_name == "grid_position":
            readable_features.append("grid position")
        elif feature_name == "year":
            readable_features.append("season/year")
        else:
            readable_features.append(feature_name)

    readable_features = list(dict.fromkeys(readable_features))

    if not readable_features:
        readable_features = [
            "rider history",
            "team",
            "event",
            "session type",
            "grid position",
        ]

    explanation_text = (
        f"The model predicted {prediction} with {confidence:.0%} confidence. "
        f"The main historical factors considered were "
        f"{', '.join(readable_features[:5])}. "
        f"The confidence score is based on RandomForest class probabilities. "
        f"This is a portfolio/demo prediction, not an official MotoGP forecast."
    )

    return {
        "summary": explanation_text,
        "top_factors": readable_features[:5],
        "model_note": "RandomForestClassifier trained on historical MotoGP race result features.",
        "important_features": top_features,
    }

def predict_performance(input_data: Any) -> dict:
    model = load_model()

    if model is None:
        return {
            "prediction": "Model not trained",
            "confidence": 0.0,
            "probabilities": {},
            "message": (
                "The ML model has not been trained yet. "
                "Run `python ml/train_model.py` from the project root first."
            ),
        }

    row = {
        "year": input_data.year,
        "event_name": input_data.event_name,
        "circuit": input_data.circuit,
        "rider": input_data.rider,
        "team": input_data.team,
        "grid_position": input_data.grid_position,
        "session_type": input_data.session_type,
    }

    df = pd.DataFrame([row], columns=FEATURE_COLUMNS)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(2025).astype(int)
    df["grid_position"] = pd.to_numeric(df["grid_position"], errors="coerce").fillna(99)

    for col in ["event_name", "circuit", "rider", "team", "session_type"]:
        df[col] = df[col].fillna("Unknown").replace("", "Unknown").astype(str)

    prediction = model.predict(df)[0]

    probabilities = {}
    confidence = 0.0

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(df)[0]
        classes = model.classes_

        probabilities = {
            str(label): round(float(prob), 4)
            for label, prob in zip(classes, proba)
        }

        confidence = round(float(max(proba)), 4)
    
    explanation = build_prediction_explanation(
        input_data=input_data,
        prediction=prediction,
        confidence=confidence,
        probabilities=probabilities
    )

    return {
        "prediction": str(prediction),
        "confidence": confidence,
        "probabilities": probabilities,
        "explanation": explanation,
        "input": df.iloc[0].to_dict(),
        "message": (
            "This is a simple ML prediction based on historical MotoGP results. "
            "It is for portfolio/demo purposes, not an official race forecast."
        ),
    }