from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
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
    muscle_data: Optional[MuscleData] = None
    exercise_id: Optional[int] = None
    workout_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[List[str]] = None

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

async def stream_response(response_stream: AsyncGenerator) -> AsyncGenerator[bytes, None]:
    """Stream the response chunks"""
    try:
        async for chunk in response_stream:
            if chunk:
                # Log the chunk for debugging
                logger.debug(f"Processing chunk: {chunk}")
                
                # Ensure chunk has the correct structure
                if isinstance(chunk, dict):
                    # Already formatted chunks from Messages API
                    if "type" in chunk and chunk["type"] in ["message", "muscle_data", "error"]:
                        # Don't double-encode error messages
                        if chunk["type"] == "error":
                            yield json.dumps({"type": "error", "error": chunk["error"]}).encode() + b"\n"
                        else:
                            yield json.dumps(chunk).encode() + b"\n"
                    # Legacy format conversion
                    elif "completion" in chunk:
                        yield json.dumps({"type": "message", "message": chunk["completion"]}).encode() + b"\n"
                    elif "muscle_data" in chunk:
                        yield json.dumps({"type": "muscle_data", "muscle_data": chunk["muscle_data"]}).encode() + b"\n"
                    elif "error" in chunk:
                        yield json.dumps({"type": "error", "error": chunk["error"]}).encode() + b"\n"
                # String chunks (convert to message type)
                elif isinstance(chunk, str):
                    yield json.dumps({"type": "message", "message": chunk}).encode() + b"\n"
                
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        error_chunk = {"type": "error", "error": str(e)}
        yield json.dumps(error_chunk).encode() + b"\n"

@router.post("")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> StreamingResponse:
    """Chat endpoint that processes messages and returns streaming responses"""
    try:
        # TODO: Get actual user ID from auth. Using 1 for now.
        user_id = 1
        integration_service = IntegrationService(db)
        response_stream = integration_service.process_workout_stream(user_id, request.message)
        return StreamingResponse(
            stream_response(response_stream),
            media_type='text/event-stream'
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
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
