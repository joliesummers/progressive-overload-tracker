from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from ..services.bedrock_agent_service import BedrockAgentService
from ..services.workout_storage_service import WorkoutStorageService
from sqlalchemy.orm import Session
from ..models.database import get_db
from datetime import datetime
from ..models.user import User
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()
agent_service = BedrockAgentService()

class ChatRequest(BaseModel):
    message: str

class MuscleData(BaseModel):
    primary_muscles: List[tuple[str, float]]
    secondary_muscles: List[tuple[str, float]]
    total_volume: float

class ChatResponse(BaseModel):
    message: str
    muscle_data: Optional[MuscleData] = None
    exercise_id: Optional[int] = None

def get_or_create_default_user(db: Session) -> User:
    """Get or create a default user for testing"""
    user = db.query(User).filter(User.username == "default").first()
    if not user:
        logger.info("Creating default user")
        user = User(username="default", email="default@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Send a message to the Bedrock agent and get a response with structured muscle data if available.
    Automatically stores muscle data in the database.
    """
    try:
        logger.info(f"Received chat request: {request.message}")
        
        # Get response from agent
        response = agent_service.invoke_agent_with_retry(request.message)
        logger.debug(f"Raw agent response: {response}")
        
        if not isinstance(response, dict):
            logger.warning(f"Unexpected response type from agent: {type(response)}")
            return ChatResponse(message=str(response))
            
        message = response.get('message', '')
        if not message:
            logger.error("Empty response from Bedrock agent")
            raise ValueError("Empty response from Bedrock agent")
            
        if 'muscle_data' in response:
            try:
                muscle_data = response['muscle_data']
                logger.info(f"Received muscle data: {muscle_data}")
                exercise_id = None
                
                # Store in database
                storage_service = WorkoutStorageService(db)
                
                # Get or create default user
                user = get_or_create_default_user(db)
                logger.debug(f"Using user ID: {user.id}")
                
                # Create a session for this workout
                session = storage_service.create_workout_session(user_id=user.id)
                logger.debug(f"Created workout session ID: {session.id}")
                
                # Try to extract exercise name from message
                try:
                    message_lower = request.message.lower()
                    exercise_name = None
                    
                    # Pattern 1: "... of X with ..."
                    if " of " in message_lower and " with " in message_lower:
                        exercise_name = message_lower.split(" of ")[1].split(" with ")[0].strip()
                        logger.debug(f"Extracted exercise name using pattern 1: {exercise_name}")
                    # Pattern 2: "X: ..."
                    elif ":" in message_lower:
                        exercise_name = message_lower.split(":")[0].strip()
                        logger.debug(f"Extracted exercise name using pattern 2: {exercise_name}")
                    # Pattern 3: First few words
                    else:
                        words = message_lower.split()
                        exercise_name = " ".join(words[:3])
                        logger.debug(f"Extracted exercise name using pattern 3: {exercise_name}")
                        
                    if not exercise_name:
                        logger.warning("Could not extract exercise name, using default")
                        exercise_name = "unnamed_exercise"
                        
                except Exception as e:
                    logger.error(f"Error extracting exercise name: {str(e)}")
                    exercise_name = "unnamed_exercise"
                
                # Store exercise data
                logger.info(f"Storing exercise: {exercise_name} with muscle data")
                exercise = storage_service.store_exercise_data(
                    session_id=session.id,
                    exercise_name=exercise_name,
                    muscle_data=muscle_data
                )
                exercise_id = exercise.id
                logger.debug(f"Stored exercise with ID: {exercise_id}")
                
                # End the workout session
                storage_service.end_workout_session(session.id)
                logger.debug(f"Ended workout session ID: {session.id}")
                
                return ChatResponse(
                    message=message,
                    muscle_data=MuscleData(**muscle_data),
                    exercise_id=exercise_id
                )
            except Exception as e:
                logger.error(f"Error processing muscle data: {str(e)}", exc_info=True)
                # Continue with basic response if muscle data processing fails
        
        return ChatResponse(message=message)
        
    except ValueError as e:
        # Known validation errors
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )
