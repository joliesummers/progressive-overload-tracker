from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .services.exercise_analysis import MockClaudeService, ExerciseAnalysis

app = FastAPI(title="Progressive Overload API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
claude_service = MockClaudeService()

class WorkoutInput(BaseModel):
    exercise_description: str
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    notes: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Welcome to Progressive Overload API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze/exercise")
async def analyze_exercise(workout: WorkoutInput) -> ExerciseAnalysis:
    """
    Analyze an exercise description to identify muscles worked and activation levels
    """
    try:
        analysis = await claude_service.analyze_exercise(workout.exercise_description)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment")
async def analyze_workout_sentiment(workout: WorkoutInput):
    """
    Analyze workout notes for sentiment
    """
    if not workout.notes:
        raise HTTPException(status_code=400, detail="Workout notes are required for sentiment analysis")
    
    try:
        sentiment = await claude_service.analyze_workout_sentiment(workout.notes)
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
