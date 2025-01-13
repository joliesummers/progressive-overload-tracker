from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services import MockClaudeService, ExerciseAnalysis

router = APIRouter()
claude_service = MockClaudeService()

class WorkoutInput(BaseModel):
    exercise_description: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    notes: Optional[str] = None

@router.post("/analyze", response_model=ExerciseAnalysis)
async def analyze_exercise(workout: WorkoutInput):
    """
    Analyze an exercise description to identify muscles worked and activation levels
    """
    try:
        analysis = await claude_service.analyze_exercise(workout.exercise_description)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/sentiment")
async def analyze_workout_sentiment(workout: WorkoutInput):
    """
    Analyze workout notes for sentiment
    """
    try:
        sentiment = await claude_service.analyze_sentiment(workout.notes or "")
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
