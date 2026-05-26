# RaceMind AI Architecture

RaceMind AI is a full-stack GenAI and ML-powered MotoGP intelligence platform.

It combines:

- MotoGP race result analytics
- Rider comparison
- Retrieval-Augmented Generation
- AI commentary generation
- machine learning performance prediction

---

## High-Level Architecture

```txt
User
 |
 v
Next.js Frontend
 |
 | REST API
 v
FastAPI Backend
 |
 |-----------------------------|-----------------------------|
 |                             |                             |
 v                             v                             v
Data Service              GenAI Services                 ML Service
 |                             |                             |
 v                             |                             v
Clean MotoGP CSV              |                      RandomForest Model
                               |
                               |---- RAG Assistant
                               |---- Commentary Generator
```

---

## Frontend

The frontend is built with:

- Next.js
- TypeScript
- Tailwind CSS
- Recharts

Frontend pages:

```txt
/
Landing page

/dashboard
MotoGP analytics dashboard

/compare
Rider comparison page

/assistant
RAG-based racing assistant

/commentator
AI commentary generator

/predict
ML performance predictor
```

The frontend communicates with the backend through REST API calls.

---

## Backend

The backend is built with:

- FastAPI
- Python
- pandas
- pydantic
- scikit-learn
- joblib
- optional OpenAI API integration

Backend endpoints:

```txt
GET /health
GET /riders
GET /events
GET /dashboard
GET /stats/rider/{rider_name}
GET /compare?rider_a=...&rider_b=...
POST /ai/chat
POST /ai/commentary
POST /ml/predict
```

---

## Data Layer

The project uses a cleaned MotoGP dataset stored at:

```txt
data/processed/race_results_clean.csv
```

The raw Kaggle files are stored locally in:

```txt
data/raw/
```

but they are not committed to GitHub.

The cleaned dataset contains fields such as:

```txt
year
series
event_name
session_type
circuit
rider
team
grid_position
finish_position
points
status
number
time_gap
```

---

## Data Service

The data service reads the cleaned CSV and provides analytics such as:

- total riders
- total events
- total teams
- years covered
- top points riders
- top winners
- podium leaders
- average finish leaders
- individual rider stats
- rider comparison insights

Main file:

```txt
backend/app/services/data_service.py
```

---

## RAG Assistant

The RAG assistant uses local markdown files as a simple knowledge base.

Knowledge base folder:

```txt
knowledge_base/
```

Files:

```txt
racing_concepts.md
motogp_basics.md
race_strategy.md
rider_profiles.md
glossary.md
```

For the MVP, retrieval uses keyword overlap over text chunks.

Flow:

```txt
Question
 |
 v
Load markdown files
 |
 v
Split into chunks
 |
 v
Score chunks by keyword overlap
 |
 v
Return answer with source files
```

If an OpenAI API key is available, the backend can generate a more natural answer using the retrieved context. If no API key is available, the app returns a useful local fallback answer.

Main file:

```txt
backend/app/services/rag_service.py
```

---

## Commentary Generator

The commentary generator creates MotoGP-style commentary from:

- rider
- race/event
- scenario
- style
- duration

Supported styles:

```txt
dramatic commentator
technical race engineer
documentary narrator
social media caption
beginner-friendly explanation
```

If an OpenAI API key is available, the app uses an LLM. If not, it returns a strong fallback commentary template.

Main file:

```txt
backend/app/services/ai_service.py
```

---

## Machine Learning Model

The ML model predicts a rider performance class:

```txt
Strong
Average
Poor
```

Target rules:

```txt
Strong  = finish_position <= 3
Average = finish_position <= 10
Poor    = DNF, DNS, RET, DSQ, NC, missing finish position, or finish_position > 10
```

Features used:

```txt
year
event_name
circuit
rider
team
session_type
```

The model is a scikit-learn pipeline with:

- OneHotEncoder for categorical features
- RandomForestClassifier for classification

Model files:

```txt
ml/train_model.py
ml/model.pkl
ml/model_metrics.json
```

Backend serving file:

```txt
backend/app/services/ml_service.py
```

---

## Important Limitations

This is a portfolio MVP, not an official MotoGP forecasting system.

Known limitations:

- The model does not use live race data.
- The current clean race dataset has missing grid positions.
- The RAG system uses keyword retrieval first, not embeddings.
- Commentary generation does not verify official race facts unless they are provided by the user.
- Predictions are based on historical results and simple features only.

---

## Future Improvements

Possible next upgrades:

1. Add vector embeddings for RAG.
2. Add ChromaDB or FAISS for semantic search.
3. Join qualifying data to fill grid positions.
4. Add model explainability and feature importance.
5. Add richer race history pages.
6. Add Isle of Man TT knowledge base.
7. Add user-uploaded CSV analysis.
8. Add text-to-speech commentary.
9. Deploy frontend and backend.
