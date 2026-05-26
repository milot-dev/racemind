from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str


class CommentaryRequest(BaseModel):
    rider: str
    race: str
    scenario: str
    style: str = "dramatic commentator"
    duration_seconds: Optional[int] = 45


class PredictionRequest(BaseModel):
    year: int
    event_name: str
    circuit: str
    rider: str
    team: str
    grid_position: Optional[int] = None
    session_type: str = "Race"