from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from ..models.database import get_db
from ..services.workout_storage_service import WorkoutStorageService
from ..models.exercise import WorkoutSession
from pydantic import BaseModel
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["workout"],
    responses={404: {"description": "Not found"}}
)

class StartWorkoutRequest(BaseModel):
    user_id: int

class WorkoutResponse(BaseModel):
    id: int
    message: str

class WorkoutSessionResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime | None
    total_volume: float | None

@router.post("/start", response_model=WorkoutResponse)
async def start_workout(request: StartWorkoutRequest, db: Session = Depends(get_db)):
    """Start a new workout session"""
    logger.debug(f"Starting workout session for user {request.user_id}")
    try:
        storage_service = WorkoutStorageService(db)
        session = storage_service.create_workout_session(request.user_id)
        logger.debug(f"Workout session started successfully: {session.id}")
        return WorkoutResponse(
            id=session.id,
            message="Workout session started successfully"
        )
    except Exception as e:
        logger.error(f"Error starting workout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end/{session_id}", response_model=Dict)
async def end_workout(session_id: int, db: Session = Depends(get_db)):
    """End a workout session"""
    logger.debug(f"Ending workout session {session_id}")
    try:
        storage_service = WorkoutStorageService(db)
        session = storage_service.end_workout_session(session_id)
        return {
            "message": "Workout session ended successfully",
            "session_id": session.id,
            "total_volume": session.total_volume,
            "duration": (session.end_time - session.start_time).total_seconds() / 60  # Duration in minutes
        }
    except Exception as e:
        logger.error(f"Error ending workout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-sessions/{user_id}", response_model=List[WorkoutSessionResponse])
async def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    """Get all workout sessions for a user"""
    logger.debug(f"Getting sessions for user {user_id}")
    try:
        storage_service = WorkoutStorageService(db)
        sessions = db.query(WorkoutSession).filter(WorkoutSession.user_id == user_id).all()
        logger.debug(f"Found {len(sessions)} sessions")
        return [
            WorkoutSessionResponse(
                id=session.id,
                start_time=session.start_time,
                end_time=session.end_time,
                total_volume=session.total_volume
            )
            for session in sessions
        ]
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
