# RaceMind AI

RaceMind AI is a full-stack GenAI and ML-powered MotoGP intelligence platform.

It analyzes real MotoGP race result data, compares riders, provides rider and race detail pages, answers racing questions using RAG, generates AI race commentary, and predicts rider performance using machine learning.

---

## Project Overview

RaceMind AI was built as an AI Engineering portfolio project.

The project demonstrates:

- data preprocessing
- backend API development with FastAPI
- dashboard analytics
- frontend integration with Next.js
- retrieval-augmented generation
- local vector search with sentence-transformers
- prompt engineering
- AI commentary generation
- classical machine learning
- model serving
- lightweight model explainability

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

Route:

```txt
/dashboard
```

### Riders Page

Browse all riders from the cleaned dataset.

Route:

```txt
/riders
```

Clicking a rider opens their dedicated profile page.

### Rider Profile Pages

Each rider profile shows:

- total points
- wins
- podiums
- DNFs
- team history
- yearly performance trends
- recent results

Route:

```txt
/rider/[name]
```

Example:

```txt
/rider/M.%20Marquez
```

### Races Page

Browse all available races from the cleaned dataset.

Route:

```txt
/races
```

Clicking a race opens its detail page.

### Race Detail Pages

Each race detail page shows:

- race/session summary
- podium
- team points
- full results table
- generated race summary

Route:

```txt
/race/[year]/[event]
```

Example:

```txt
/race/2025/QAT
```

### Rider Comparison

Compare two riders by:

- total points
- wins
- podiums
- top 10 finishes
- DNFs
- average finish
- consistency

Route:

```txt
/compare
```

### RAG Racing Assistant

Ask motorcycle racing questions grounded in a local knowledge base.

The assistant uses:

- local markdown knowledge base
- sentence-transformers embeddings
- cosine similarity retrieval
- local fallback answer
- optional OpenAI generation if an API key is configured

Example questions:

```txt
What is race pace?
Why is qualifying important in MotoGP?
Explain tire degradation.
What makes a rider consistent?
```

Route:

```txt
/assistant
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

Route:

```txt
/commentator
```

### ML Performance Predictor

Predict whether a rider performance will be:

```txt
Strong
Average
Poor
```

The model is trained on historical MotoGP race result features and returns:

- prediction
- confidence
- probability breakdown
- explanation summary
- top model factors
- feature importance

Route:

```txt
/predict
```

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
- sentence-transformers
- optional OpenAI API

### Data and ML

- Kaggle MotoGP Race Results dataset
- cleaned CSV data pipeline
- RandomForestClassifier
- OneHotEncoder
- model metrics saved as JSON
- lightweight feature-importance explanation

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

The project uses `Race.csv` and `Qualifying.csv`.

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
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── riders/page.tsx
│   │   │   ├── rider/[name]/page.tsx
│   │   │   ├── races/page.tsx
│   │   │   ├── race/[year]/[event]/page.tsx
│   │   │   ├── compare/page.tsx
│   │   │   ├── assistant/page.tsx
│   │   │   ├── commentator/page.tsx
│   │   │   └── predict/page.tsx
│   │   ├── components/
│   │   └── lib/api.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── services/
│   │       ├── data_service.py
│   │       ├── rag_service.py
│   │       ├── ai_service.py
│   │       └── ml_service.py
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   ├── raw/
│   │   ├── Race.csv
│   │   └── Qualifying.csv
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
│   ├── isle_of_man_tt.md
│   └── glossary.md
│
├── docs/
│   └── architecture.md
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
GET /races
GET /events
GET /dashboard
GET /stats/rider/{rider_name}
GET /stats/rider/{rider_name}/trends
GET /race/{year}/{event_name}
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

Expected files:

```txt
data/raw/Race.csv
data/raw/Qualifying.csv
```

Then run from the project root:

```bash
python scripts/inspect_dataset.py
python scripts/prepare_dataset.py
```

This creates:

```txt
data/processed/race_results_clean.csv
```

`grid_position` is populated by joining `Race.csv` with `Qualifying.csv` where matching rows are available.

---

## ML Training

Train the model from the project root:

```bash
python ml/train_model.py
```

This creates:

```txt
ml/model.pkl
ml/model_metrics.json
```

The model predicts:

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
grid_position
session_type
```

The prediction endpoint also returns a lightweight explanation based on RandomForest feature importance.

---

## RAG Assistant

RaceMind AI includes a retrieval-augmented generation assistant for MotoGP, motorcycle racing.

The assistant reads local markdown files from:

```txt
knowledge_base/
```

It uses:

- sentence-transformers
- local embeddings
- cosine similarity search
- source file reporting
- local fallback answer
- optional OpenAI generation if configured

Current RAG flow:

```txt
User question
→ local embedding
→ cosine similarity search
→ top knowledge base chunks
→ OpenAI answer or local fallback
→ answer with source files
```

---

## AI Commentary Generator

The commentary generator accepts:

- rider
- race
- scenario
- style
- duration seconds

It can use OpenAI if an API key is configured. Otherwise, it returns a local fallback commentary.

---

## Limitations

This is a portfolio MVP, not an official MotoGP prediction system.

Current limitations:

- no live MotoGP data integration
- no lap-time telemetry
- no official MotoGP API integration
- some grid positions may still be missing if raw dataset names do not match perfectly
- RAG uses local sentence-transformer embeddings and cosine similarity, not a persistent vector database
- the ML model is trained only on historical result-level data
- commentary does not verify official race facts unless provided in the prompt

---

## Portfolio Description

RaceMind AI is a full-stack GenAI and ML-powered MotoGP intelligence platform. It uses real MotoGP race results from Kaggle to provide rider analytics, race analytics, comparison dashboards, rider profile pages, race detail pages, a RAG-based racing assistant, AI-generated race commentary, and a machine learning performance predictor with lightweight explainability.

The project demonstrates practical AI engineering skills including data preprocessing, FastAPI backend development, Next.js frontend integration, retrieval-augmented generation, prompt engineering, classical ML modeling, model serving, and model explainability.
