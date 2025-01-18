from pydantic import BaseModel, RootModel
from datetime import datetime
from typing import Optional, Dict, List

class MuscleTrackingResponse(BaseModel):
    id: int
    user_id: int
    muscle_name: str
    status: str
    last_trained: datetime
    total_volume: float
    exercise_count: int
    weekly_volume: float
    monthly_volume: float
    coverage_rating: str
    recovery_status: float
    week_start: datetime

    class Config:
        from_attributes = True  # This enables ORM mode

class MuscleVolumeResponse(BaseModel):
    muscle_name: str
    total_volume: float
    date: datetime
    week_start: datetime
    exercise_count: int

    class Config:
        from_attributes = True  # This enables ORM mode

class VolumeDataPoint(BaseModel):
    date: str
    volume: float

    class Config:
        from_attributes = True

class VolumeProgressionResponse(RootModel):
    root: Dict[str, List[VolumeDataPoint]]

    class Config:
        from_attributes = True
