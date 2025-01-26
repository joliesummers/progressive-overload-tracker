from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Dict, AsyncGenerator
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from ..models.exercise import (
    WorkoutSession, 
    Exercise, 
    MuscleActivation,
    MuscleTracking,
    MuscleVolumeData
)
from ..models.database import get_db
from ..schemas.muscle import MuscleTrackingResponse, MuscleVolumeResponse, VolumeProgressionResponse
from ..services.bedrock_agent_service import BedrockAgentService
from ..services.workout_storage_service import WorkoutStorageService
import logging
import json
import traceback

logger = logging.getLogger(__name__)

# Create router with explicit configuration
logger.debug("Creating analytics router...")
router = APIRouter(
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

# Initialize BedrockAgentService
bedrock_service = BedrockAgentService()

def get_storage_service(db: Session = Depends(get_db)) -> WorkoutStorageService:
    """Dependency to get WorkoutStorageService instance"""
    return WorkoutStorageService(db)

async def stream_response(response_stream: AsyncGenerator) -> AsyncGenerator[bytes, None]:
    """Stream the response chunks"""
    try:
        async for chunk in response_stream:
            if chunk:
                yield json.dumps(chunk).encode() + b"\n"
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        yield json.dumps({"error": str(e)}).encode()

@router.get("/test", response_model=dict)
async def test_analytics():
    """Test endpoint to verify analytics router is working"""
    return {"status": "Analytics router is working"}

@router.get("/muscle-tracking", response_model=List[MuscleTrackingResponse])
async def get_muscle_tracking(
    user_id: int = Query(..., description="User ID to get tracking data for"),
    storage_service: WorkoutStorageService = Depends(get_storage_service)
):
    """Get tracking data for all muscles worked in the past month"""
    try:
        logger.info(f"Getting muscle tracking data for user {user_id}")
        tracking_data = storage_service.get_muscle_tracking(user_id=user_id)
        logger.info(f"Found {len(tracking_data)} muscle tracking entries")
        return tracking_data
    except Exception as e:
        logger.error(f"Error getting muscle tracking data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/muscle-volume", response_model=List[MuscleVolumeResponse])
async def get_muscle_volume(
    user_id: int = Query(..., description="User ID to get volume data for"),
    timeframe: str = Query(..., regex="^(weekly|monthly)$"),
    storage_service: WorkoutStorageService = Depends(get_storage_service)
):
    """Get volume data for all muscles worked in the specified timeframe"""
    try:
        logger.info(f"Getting muscle volume data for user {user_id} with timeframe {timeframe}")
        volume_data = storage_service.get_muscle_volume_data(timeframe, user_id=user_id)
        logger.info(f"Found {len(volume_data)} volume data entries")
        return volume_data
    except Exception as e:
        logger.error(f"Error getting muscle volume data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/volume-progression", response_model=VolumeProgressionResponse)
async def get_volume_progression(
    user_id: int = Query(..., description="User ID to get progression data for"),
    timeframe: str = Query("weekly", description="Timeframe for progression analysis"),
    storage_service: WorkoutStorageService = Depends(get_storage_service)
):
    """Get progression data for muscle volume over time"""
    try:
        logger.info(f"Getting volume progression data for user {user_id} with timeframe {timeframe}")
        volume_data = storage_service.get_muscle_volume_data(timeframe, user_id=user_id)
        logger.info(f"Found {len(volume_data)} volume data entries")
        
        # Process the data for visualization
        progression_data = {}
        for entry in volume_data:
            if entry.muscle_name not in progression_data:
                progression_data[entry.muscle_name] = []
            progression_data[entry.muscle_name].append({
                "date": entry.date.isoformat(),
                "volume": entry.total_volume
            })
        
        logger.info(f"Processed data for {len(progression_data)} muscles")
        return progression_data
    except Exception as e:
        logger.error(f"Error getting volume progression data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/minimal")
async def minimal_test():
    """Minimal test endpoint"""
    return {"message": "Minimal test endpoint working"}

@router.get("/test/volume")
async def test_volume():
    """Simple test endpoint"""
    return {
        "message": "Test volume endpoint working",
        "data": {
            "chest": 1000,
            "back": 1200,
            "legs": 1500
        }
    }
