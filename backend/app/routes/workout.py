from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from ..models.database import get_db
from ..services.workout_storage_service import WorkoutStorageService
from ..services.integration_service import IntegrationService
from ..models.exercise import WorkoutSession, MuscleActivationLevel, Exercise, MuscleActivationData
from pydantic import BaseModel
from datetime import datetime
import logging
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["workouts"],
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
    end_time: Optional[datetime] = None
    total_volume: Optional[float] = None

class ExerciseRequest(BaseModel):
    session_id: int
    exercise_name: str
    movement_pattern: Optional[str] = None
    num_sets: Optional[int] = None
    reps: Optional[List[int]] = None
    weight: Optional[List[float]] = None
    rpe: Optional[float] = None
    tempo: Optional[str] = None
    total_volume: Optional[float] = None
    notes: Optional[str] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None
    rest_period: Optional[int] = None
    muscle_activations: List[MuscleActivationData]

class ExerciseResponse(BaseModel):
    id: int
    session_id: int
    name: str
    movement_pattern: Optional[str] = None
    notes: Optional[str] = None
    num_sets: Optional[int] = None
    reps: Optional[List[int]] = None
    weight: Optional[List[float]] = None
    rpe: Optional[float] = None
    tempo: Optional[str] = None
    total_volume: Optional[float] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None
    rest_period: Optional[int] = None
    muscle_activations: List[MuscleActivationData]

class WorkoutSummaryResponse(BaseModel):
    session_id: int
    start_time: datetime
    end_time: Optional[datetime]
    total_volume: float
    exercises: List[ExerciseResponse]

class ProcessWorkoutRequest(BaseModel):
    session_id: int
    workout_text: str

class ProcessWorkoutResponse(BaseModel):
    id: int
    session_id: int
    name: str
    movement_pattern: Optional[str] = None
    notes: Optional[str] = None
    num_sets: Optional[int] = None
    reps: List[int] = []
    weight: List[float] = []
    rpe: Optional[float] = None
    tempo: Optional[str] = None
    total_volume: Optional[float] = None
    equipment: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_duration: Optional[int] = None
    rest_period: Optional[int] = None
    muscle_activations: List[MuscleActivationData] = []

@router.post("/start", response_model=WorkoutSessionResponse)
async def start_workout(request: StartWorkoutRequest, db: Session = Depends(get_db)):
    """Start a new workout session"""
    try:
        storage_service = WorkoutStorageService(db)
        session = storage_service.create_workout_session(request.user_id)
        return WorkoutSessionResponse(
            id=session.id,
            start_time=session.start_time,
            end_time=session.end_time,
            total_volume=session.total_volume
        )
    except Exception as e:
        logger.error(f"Error starting workout session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=ProcessWorkoutResponse)
async def process_workout(
    request: ProcessWorkoutRequest,
    db: Session = Depends(get_db)
):
    """Process workout text through Bedrock and store results"""
    try:
        logger.debug(f"Processing workout for session {request.session_id}")
        logger.debug(f"Workout text: {request.workout_text}")
        
        # Process workout through integration service
        integration_service = IntegrationService(db)
        result = await integration_service.process_workout(request.session_id, request.workout_text)
        logger.debug(f"Got result from integration service: {result}")
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
        
    except Exception as e:
        logger.error(f"Error processing workout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end")
async def end_workout(
    request: Dict[str, int],
    db: Session = Depends(get_db)
):
    """End a workout session"""
    try:
        storage_service = WorkoutStorageService(db)
        session = await storage_service.end_workout_session(request["session_id"])
        return {"message": "Workout session ended successfully"}
    except Exception as e:
        logger.error(f"Error ending workout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end/{session_id}", response_model=Dict)
async def end_workout_legacy(session_id: int, db: Session = Depends(get_db)):
    """End a workout session (Legacy)"""
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

@router.post("/store-exercise", response_model=Dict)
async def store_exercise(request: ExerciseRequest, db: Session = Depends(get_db)):
    """Store exercise data"""
    logger.debug(f"Storing exercise data for session {request.session_id}")
    try:
        storage_service = WorkoutStorageService(db)
        exercise = storage_service.store_exercise_data(
            session_id=request.session_id,
            exercise_name=request.exercise_name,
            movement_pattern=request.movement_pattern,
            num_sets=request.num_sets,
            reps=request.reps,
            weight=request.weight,
            rpe=request.rpe,
            tempo=request.tempo,
            total_volume=request.total_volume,
            notes=request.notes,
            equipment=request.equipment,
            difficulty=request.difficulty,
            estimated_duration=request.estimated_duration,
            rest_period=request.rest_period,
            muscle_activations=request.muscle_activations
        )
        return {
            "message": "Exercise stored successfully",
            "exercise_id": exercise.id,
            "session_id": request.session_id
        }
    except Exception as e:
        logger.error(f"Error storing exercise: {str(e)}")
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

@router.get("/{session_id}/summary", response_model=WorkoutSummaryResponse)
async def get_workout_summary(session_id: int, db: Session = Depends(get_db)):
    """Get a summary of a workout session including all exercises"""
    logger.debug(f"Getting summary for workout session {session_id}")
    try:
        storage_service = WorkoutStorageService(db)
        
        # Get the session
        session = storage_service.get_workout_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Workout session not found")
        
        # Get all exercises for this session
        exercises = storage_service.get_session_exercises(session_id)
        
        # Calculate total volume
        total_volume = sum(ex.total_volume or 0 for ex in exercises)
        
        return WorkoutSummaryResponse(
            session_id=session.id,
            start_time=session.start_time,
            end_time=session.end_time,
            total_volume=total_volume,
            exercises=[ExerciseResponse(**ex.to_dict()) for ex in exercises]
        )
    except Exception as e:
        logger.error(f"Error getting workout summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exercises/{exercise_id}", response_model=Dict[str, Any])
async def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Get exercise details by ID"""
    try:
        storage_service = WorkoutStorageService(db)
        exercise = storage_service.get_exercise(exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return exercise.to_dict()
    except Exception as e:
        logger.error(f"Error getting exercise: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
