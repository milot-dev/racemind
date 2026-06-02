# RaceMind AI

RaceMind AI is a full-stack GenAI and ML-powered MotoGP intelligence platform.

It analyzes real MotoGP race result data, compares riders, answers racing questions using RAG, generates AI race commentary, and predicts rider performance using machine learning.

---

## Project Overview

RaceMind AI was built as an AI Engineer portfolio project.

The project demonstrates:

- data preprocessing
- backend API development
- dashboard analytics
- frontend integration
- retrieval-augmented generation
- prompt engineering
- AI commentary generation
- classical machine learning
- model serving

---

## Features

### MotoGP Dashboard

Explore real MotoGP race result data with:

- total riders
- total events
- total teams
- years covered
- top points riders
- top winners
- podium leaders
- average finish leaders

### Rider Comparison

Compare two riders by:

- total points
- wins
- podiums
- top 10 finishes
- DNFs
- average finish
- consistency

### RAG Racing Assistant

Ask motorcycle racing questions grounded in a local knowledge base.

Example questions:

```txt
What is race pace?
Why is qualifying important in MotoGP?
Explain tire degradation.
What makes a rider consistent?
```

### AI Commentary Generator

Generate MotoGP-style commentary from a race scenario.

Supported styles:

```txt
dramatic commentator
technical race engineer
documentary narrator
social media caption
beginner-friendly explanation
```

### ML Performance Predictor

Predict whether a rider performance will be:

```txt
Strong
Average
Poor
```

The model is trained on historical MotoGP race result features.

---

## Tech Stack

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Recharts
- Fetch API

### Backend

- FastAPI
- Python
- pandas
- pydantic
- scikit-learn
- joblib
- optional OpenAI API

### Data and ML

- Kaggle MotoGP Race Results dataset
- cleaned CSV data pipeline
- RandomForestClassifier
- model metrics saved as JSON

---

## Dataset

This project uses the Kaggle dataset:

```txt
MotoGP Race Results (2022–2025)
Dataset slug: sammee/motogp-race-results-2022
```

Dataset link:

```txt
https://www.kaggle.com/datasets/sammee/motogp-race-results-2022
```

For the MVP, the dataset is cleaned and filtered mainly for MotoGP class analysis.

The processed dataset is stored at:

```txt
data/processed/race_results_clean.csv
```

The raw Kaggle files are not committed to GitHub.

---

## Project Structure

```txt
racemind_ai/
├── frontend/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── services/
│   │       ├── data_service.py
│   │       ├── ai_service.py
│   │       ├── rag_service.py
│   │       └── ml_service.py
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── race_results_clean.csv
│   └── README.md
│
├── scripts/
│   ├── inspect_dataset.py
│   └── prepare_dataset.py
│
├── ml/
│   ├── train_model.py
│   ├── model.pkl
│   ├── model_metrics.json
│   └── README.md
│
├── knowledge_base/
│   ├── racing_concepts.md
│   ├── motogp_basics.md
│   ├── race_strategy.md
│   ├── rider_profiles.md
│   └── glossary.md
│
├── docs/
│   ├── architecture.md
│ 
│   
│
├── README.md
└── .gitignore
```

---

## Architecture

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

More details are available in:

```txt
docs/architecture.md
```

---

## API Endpoints

### Health

```txt
GET /health
```

### Data and Analytics

```txt
GET /riders
GET /events
GET /dashboard
GET /stats/rider/{rider_name}
GET /compare?rider_a=...&rider_b=...
```

### GenAI

```txt
POST /ai/chat
POST /ai/commentary
```

### Machine Learning

```txt
POST /ml/predict
```

---

## Backend Setup

From the project root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run backend:

```bash
uvicorn app.main:app --reload
```

Backend docs:

```txt
http://localhost:8000/docs
```

---

## Frontend Setup

From the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```txt
http://localhost:3000
```

Create:

```txt
frontend/.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Dataset Preparation

Download the Kaggle dataset into:

```txt
data/raw/
```

Then run:

```bash
python scripts/inspect_dataset.py
python scripts/prepare_dataset.py
```

This creates:

```txt
data/processed/race_results_clean.csv
```

---

## ML Training

Install dependencies:

```bash
cd backend
pip install scikit-learn joblib
pip freeze > requirements.txt
```

Train the model from project root:

```bash
python ml/train_model.py
```

This creates:

```txt
ml/model.pkl
ml/model_metrics.json
```

---

## RAG Assistant

The RAG assistant uses markdown files from:

```txt
knowledge_base/
```

For the MVP, it uses keyword-based retrieval.

If `OPENAI_API_KEY` exists, it can use an LLM to generate answers from retrieved context.

If no API key exists, it returns a local fallback answer based on the best retrieved context.

---

## AI Commentary Generator

The commentary generator accepts:

- rider
- race
- scenario
- style
- duration seconds

It can use OpenAI if an API key is configured, otherwise it returns a high-quality local fallback commentary.

---

## ML Predictor

The ML model predicts:

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

`grid_position` is not used yet because it is missing in the current Race.csv-based cleaned dataset.

---

## Limitations

This is a portfolio MVP, not an official MotoGP prediction system.

Current limitations:

- no live MotoGP data integration
- no lap-time telemetry
- Some grid positions may still be missing because of naming differences between raw files.
- RAG uses keyword retrieval instead of embeddings
- model is simple and trained only on historical result-level data
- commentary does not verify official race facts unless provided in the prompt

---

## Future Improvements

Planned improvements:

1. Join qualifying data to fill grid positions.
2. Add vector embeddings for RAG.
3. Add ChromaDB or FAISS.
4. Add model explainability.
5. Add rider profile pages.
6. Add race detail pages.
7. Add Isle of Man TT knowledge base.
8. Add user-uploaded race CSV analysis.
9. Add text-to-speech commentary.
10. Deploy frontend and backend.

---

## Portfolio Description

RaceMind AI is a full-stack GenAI and ML-powered MotoGP intelligence platform. It uses real MotoGP race results from Kaggle to provide rider analytics, comparison dashboards, a RAG-based racing assistant, AI-generated race commentary, and a machine learning performance predictor.

The project demonstrates practical AI engineering skills including data preprocessing, FastAPI backend development, Next.js frontend integration, retrieval-augmented generation, prompt engineering, classical ML modeling, and model serving.
