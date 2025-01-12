from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class MuscleTrackingStatus(BaseModel):
    muscle_name: str
    last_workout: str  # ISO format date string
    recovery_status: str  # "Recovered" | "Recovering" | "Fatigued"
    volume_trend: float
    sets_last_week: int

class Exercise(BaseModel):
    exercise_name: str
    muscle_activations: List['MuscleActivation']
    movement_pattern: str
    equipment_needed: List[str]
    notes: Optional[str] = None

class MuscleActivation(BaseModel):
    muscle_name: str
    activation_level: str  # "PRIMARY" | "SECONDARY" | "TERTIARY"
    estimated_volume: float

class WorkoutSet(BaseModel):
    exercise: Exercise
    sets: int
    reps: int
    weight: Optional[float] = None
    rpe: Optional[float] = None
    tempo: Optional[str] = None
    notes: Optional[str] = None

class WorkoutSession(BaseModel):
    id: str
    date: date
    sets: List[WorkoutSet]
    sentiment_score: Optional[float] = None
    sentiment_analysis: Optional[str] = None
    notes: Optional[str] = None

Exercise.model_rebuild()  # This is needed because of the forward reference to MuscleActivation
