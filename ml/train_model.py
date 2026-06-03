from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "race_results_clean.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "model.pkl"
METRICS_PATH = PROJECT_ROOT / "ml" / "model_metrics.json"


DNF_STATUSES = {"DNF", "DNS", "RET", "DSQ", "NC", "RETIRED"}


def create_performance_class(row):
    """
    Creates the ML target label.

    Rules:
    - DNF/DNS/RET/DSQ/NC or missing finish position => Poor
    - finish_position <= 3 => Strong
    - finish_position <= 10 => Average
    - finish_position > 10 => Poor
    """
    status = str(row.get("status", "")).strip().upper()
    finish_position = row.get("finish_position")

    if status in DNF_STATUSES:
        return "Poor"

    if pd.isna(finish_position):
        return "Poor"

    try:
        finish_position = float(finish_position)
    except ValueError:
        return "Poor"

    if finish_position <= 3:
        return "Strong"

    if finish_position <= 10:
        return "Average"

    return "Poor"

def get_feature_importance(pipeline, numeric_features, categorical_features):
    model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]

    importances = model.feature_importances_

    transformed_feature_names = []

    transformed_feature_names.extend(numeric_features)

    encoder = preprocessor.named_transformers_["categorical"]
    encoded_names = encoder.get_feature_names_out(categorical_features)
    transformed_feature_names.extend(encoded_names)

    detailed = []

    for name, importance in zip(transformed_feature_names, importances):
        detailed.append({
            "feature": str(name),
            "importance": float(importance),
        })

    detailed = sorted(
        detailed,
        key=lambda item: item["importance"],
        reverse=True,
    )

    grouped = {}

    for item in detailed:
        feature_name = item["feature"]
        importance = item["importance"]

        if feature_name in numeric_features:
            group_name = feature_name
        else:
            group_name = feature_name

            for categorical_feature in categorical_features:
                prefix = f"{categorical_feature}_"
                if feature_name.startswith(prefix):
                    group_name = categorical_feature
                    break

        grouped[group_name] = grouped.get(group_name, 0.0) + importance

    grouped_list = [
        {
            "feature": feature,
            "importance": float(importance),
        }
        for feature, importance in grouped.items()
    ]

    grouped_list = sorted(
        grouped_list,
        key=lambda item: item["importance"],
        reverse=True,
    )

    return {
        "grouped": grouped_list,
        "detailed_top_25": detailed[:25],
    }

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Clean dataset not found at {DATA_PATH}. "
            "Run scripts/prepare_dataset.py first."
        )

    print("=" * 80)
    print("RaceMind AI — ML Training")
    print("=" * 80)

    df = pd.read_csv(DATA_PATH)

    print(f"Loaded dataset: {DATA_PATH}")
    print(f"Rows before cleaning: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    required_columns = [
        "year",
        "event_name",
        "circuit",
        "rider",
        "team",
        "session_type",
        "finish_position",
        "status",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["finish_position"] = pd.to_numeric(df["finish_position"], errors="coerce")

    if "grid_position" in df.columns:
        df["grid_position"] = pd.to_numeric(df["grid_position"], errors="coerce")
    else:
        df["grid_position"] = None

    df["performance_class"] = df.apply(create_performance_class, axis=1)

    # grid_position is currently empty in your dataset, so we drop it from features
    # to avoid training on a useless column.
    feature_columns = [
        "year",
        "event_name",
        "circuit",
        "rider",
        "team",
        "grid_position",
        "session_type",
    ]

    df_model = df[feature_columns + ["performance_class"]].copy()

    essential_features = [
        "year",
        "event_name",
        "rider",
        "team",
        "session_type",
    ]

    df_model = df_model.dropna(subset=essential_features)

    for col in ["event_name", "circuit", "rider", "team", "session_type"]:
        df_model[col] = df_model[col].fillna("Unknown").astype(str)

    df_model["year"] = df_model["year"].astype(int)

    df_model["grid_position"] = pd.to_numeric(
        df_model["grid_position"],
        errors="coerce"
    ).fillna(99)
    
    print(f"Rows after cleaning: {len(df_model)}")
    print("\nTarget distribution:")
    print(df_model["performance_class"].value_counts())

    X = df_model[feature_columns]
    y = df_model["performance_class"]

    test_size = 0.2

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
            stratify=y,
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
        )

    categorical_features = [
        "event_name",
        "circuit",
        "rider",
        "team",
        "session_type",
    ]

    numeric_features = ["year", "grid_position"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "numeric",
                "passthrough",
                numeric_features,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        max_depth=None,
        min_samples_leaf=2,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    print("\nTraining model...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)

    feature_importance = get_feature_importance(
        pipeline,
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    matrix = confusion_matrix(y_test, y_pred, labels=pipeline.classes_)

    metrics = {
        "accuracy": accuracy,
        "classes": list(pipeline.classes_),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "feature_columns": feature_columns,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "feature_importance": feature_importance,
        "target": "performance_class",
        "target_rules": {
            "Strong": "finish_position <= 3",
            "Average": "finish_position <= 10",
            "Poor": "DNF/DNS/RET/DSQ/NC/missing finish or finish_position > 10",
        },
        "dataset_rows_used": int(len(df_model)),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(pipeline, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print("\nTraining complete.")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\nConfusion matrix labels:")
    print(list(pipeline.classes_))

    print("\nConfusion matrix:")
    print(matrix)


if __name__ == "__main__":
    main()