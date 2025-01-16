from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from ..models.workout import WorkoutSession, Exercise, MuscleActivation
from ..models.database import get_db
from pydantic import BaseModel, Field
from ..models.exercise import MuscleTrackingStatus, MuscleVolumeData
import logging

logger = logging.getLogger(__name__)

# Create router with explicit configuration
logger.debug("Creating analytics router...")
router = APIRouter(
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/test", response_model=dict)
async def test_analytics():
    """Test endpoint to verify analytics router is working"""
    return {"status": "Analytics router is working"}

@router.get("/muscle-tracking", response_model=List[MuscleTrackingStatus])
async def get_muscle_tracking(db: Session = Depends(get_db)):
    """Get tracking data for all muscles worked in the past month"""
    try:
        # Calculate the date one month ago
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        
        # Query for distinct muscles and their most recent activation
        recent_activations = (
            db.query(
                MuscleActivation.muscle_name,
                func.max(Exercise.timestamp).label("last_trained")
            )
            .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
            .filter(Exercise.timestamp >= one_month_ago)
            .group_by(MuscleActivation.muscle_name)
            .all()
        )
        
        # Convert to response model
        tracking_status = []
        for muscle_name, last_trained in recent_activations:
            tracking_status.append(
                MuscleTrackingStatus(
                    muscle_name=muscle_name,
                    last_trained=last_trained,
                    days_since_last_trained=(datetime.utcnow() - last_trained).days
                )
            )
        
        return tracking_status
        
    except Exception as e:
        logger.error(f"Error in get_muscle_tracking: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving muscle tracking data")

@router.get("/muscle-volume", response_model=List[MuscleVolumeData])
async def get_muscle_volume(
    timeframe: str = Query(..., regex="^(weekly|monthly)$"),
    db: Session = Depends(get_db)
):
    """Get volume data for all muscles worked in the specified timeframe"""
    try:
        # Calculate the start date based on timeframe
        days = 7 if timeframe == "weekly" else 30
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query for muscle volumes aggregated by date
        volume_data = (
            db.query(
                MuscleActivation.muscle_name,
                cast(Exercise.timestamp, Date).label("date"),
                func.sum(
                    MuscleActivation.estimated_volume
                ).label("total_volume")
            )
            .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
            .filter(Exercise.timestamp >= start_date)
            .group_by(
                MuscleActivation.muscle_name,
                cast(Exercise.timestamp, Date)
            )
            .order_by(
                MuscleActivation.muscle_name,
                cast(Exercise.timestamp, Date).desc()
            )
            .all()
        )
        
        # Convert to response model
        return [
            MuscleVolumeData(
                muscle_name=muscle_name,
                total_volume=round(float(total_volume), 2),
                date=date
            )
            for muscle_name, date, total_volume in volume_data
        ]
        
    except Exception as e:
        logger.error(f"Error in get_muscle_volume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving muscle volume data"
        )

@router.get("/minimal-test", response_model=dict)
async def minimal_test():
    """Minimal test endpoint"""
    return {"message": "Minimal test endpoint working"}

@router.get("/test-volume", response_model=dict)
async def test_volume():
    """Simple test endpoint"""
    logger.debug("Received request for test volume endpoint")
    return {
        "message": "Volume test endpoint working",
        "timestamp": datetime.utcnow()
    }
