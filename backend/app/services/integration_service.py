from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
from .cache_service import CacheService, cached
from .bedrock_agent_service import BedrockAgentService
from .output_processing_service import OutputProcessingService
from .analysis_service import AnalysisService
from .report_service import ReportService
from .workout_storage_service import WorkoutStorageService
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation
from ..models.user import User
import logging
from functools import wraps
import traceback
import inspect
import re
import json

logger = logging.getLogger(__name__)

def error_handler(func):
    """Decorator to handle errors in service methods"""
    if inspect.isasyncgenfunction(func):
        async def wrapper(*args, **kwargs):
            try:
                async for item in func(*args, **kwargs):
                    yield item
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(f"Exception type: {type(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                yield {"error": str(e)}
        return wrapper
    else:
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                logger.error(f"Exception type: {type(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise Exception(f"Internal service error: {str(e)}")
        return wrapper

class IntegrationService:
    """Service for integrating various components and handling cross-cutting concerns"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService()
        self.bedrock_service = BedrockAgentService()
        self.output_service = OutputProcessingService(db)
        self.analysis_service = AnalysisService(db)
        self.report_service = ReportService(db)
        
    @error_handler
    @cached("workout_analysis")
    async def process_workout(self, user_id: int, workout_text: str) -> Dict[str, Any]:
        """Process a workout through the entire pipeline"""
        try:
            logger.info(f"Processing workout for user {user_id}")
            logger.debug(f"Workout text: {workout_text}")
            
            # 1. Parse workout with Bedrock
            logger.debug("Invoking Bedrock agent")
            agent_response = await self.bedrock_service.invoke_agent_with_retry(workout_text)
            logger.debug(f"Got response from Bedrock: {agent_response}")
            
            if not agent_response:
                raise ValueError("No response received from Bedrock agent")
            
            # 2. Extract completion text and parse JSON
            completion_text = None
            if isinstance(agent_response, dict) and "content" in agent_response:
                for content in agent_response["content"]:
                    if content["type"] == "text":
                        completion_text = content["text"]
                        break
            
            if not completion_text:
                raise ValueError("No completion text found in agent response")
            
            # 3. Process the response to extract workout data
            logger.debug("Processing agent output")
            workout_data = await self.output_service.process_agent_output(completion_text)
            logger.debug(f"Processed workout data: {workout_data}")
            
            if not workout_data:
                raise ValueError("Failed to process workout data from agent response")
            
            # 4. Store the workout data
            logger.debug("Storing workout data")
            workout_storage = WorkoutStorageService(self.db)
            session = workout_storage.create_workout_session(user_id)
            
            # Get exercise data
            exercise_data = workout_data["exercise"]
            exercise = workout_storage.create_exercise(
                session.id,
                name=exercise_data["name"],
                movement_pattern=exercise_data["movement_pattern"],
                sets=exercise_data["sets"],
                reps=exercise_data["reps"],
                weight=exercise_data["weight"],
                total_volume=exercise_data["total_volume"],
                notes=exercise_data.get("notes", "")
            )
            
            # Store muscle activations
            for muscle in workout_data["muscle_activations"]:
                workout_storage.create_muscle_activation(
                    exercise.id,
                    muscle["muscle_name"],
                    muscle["activation_level"],
                    muscle["estimated_volume"]
                )
            
            # Return processed data
            return {
                "completion": completion_text,
                "workout_data": workout_data,
                "session_id": session.id
            }
            
        except Exception as e:
            logger.error(f"Error extracting muscle data: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    @error_handler
    @cached("user_dashboard", ttl=timedelta(minutes=30))
    async def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user dashboard data"""
        # Get progress report
        progress_report = self.report_service.generate_progress_report(user_id)
        
        # Get muscle balance
        muscle_balance = self.analysis_service.analyze_muscle_balance(user_id)
        
        # Get workout frequency
        frequency_data = self.analysis_service.analyze_workout_frequency(user_id)
        
        # Generate next steps
        next_steps = await self._generate_next_steps(user_id)
        
        return {
            "progress_report": progress_report,
            "muscle_balance": muscle_balance,
            "frequency_data": frequency_data,
            "next_steps": next_steps
        }
        
    @error_handler
    async def _generate_next_steps(self, user_id: int) -> List[str]:
        """Generate next steps based on user's current state"""
        try:
            # Get user's recent workouts
            recent_workouts = (
                self.db.query(WorkoutSession)
                .filter(WorkoutSession.user_id == user_id)
                .order_by(WorkoutSession.start_time.desc())
                .limit(5)
                .all()
            )
            
            if not recent_workouts:
                return ["Start your first workout to get personalized recommendations"]
                
            # Get user's muscle activations
            muscle_activations = (
                self.db.query(MuscleActivation)
                .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
                .join(WorkoutSession, Exercise.workout_session_id == WorkoutSession.id)
                .filter(WorkoutSession.user_id == user_id)
                .all()
            )
            
            # TODO: Use the Bedrock agent to generate personalized next steps
            # For now, return some basic recommendations
            return [
                "Continue with your current workout plan",
                "Focus on progressive overload",
                "Consider adding more variety to your exercises"
            ]
            
        except Exception as e:
            logger.error(f"Error generating next steps: {str(e)}")
            return ["Error generating recommendations"]
            
    @error_handler
    async def refresh_cache(self, user_id: int):
        """Refresh all cached data for a user"""
        await self.cache_service.clear_user_cache(user_id)
        await self.get_user_dashboard(user_id)
        
    @error_handler
    async def clear_user_cache(self, user_id: int):
        """Clear all cached data for a user"""
        await self.cache_service.clear_user_cache(user_id)
        
    @error_handler
    async def process_workout_stream(self, user_id: int, workout_text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a workout through the entire pipeline with streaming response"""
        try:
            logger.info(f"Processing workout stream for user {user_id}")
            logger.debug(f"Workout text: {workout_text}")
            
            # Parse workout with Bedrock
            logger.debug("Invoking Bedrock agent")
            async for chunk in self.bedrock_service.stream_agent_response(workout_text):
                logger.debug(f"Received chunk from Bedrock: {chunk}")
                
                # Handle errors
                if isinstance(chunk, dict):
                    if "error" in chunk:
                        logger.error(f"Error from Bedrock: {chunk['error']}")
                        yield chunk
                        continue
                        
                    if "type" in chunk:
                        if chunk["type"] == "message" and chunk.get("message"):
                            yield chunk
                            
                            # Try to extract muscle data from message
                            try:
                                muscle_data = await self.output_service.extract_muscle_data(chunk["message"])
                                if muscle_data:
                                    # Convert tuples to lists for JSON serialization
                                    formatted_data = {
                                        "primary_muscles": [{"muscle": m, "activation": a} for m, a in muscle_data["primary_muscles"]],
                                        "secondary_muscles": [{"muscle": m, "activation": a} for m, a in muscle_data["secondary_muscles"]],
                                        "total_volume": muscle_data["total_volume"],
                                        "sets": muscle_data["sets"],
                                        "reps": muscle_data["reps"],
                                        "weight": muscle_data["weight"]
                                    }
                                    yield {"type": "muscle_data", "muscle_data": formatted_data}
                            except Exception as e:
                                logger.error(f"Error extracting muscle data: {str(e)}")
                                
                        elif chunk["type"] == "muscle_data" and chunk.get("muscle_data"):
                            yield chunk
                        else:
                            logger.warning(f"Unknown chunk type: {chunk['type']}")
                            
                else:
                    logger.warning(f"Unknown chunk format: {chunk}")
                    yield {"type": "message", "message": str(chunk)}
                    
        except Exception as e:
            logger.error(f"Error in workout stream: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield {"type": "error", "error": str(e)}
