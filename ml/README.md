# RaceMind AI ML Model

This folder contains the machine learning part of RaceMind AI.

The ML pipeline trains a classifier that predicts a MotoGP rider performance class based on historical race result features.

---

## Goal

The model predicts one of three rider performance classes:

```txt
Strong
Average
Poor
```

---

## Target Rules

The target label is created from historical race results:

- `Strong`: finish position <= 3
- `Average`: finish position <= 10
- `Poor`: DNF, DNS, RET, DSQ, NC, missing finish position, or finish position > 10

---

## Features Used

The model uses:

```txt
year
event_name
circuit
rider
team
grid_position
session_type
```

`grid_position` is joined from qualifying data where available.

If `grid_position` is missing, the training and prediction pipeline uses a fallback value of `99`.

---

## Model

The project uses a scikit-learn `RandomForestClassifier` inside a pipeline with:

- `OneHotEncoder` for categorical features
- passthrough for numeric features
- `RandomForestClassifier` for classification

Numeric features:

```txt
year
grid_position
```

Categorical features:

```txt
event_name
circuit
rider
team
session_type
```

---

## Training

Run from the project root:

```bash
python ml/train_model.py
```

The script:

1. loads `data/processed/race_results_clean.csv`
2. creates the `performance_class` target
3. prepares numeric and categorical features
4. trains a RandomForestClassifier
5. evaluates the model
6. saves the model and metrics

---

## Outputs

After training, the script creates:

```txt
ml/model.pkl
ml/model_metrics.json
```

`model.pkl` contains the trained scikit-learn pipeline.

`model_metrics.json` contains:

- accuracy
- classification report
- confusion matrix
- class labels
- feature columns
- numeric features
- categorical features
- grouped feature importance
- detailed top feature importance
- target rules
- dataset rows used

---

## Prediction API

The backend serves predictions through:

```txt
POST /ml/predict
```

Example payload:

```json
{
  "year": 2025,
  "event_name": "QAT",
  "circuit": "QAT",
  "rider": "M. Marquez",
  "team": "Ducati Lenovo Team",
  "grid_position": 1,
  "session_type": "Race"
}
```

Example response:

```json
{
  "prediction": "Strong",
  "confidence": 0.814,
  "probabilities": {
    "Average": 0.1299,
    "Poor": 0.0561,
    "Strong": 0.814
  },
  "explanation": {
    "summary": "The model predicted Strong with 81% confidence...",
    "top_factors": [
      "team",
      "rider history",
      "session type",
      "event",
      "circuit"
    ],
    "important_features": [
      {
        "feature": "team",
        "importance": 0.3026
      }
    ],
    "model_note": "RandomForestClassifier trained on historical MotoGP results. This is not an official MotoGP forecast."
  }
}
```

---

## Model Explainability

The project includes lightweight model explainability based on RandomForest feature importance.

The training script saves two types of feature importance:

```txt
grouped
detailed_top_25
```

`grouped` aggregates one-hot encoded columns back into readable feature groups such as:

```txt
team
rider
session_type
event_name
circuit
year
grid_position
```

The prediction endpoint uses the grouped importance to return a readable explanation.

---

## Notes

This model is for portfolio and demo purposes.

It is not an official MotoGP prediction system and should not be interpreted as a real race forecasting model.
