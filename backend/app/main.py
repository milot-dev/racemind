from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services.rag_service import answer_question

from app.models.schemas import ChatRequest, CommentaryRequest, PredictionRequest
from app.services.data_service import (
    get_all_riders,
    get_all_events,
    get_dashboard_summary,
    get_rider_stats,
    compare_riders,
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
    return {
        "commentary": (
            f"{request.rider} lines up the moment at {request.race}. "
            f"{request.scenario}. "
            "The pace, the pressure, and the racecraft all come together in a classic MotoGP-style performance."
        ),
        "style": request.style,
        "rider": request.rider
    }


@app.post("/ml/predict")
def ml_predict(request: PredictionRequest):
    return {
        "prediction": "Average",
        "confidence": 0.50,
        "probabilities": {
            "Strong": 0.25,
            "Average": 0.50,
            "Poor": 0.25
        },
        "note": "Temporary mock prediction. Train the ML model later to enable real predictions."
    }