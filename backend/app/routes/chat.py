from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, AsyncGenerator
from ..services.integration_service import IntegrationService
from ..services.bedrock_agent_service import BedrockAgentService
from ..services.workout_storage_service import WorkoutStorageService
from sqlalchemy.orm import Session
from ..models.database import get_db
from datetime import datetime
from ..models.user import User
import logging
import json
import traceback

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["chat"],
)

agent_service = BedrockAgentService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MuscleData(BaseModel):
    primary_muscles: List[tuple[str, float]]
    secondary_muscles: List[tuple[str, float]]
    total_volume: float

class ChatResponse(BaseModel):
    message: str
    display_message: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    muscle_data: Optional[Dict[str, Any]] = None
    exercise_id: Optional[int] = None
    workout_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    session_id: Optional[int] = None

async def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get or create a default user for testing"""
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Chat endpoint that processes messages and returns responses"""
    try:
        # TODO: Get actual user ID from auth. Using 1 for now.
        user_id = 1
        
        # Get workout data from Bedrock
        bedrock_service = BedrockAgentService()
        response = await bedrock_service.invoke_agent(request.message)
        
        if not response:
            raise ValueError("No response received from Bedrock agent")
        
        logger.debug(f"Raw response from Claude: {response}")
        
        # Parse the response
        structured_data = response.get("structured_data")
        display_message = response.get("display_message")
        
        if not structured_data:
            raise ValueError("No structured data found in response")
            
        logger.debug(f"Structured data: {structured_data}")
        logger.debug(f"Exercise data: {structured_data.get('exercise', {})}")
        logger.debug(f"Sets data: {structured_data.get('exercise', {}).get('sets', {})}")
        
        # Store workout data
        workout_storage = WorkoutStorageService(db)
        
        # Create and store session
        session = workout_storage.create_workout_session(user_id)
        
        # Store exercise data
        exercise = workout_storage.store_exercise_data(
            session_id=session.id,
            exercise_name="",  # This will be taken from structured_data
            muscle_data=structured_data
        )
        
        # End the session
        session = workout_storage.end_workout_session(session.id)
        
        # Get muscle data
        volume_data = workout_storage.get_muscle_volume_data(timeframe="weekly", user_id=user_id)
        tracking_data = workout_storage.get_muscle_tracking(days=30, user_id=user_id)
        activations = structured_data.get("muscle_activations", [])
        
        # Return response
        return ChatResponse(
            message=display_message or "Successfully processed your workout",
            structured_data=structured_data,
            muscle_data={
                "activations": activations,
                "volume_data": volume_data,
                "tracking_data": tracking_data
            },
            exercise_id=exercise.id if exercise else None,
            workout_data={
                "session_id": session.id,
                "display_message": display_message,
                "exercise": structured_data.get("exercise", {})
            }
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.options("")
async def chat_options():
    """Handle OPTIONS requests for CORS"""
    return {
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "true",
    }
