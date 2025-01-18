from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..models.progress import ProgressMetric, PerformanceAggregate, UserInsight, MetricType
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation
import logging
import json
import re

logger = logging.getLogger(__name__)

class OutputProcessingService:
    """Service for processing and analyzing workout data to generate insights and track progress"""
    
    def __init__(self, db: Session):
        self.db = db

    def update_progress_metrics(self, user_id: int, exercise_name: str, 
                              muscle_data: Dict[str, Any]) -> List[ProgressMetric]:
        """Update progress metrics based on new exercise data"""
        metrics = []
        
        # Calculate and store volume metric
        volume_metric = ProgressMetric(
            user_id=user_id,
            exercise_name=exercise_name,
            metric_type=MetricType.VOLUME,
            value=muscle_data.get("total_volume", 0.0)
        )
        metrics.append(volume_metric)
        
        # Store metrics for each primary muscle
        for muscle_name, activation_ratio in muscle_data.get("primary_muscles", []):
            muscle_metric = ProgressMetric(
                user_id=user_id,
                muscle_group=muscle_name,
                metric_type=MetricType.VOLUME,
                value=muscle_data["total_volume"] * activation_ratio
            )
            metrics.append(muscle_metric)
        
        self.db.add_all(metrics)
        self.db.commit()
        return metrics

    def aggregate_performance(self, user_id: int, days: int = 7) -> List[PerformanceAggregate]:
        """Aggregate performance data for the specified time period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all exercises in the period
        exercises = (
            self.db.query(Exercise)
            .join(WorkoutSession)
            .filter(
                WorkoutSession.user_id == user_id,
                Exercise.timestamp >= start_date
            )
            .all()
        )
        
        # Group by exercise name
        exercise_data: Dict[str, Dict] = {}
        for exercise in exercises:
            if exercise.name not in exercise_data:
                exercise_data[exercise.name] = {
                    "total_volume": 0.0,
                    "total_reps": 0,
                    "max_weight": 0.0,
                    "session_count": 0
                }
            
            data = exercise_data[exercise.name]
            data["total_volume"] += exercise.total_volume
            # Add other metrics as needed
            
        # Create aggregates
        aggregates = []
        for exercise_name, data in exercise_data.items():
            aggregate = PerformanceAggregate(
                user_id=user_id,
                exercise_name=exercise_name,
                period_start=start_date,
                period_end=datetime.utcnow(),
                total_volume=data["total_volume"],
                session_count=data["session_count"],
                total_reps=data["total_reps"],
                max_weight=data["max_weight"]
            )
            aggregates.append(aggregate)
        
        self.db.add_all(aggregates)
        self.db.commit()
        return aggregates

    def generate_insights(self, user_id: int) -> List[UserInsight]:
        """Generate insights based on user's workout data"""
        insights = []
        
        # Volume progression insight
        volume_metrics = (
            self.db.query(ProgressMetric)
            .filter(
                ProgressMetric.user_id == user_id,
                ProgressMetric.metric_type == MetricType.VOLUME
            )
            .order_by(ProgressMetric.timestamp.desc())
            .limit(10)
            .all()
        )
        
        if volume_metrics:
            recent_volume = volume_metrics[0].value
            avg_volume = sum(m.value for m in volume_metrics) / len(volume_metrics)
            
            if recent_volume > avg_volume * 1.1:  # 10% above average
                insight = UserInsight(
                    user_id=user_id,
                    category="progress",
                    insight_text=f"Your recent workout volume is 10% above your average - great progress!",
                    relevance_score=0.8
                )
                insights.append(insight)
        
        self.db.add_all(insights)
        self.db.commit()
        return insights

    def get_user_insights(self, user_id: int, limit: int = 5) -> List[UserInsight]:
        """Get the most relevant recent insights for a user"""
        return (
            self.db.query(UserInsight)
            .filter(
                UserInsight.user_id == user_id,
                UserInsight.expires_at.is_(None) | (UserInsight.expires_at > datetime.utcnow())
            )
            .order_by(
                UserInsight.relevance_score.desc(),
                UserInsight.generated_at.desc()
            )
            .limit(limit)
            .all()
        )

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        """Create a new workout session"""
        session = WorkoutSession(
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        return session

    def store_exercise_data(self, session_id: int, exercise_name: str, muscle_data: Dict[str, Any]) -> Exercise:
        """Store exercise data and muscle activations"""
        # Create exercise record
        exercise = Exercise(
            session_id=session_id,
            name=exercise_name.lower(),
            total_volume=muscle_data.get("total_volume", 0.0),
            timestamp=datetime.utcnow()
        )
        self.db.add(exercise)
        self.db.flush()  # Get exercise ID without committing

        # Store muscle activations
        activations = []
        
        # Primary muscles
        for muscle_name, activation_ratio in muscle_data.get("primary_muscles", []):
            activation = MuscleActivation(
                exercise_id=exercise.id,
                muscle_name=muscle_name.lower(),
                activation_level=activation_ratio,
                is_primary=True
            )
            activations.append(activation)
        
        # Secondary muscles
        for muscle_name, activation_ratio in muscle_data.get("secondary_muscles", []):
            activation = MuscleActivation(
                exercise_id=exercise.id,
                muscle_name=muscle_name.lower(),
                activation_level=activation_ratio,
                is_primary=False
            )
            activations.append(activation)

        if activations:
            self.db.add_all(activations)
        
        self.db.commit()
        return exercise

    def end_workout_session(self, session_id: int) -> WorkoutSession:
        """End a workout session"""
        session = self.db.query(WorkoutSession).get(session_id)
        if session:
            session.end_time = datetime.utcnow()
            self.db.commit()
        return session

    async def extract_muscle_data(self, response_text: str) -> Dict[str, Any]:
        """Extract muscle activation data from the Bedrock agent's response"""
        try:
            logger.debug(f"Extracting muscle data from response: {response_text}")
            
            # Try to find JSON object in text (it might be surrounded by other text)
            json_match = re.search(r'\{[^{]*"exercise"[^}]*\}', response_text)
            if not json_match:
                logger.error("No valid JSON found in response")
                return None
                
            # Parse the JSON
            data = json.loads(json_match.group())
            logger.debug(f"Parsed JSON data: {data}")
            
            # Extract exercise data
            exercise = data.get("exercise", {})
            sets = exercise.get("sets", {})
            
            # Initialize result structure
            muscle_data = {
                "primary_muscles": [],
                "secondary_muscles": [],
                "total_volume": exercise.get("total_volume", 0.0),
                "sets": sets.get("count", 0),
                "reps": sets.get("reps", 0),
                "weight": sets.get("weight", 0.0)
            }
            
            # Process muscle activations
            for activation in data.get("muscle_activations", []):
                muscle_name = activation.get("muscle_name")
                activation_level = activation.get("activation_level")
                volume_percentage = activation.get("estimated_volume", 0) / 100.0
                
                if activation_level == "PRIMARY":
                    muscle_data["primary_muscles"].append((muscle_name, volume_percentage))
                elif activation_level == "SECONDARY":
                    muscle_data["secondary_muscles"].append((muscle_name, volume_percentage))
                # We ignore TERTIARY muscles as they weren't in the original schema
            
            logger.debug(f"Final extracted muscle data: {muscle_data}")
            return muscle_data
            
        except Exception as e:
            logger.error(f"Error extracting muscle data: {str(e)}")
            logger.error(f"Response text that caused error: {response_text}")
            return None

    async def process_agent_output(self, agent_response: Any) -> Dict[str, Any]:
        """Process the output from the Bedrock agent"""
        try:
            logger.debug(f"Processing agent output: {agent_response}")
            
            # Handle AioEventStream response
            if hasattr(agent_response, '__aiter__'):
                completion_text = ""
                async for event in agent_response:
                    logger.debug(f"Processing event: {event}")
                    if "chunk" in event and "bytes" in event["chunk"]:
                        try:
                            chunk = json.loads(event["chunk"]["bytes"].decode())
                            if "completion" in chunk:
                                completion_text += chunk["completion"]
                        except json.JSONDecodeError:
                            logger.error(f"Failed to decode chunk: {event}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing chunk: {str(e)}")
                            continue
            else:
                completion_text = agent_response

            # Try to find and parse JSON in the response
            try:
                # Find JSON object in text (it might be surrounded by other text)
                json_match = re.search(r'\{[^{]*"exercise"[^}]*\}', completion_text)
                if json_match:
                    workout_data = json.loads(json_match.group())
                else:
                    logger.error("No valid JSON found in response")
                    return {}

                exercise_data = workout_data["exercise"]
                muscle_data = workout_data["muscle_activations"]

                # Convert to our internal format
                result = {
                    "exercise": {
                        "name": exercise_data["name"],
                        "movement_pattern": exercise_data["movement_pattern"],
                        "sets": exercise_data["sets"]["count"],
                        "reps": exercise_data["sets"]["reps"],
                        "weight": exercise_data["sets"]["weight"],
                        "total_volume": exercise_data["total_volume"],
                        "notes": exercise_data.get("notes", ""),
                        "rpe": exercise_data["sets"].get("rpe"),
                        "tempo": exercise_data["sets"].get("tempo")
                    },
                    "muscle_activations": [
                        {
                            "muscle_name": muscle["muscle_name"],
                            "activation_level": muscle["activation_level"],
                            "estimated_volume": muscle["estimated_volume"]
                        }
                        for muscle in muscle_data
                    ]
                }

                logger.debug(f"Processed workout data: {result}")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from response: {str(e)}")
                return {}
            except KeyError as e:
                logger.error(f"Missing required field in response: {str(e)}")
                return {}
            except Exception as e:
                logger.error(f"Error processing agent output: {str(e)}")
                return {}

        except Exception as e:
            logger.error(f"Error in process_agent_output: {str(e)}")
            return {}
