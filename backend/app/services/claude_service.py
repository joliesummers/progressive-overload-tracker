import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncGenerator
from .bedrock_agent_service import BedrockAgentService
from .workout_storage_service import WorkoutStorageService
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service for interacting with Claude AI assistant"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bedrock_service = BedrockAgentService()
        self.storage_service = WorkoutStorageService(db)
        
    async def process_workout(self, user_id: int, workout_text: str) -> Dict[str, Any]:
        """Process a workout through Claude with streaming response"""
        try:
            # Get streaming response from Bedrock
            response = await self.bedrock_service.invoke_agent_with_retry(workout_text)
            
            if not response:
                raise ValueError("No response received from Claude")
            
            # Extract exercise data
            exercise_data = await self._extract_exercise_data(response)
            
            if exercise_data:
                # Store exercise data
                session = self.storage_service.create_workout_session(user_id)
                exercise = self.storage_service.store_exercise_data(
                    session.id,
                    exercise_data["name"],
                    exercise_data["muscle_data"]
                )
                
                return {
                    "message": response,
                    "exercise_id": exercise.id,
                    "muscle_data": exercise_data["muscle_data"]
                }
            
            return {"message": response}
            
        except Exception as e:
            logger.error(f"Error processing workout: {str(e)}")
            raise
            
    async def _extract_exercise_data(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract exercise data from Claude's response"""
        try:
            # Extract exercise name
            name_match = re.search(r'Exercise:\s*([^\n]+)', text)
            if not name_match:
                return None
                
            exercise_name = name_match.group(1).strip()
            
            # Extract muscle data using Bedrock
            muscle_data = await self.bedrock_service._extract_muscle_data(text)
            
            if not muscle_data:
                return None
                
            return {
                "name": exercise_name,
                "muscle_data": muscle_data
            }
            
        except Exception as e:
            logger.error(f"Error extracting exercise data: {str(e)}")
            return None
