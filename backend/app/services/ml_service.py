from pathlib import Path
from functools import lru_cache
from typing import Any
import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "ml" / "model.pkl"


FEATURE_COLUMNS = [
    "year",
    "event_name",
    "circuit",
    "rider",
    "team",
    "session_type",
]


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        return None

    return joblib.load(MODEL_PATH)


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
        "session_type": input_data.session_type,
    }

    df = pd.DataFrame([row], columns=FEATURE_COLUMNS)

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

    return {
        "prediction": str(prediction),
        "confidence": confidence,
        "probabilities": probabilities,
        "input": row,
        "message": (
            "This is a simple ML prediction based on historical MotoGP results. "
            "It is for portfolio/demo purposes, not an official race forecast."
        ),
    }