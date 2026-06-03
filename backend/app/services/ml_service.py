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


def build_prediction_explanation(prediction: str, confidence: float) -> dict:
    metrics = load_model_metrics()

    importance_data = metrics.get("feature_importance", {})
    grouped_importance = importance_data.get("grouped", [])

    top_features = grouped_importance[:5]

    readable = []

    for item in top_features:
        feature = item.get("feature", "")

        if feature == "grid_position":
            readable.append("starting grid position")
        elif feature == "year":
            readable.append("season/year")
        elif feature == "rider":
            readable.append("rider history")
        elif feature == "team":
            readable.append("team")
        elif feature == "event_name":
            readable.append("event")
        elif feature == "circuit":
            readable.append("circuit")
        elif feature == "session_type":
            readable.append("session type")
        else:
            readable.append(feature)

    if not readable:
        readable = [
            "rider history",
            "team",
            "event",
            "session type",
            "starting grid position",
        ]

    return {
        "summary": (
            f"The model predicted {prediction} with {confidence:.0%} confidence. "
            f"The main historical factors considered were {', '.join(readable[:5])}. "
            "This explanation is based on RandomForest feature importance and is for portfolio/demo purposes."
        ),
        "top_factors": readable[:5],
        "important_features": top_features,
        "model_note": (
            "RandomForestClassifier trained on historical MotoGP results. "
            "This is not an official MotoGP forecast."
        ),
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
        prediction=str(prediction),
        confidence=confidence,
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