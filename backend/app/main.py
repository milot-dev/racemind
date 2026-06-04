from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services.rag_service import answer_question
from app.services.ai_service import generate_commentary
from app.services.ml_service import predict_performance

from app.models.schemas import ChatRequest, CommentaryRequest, PredictionRequest
from app.services.data_service import (
    get_all_riders,
    get_all_events,
    get_dashboard_summary,
    get_rider_stats,
    compare_riders,
    get_rider_trends,
    get_race_detail,
    get_all_races
)


app = FastAPI(
    title="RaceMind AI API",
    description="FastAPI backend for MotoGP analytics, GenAI, RAG, and ML prediction.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
         "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "RaceMind AI"
    }


@app.get("/riders")
def riders():
    return {
        "riders": get_all_riders()
    }


@app.get("/events")
def events():
    return {
        "events": get_all_events()
    }


@app.get("/dashboard")
def dashboard():
    return get_dashboard_summary()


@app.get("/stats/rider/{rider_name}")
def rider_stats(rider_name: str):
    return get_rider_stats(rider_name)


@app.get("/compare")
def compare(
    rider_a: str = Query(..., description="First rider name"),
    rider_b: str = Query(..., description="Second rider name"),
):
    return compare_riders(rider_a, rider_b)


@app.post("/ai/chat")
def ai_chat(request: ChatRequest):
    return answer_question(request.question)

@app.post("/ai/commentary")
def ai_commentary(request: CommentaryRequest):
    return generate_commentary(request)

@app.post("/ml/predict")
def ml_predict(request: PredictionRequest):
    return predict_performance(request)

@app.get("/stats/rider/{rider_name}/trends")
def rider_trends(rider_name: str):
    return get_rider_trends(rider_name)

@app.get("/race/{year}/{event_name}")
def race_detail(year: int, event_name: str):
    return get_race_detail(year, event_name)

@app.get("/races")
def races():
    return get_all_races()