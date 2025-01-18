from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from ..models.database import get_db
from ..services.analysis_service import AnalysisService
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

class ProgressionResponse(BaseModel):
    current_value: float
    previous_value: float
    percent_change: float
    trend: str

class MuscleBalanceResponse(BaseModel):
    muscle_name: str
    total_volume: float
    relative_emphasis: float
    frequency: int
    last_trained: datetime

class FrequencyResponse(BaseModel):
    total_sessions: int
    average_frequency: float
    consistency_score: float
    days_tracked: int

@router.get("/progression/{exercise_name}", response_model=ProgressionResponse)
async def get_exercise_progression(
    exercise_name: str,
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get progressive overload metrics for a specific exercise"""
    analysis_service = AnalysisService(db)
    metrics = analysis_service.calculate_progressive_overload(1, exercise_name, days)  # TODO: Get real user_id
    
    if not metrics:
        raise HTTPException(status_code=404, detail="No data found for this exercise")
        
    return metrics

@router.get("/progression", response_model=Dict[str, ProgressionResponse])
async def get_all_progressions(
    days: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get progression metrics for all exercises"""
    analysis_service = AnalysisService(db)
    return analysis_service.analyze_volume_progression(1, days)  # TODO: Get real user_id

@router.get("/rest-periods", response_model=Dict[str, float])
async def get_rest_periods(
    exercise_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recommended rest periods for exercises"""
    analysis_service = AnalysisService(db)
    rest_periods = analysis_service.calculate_rest_periods(1, exercise_name)  # TODO: Get real user_id
    
    # Convert timedelta to days for API response
    return {
        name: period.days + (period.seconds / 86400)
        for name, period in rest_periods.items()
    }

@router.get("/muscle-balance", response_model=List[MuscleBalanceResponse])
async def get_muscle_balance(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get muscle balance analysis"""
    analysis_service = AnalysisService(db)
    return analysis_service.analyze_muscle_balance(1, days)  # TODO: Get real user_id

@router.get("/workout-frequency", response_model=FrequencyResponse)
async def get_workout_frequency(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get workout frequency analysis"""
    analysis_service = AnalysisService(db)
    return analysis_service.analyze_workout_frequency(1, days)  # TODO: Get real user_id
