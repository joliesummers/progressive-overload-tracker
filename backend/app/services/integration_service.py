from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
from .cache_service import CacheService, cached
from .bedrock_agent_service import BedrockAgentService
from .analysis_service import AnalysisService
from .report_service import ReportService
from .workout_storage_service import WorkoutStorageService
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation
from ..models.user import User
import logging
from functools import wraps
import traceback
import inspect
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
        self.analysis_service = AnalysisService(db)
        self.report_service = ReportService(db)
        
    @error_handler
    @cached("workout_analysis")
    async def process_workout(self, session_id: int, workout_text: str) -> Dict[str, Any]:
        """Process a workout through the entire pipeline"""
        try:
            logger.info(f"Processing workout for session {session_id}")
            logger.debug(f"Workout text: {workout_text}")
            
            # Get response from Bedrock
            response = await self.bedrock_service.invoke_agent(workout_text)
            logger.debug(f"Bedrock response: {response}")
            
            if not response or "structured_data" not in response:
                raise ValueError("Invalid response from Bedrock")
                
            structured_data = response["structured_data"]
            if "exercises" not in structured_data or not structured_data["exercises"]:
                raise ValueError("No exercises found in response")
            
            # Store the workout data
            logger.debug("Storing workout data")
            workout_storage = WorkoutStorageService(self.db)
            
            # Process each exercise
            exercises = []
            for exercise_data in structured_data["exercises"]:
                logger.debug(f"Processing exercise: {exercise_data}")
                
                # Store exercise data
                exercise = await workout_storage.store_exercise_data(
                    session_id=session_id,
                    name=exercise_data.get("name"),
                    movement_pattern=exercise_data.get("movement_pattern"),
                    num_sets=exercise_data.get("num_sets"),
                    reps=exercise_data.get("reps", []),  # Already an array
                    weight=exercise_data.get("weight", []),  # Already an array
                    rpe=exercise_data.get("rpe"),
                    tempo=exercise_data.get("tempo"),
                    total_volume=exercise_data.get("total_volume"),
                    notes=exercise_data.get("notes"),
                    equipment=exercise_data.get("equipment"),
                    difficulty=exercise_data.get("difficulty"),
                    estimated_duration=exercise_data.get("estimated_duration"),
                    rest_period=exercise_data.get("rest_period"),
                    muscle_activations=exercise_data.get("muscle_activations", [])
                )
                exercises.append(exercise)
            
            # Return the first exercise for now (maintaining backward compatibility)
            return exercises[0].to_dict() if exercises else None
            
        except Exception as e:
            logger.error(f"Error processing workout: {str(e)}")
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
    async def process_workout_stream(self, user_id: int, workout_text: str) -> Dict[str, Any]:
        """Process a workout through the entire pipeline"""
        try:
            logger.info(f"Processing workout for user {user_id}")
            logger.debug(f"Workout text: {workout_text}")
            
            # Parse workout with Bedrock
            logger.debug("Invoking Bedrock agent")
            response = await self.bedrock_service.invoke_agent(workout_text)
            logger.debug(f"Got response from Bedrock: {response}")
            
            if not response:
                raise ValueError("No response received from Bedrock agent")
            
            # Parse the response to get structured data and display message
            try:
                # First try to get structured_data directly from response
                if isinstance(response, dict):
                    structured_data = response.get("structured_data")
                    display_message = response.get("display_message", "")
                    
                # If not found, try to parse from message
                if not structured_data and isinstance(response.get("message"), str):
                    message = response["message"]
                    # Find the last JSON object in the message
                    json_start = message.rfind("{\n")
                    json_end = message.rfind("\n}") + 2
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = message[json_start:json_end]
                        logger.debug(f"Extracted JSON string: {json_str}")
                        parsed_data = json.loads(json_str)
                        structured_data = parsed_data.get("structured_data")
                        display_message = parsed_data.get("display_message", "")
                
                if not structured_data:
                    raise ValueError("No structured data found in response")
                    
                logger.debug(f"Extracted structured data: {structured_data}")
                logger.debug(f"Display message: {display_message}")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing response: {str(e)}")
                raise ValueError(f"Invalid response format from Bedrock agent: {str(e)}")
            
            # Store the workout data
            try:
                logger.debug("Creating workout session")
                workout_storage = WorkoutStorageService(self.db)
                session = workout_storage.create_workout_session(user_id)
                logger.debug(f"Created workout session with ID: {session.id}")
                
                # Store exercise and muscle activation data
                logger.debug("Storing exercise data with structured data")
                exercises = []
                for exercise_data in structured_data.get("exercises", []):
                    exercise = workout_storage.store_exercise_data(
                        session_id=session.id,
                        name=exercise_data.get("name"),
                        movement_pattern=exercise_data.get("movement_pattern"),
                        num_sets=exercise_data.get("sets", {}).get("count"),
                        reps=exercise_data.get("sets", {}).get("reps", []),  # Pass raw array
                        weight=exercise_data.get("sets", {}).get("weight", []),  # Pass raw array
                        rpe=exercise_data.get("sets", {}).get("rpe"),
                        tempo=exercise_data.get("sets", {}).get("tempo"),
                        total_volume=exercise_data.get("total_volume"),
                        notes=exercise_data.get("notes"),
                        equipment=exercise_data.get("metadata", {}).get("equipment"),
                        difficulty=exercise_data.get("metadata", {}).get("difficulty"),
                        estimated_duration=exercise_data.get("metadata", {}).get("estimated_duration"),
                        rest_period=exercise_data.get("metadata", {}).get("rest_period"),
                        muscle_activations=[
                            {
                                "muscle_name": m.get("muscle"),
                                "activation_level": m.get("level"),
                                "estimated_volume": m.get("volume")
                            }
                            for m in exercise_data.get("muscle_activations", [])
                        ]
                    )
                    exercises.append(exercise)
                
                # End the workout session
                logger.debug("Ending workout session")
                session = workout_storage.end_workout_session(session.id)
                logger.debug(f"Ended workout session: {session.id}")
                
                # Get muscle data
                logger.debug("Getting muscle volume data")
                volume_data = workout_storage.get_muscle_volume_data(timeframe="weekly", user_id=user_id)
                logger.debug(f"Got volume data: {volume_data}")
                
                logger.debug("Getting muscle tracking data")
                tracking_data = workout_storage.get_muscle_tracking(days=30, user_id=user_id)
                logger.debug(f"Got tracking data: {tracking_data}")
                
                logger.debug("Getting muscle activations")
                activations = []
                for exercise in exercises:
                    for muscle_activation in exercise.muscle_activations:
                        activations.append({
                            "muscle_name": muscle_activation.muscle_name,
                            "activation_level": muscle_activation.activation_level,
                            "estimated_volume": muscle_activation.estimated_volume
                        })
                logger.debug(f"Got activations: {activations}")
                
                # Return processed data
                result = {
                    "message": response["message"],  # Use the full message from Bedrock
                    "structured_data": structured_data,  # Include the full structured data
                    "muscle_data": {
                        "activations": activations,
                        "volume_data": volume_data,
                        "tracking_data": tracking_data
                    },
                    "exercise_id": exercises[0].id if exercises else None,
                    "workout_data": {
                        "session_id": session.id,
                        "display_message": display_message,
                        "exercises": [{"id": exercise.id, "name": exercise.name} for exercise in exercises]
                    },
                    "recommendations": None,  # TODO: Add recommendations based on volume data
                    "next_steps": None  # TODO: Add next steps based on tracking data
                }
                logger.debug(f"Final result: {result}")
                return result
                
            except Exception as e:
                logger.error(f"Error storing workout data: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            
        except Exception as e:
            logger.error(f"Error processing workout: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    @error_handler
    async def refresh_cache(self, user_id: int):
        """Refresh all cached data for a user"""
        await self.cache_service.clear_user_cache(user_id)
        await self.get_user_dashboard(user_id)
        
    @error_handler
    async def clear_user_cache(self, user_id: int):
        """Clear all cached data for a user"""
        await self.cache_service.clear_user_cache(user_id)
