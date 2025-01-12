from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.user import User
from ..services.auth import get_current_user
from ..models.exercise import MuscleTrackingStatus
from datetime import datetime

router = APIRouter()

@router.get("/muscle-tracking", response_model=List[MuscleTrackingStatus])
async def get_muscle_tracking(current_user: User = Depends(get_current_user)):
    # TODO: Replace with actual data from the database
    # This is mock data for now
    mock_data = [
        {
            "muscle_name": "Chest",
            "last_workout": "2025-01-10",
            "recovery_status": "Recovered",
            "volume_trend": 5.2,
            "sets_last_week": 12
        },
        {
            "muscle_name": "Back",
            "last_workout": "2025-01-11",
            "recovery_status": "Recovering",
            "volume_trend": 3.8,
            "sets_last_week": 15
        },
        {
            "muscle_name": "Legs",
            "last_workout": "2025-01-09",
            "recovery_status": "Recovered",
            "volume_trend": 4.5,
            "sets_last_week": 18
        },
        {
            "muscle_name": "Shoulders",
            "last_workout": "2025-01-08",
            "recovery_status": "Recovered",
            "volume_trend": 2.9,
            "sets_last_week": 9
        }
    ]
    return mock_data
