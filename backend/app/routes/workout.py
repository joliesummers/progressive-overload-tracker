from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..models.database import get_db
from ..services.workout_storage_service import WorkoutStorageService
from pydantic import BaseModel

router = APIRouter()

class StartWorkoutRequest(BaseModel):
    user_id: int

class WorkoutResponse(BaseModel):
    id: int
    message: str

@router.post("/start", response_model=WorkoutResponse)
async def start_workout(request: StartWorkoutRequest, db: Session = Depends(get_db)):
    """Start a new workout session"""
    try:
        storage_service = WorkoutStorageService(db)
        session = storage_service.create_workout_session(request.user_id)
        return WorkoutResponse(
            id=session.id,
            message="Workout session started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end/{session_id}", response_model=Dict)
async def end_workout(session_id: int, db: Session = Depends(get_db)):
    """End a workout session"""
    try:
        storage_service = WorkoutStorageService(db)
        storage_service.end_workout_session(session_id)
        return {"message": f"Workout session {session_id} ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
