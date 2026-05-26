# RaceMind AI ML Model

This folder contains the machine learning part of RaceMind AI.

## Goal

The model predicts a rider performance class:

- Strong
- Average
- Poor

## Target Rules

The target label is created from historical race results:

- `Strong`: finish position <= 3
- `Average`: finish position <= 10
- `Poor`: DNF, DNS, RET, DSQ, NC, missing finish position, or finish position > 10

## Features Used

The MVP model uses:

- year
- event_name
- circuit
- rider
- team
- session_type

`grid_position` is not used yet because the current cleaned Race.csv data has missing grid positions.

## Model

The MVP uses a scikit-learn `RandomForestClassifier` inside a pipeline with:

- `OneHotEncoder` for categorical features
- passthrough for year
- `RandomForestClassifier` for classification

## Outputs

After training, the script creates:

```txt
ml/model.pkl
ml/model_metrics.json