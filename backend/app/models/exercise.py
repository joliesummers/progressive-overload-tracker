from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class MuscleTrackingStatus(BaseModel):
    """Model for tracking muscle training status"""
    muscle_name: str = Field(..., description="Name of the muscle")
    last_trained: datetime = Field(..., description="Last time this muscle was trained")
    days_since_last_trained: int = Field(..., description="Days since last trained")

    class Config:
        from_attributes = True

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

class MuscleVolumeData(BaseModel):
    """Model for muscle volume data"""
    muscle_name: str = Field(..., description="Name of the muscle")
    total_volume: float = Field(..., description="Total volume for the muscle in kg")
    date: datetime = Field(..., description="Date of the volume data")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

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
