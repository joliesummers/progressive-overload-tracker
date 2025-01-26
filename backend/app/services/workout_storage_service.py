from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
from ..models.exercise import (
    Exercise,
    WorkoutSession,
    MuscleActivation,
    MuscleActivationLevel
)
import logging
import json
import traceback
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class WorkoutStorageService:
    """Service for storing workout data in the database"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        """Create a new workout session"""
        try:
            session = WorkoutSession(
                user_id=user_id,
                start_time=datetime.now(),
                total_volume=0
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating workout session: {str(e)}")
            raise

    def get_workout_session(self, session_id: int) -> Optional[WorkoutSession]:
        """Get a workout session by ID"""
        try:
            return self.db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        except Exception as e:
            logger.error(f"Error getting workout session: {str(e)}")
            return None

    def get_session_exercises(self, session_id: int) -> List[Exercise]:
        """Get all exercises for a workout session"""
        try:
            exercises = self.db.query(Exercise).filter(Exercise.session_id == session_id).all()
            # Load relationships
            for exercise in exercises:
                _ = exercise.muscle_activations
            return exercises
        except Exception as e:
            logger.error(f"Error getting session exercises: {str(e)}")
            return []

    def end_workout_session(self, session_id: int) -> WorkoutSession:
        """End a workout session and calculate total volume"""
        try:
            session = self.get_workout_session(session_id)
            if not session:
                raise ValueError("Session not found")
                
            # Get all exercises and calculate total volume
            exercises = self.get_session_exercises(session_id)
            total_volume = sum(ex.total_volume or 0 for ex in exercises)
            
            # Update session
            session.end_time = datetime.utcnow()
            session.total_volume = total_volume
            
            self.db.commit()
            self.db.refresh(session)
            return session
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ending workout session: {str(e)}")
            raise

    def store_exercise_data(
        self,
        session_id: int,
        name: str,
        movement_pattern: Optional[str] = None,
        notes: Optional[str] = None,
        num_sets: Optional[int] = None,
        reps: Optional[List[int]] = None,
        weight: Optional[List[float]] = None,
        rpe: Optional[float] = None,
        tempo: Optional[str] = None,
        total_volume: Optional[float] = None,
        equipment: Optional[str] = None,
        difficulty: Optional[str] = None,
        estimated_duration: Optional[int] = None,
        rest_period: Optional[int] = None,
        muscle_activations: Optional[List[Dict[str, Any]]] = None
    ) -> Exercise:
        """Store exercise data with proper array handling"""
        try:
            # Create exercise record
            exercise = Exercise(
                session_id=session_id,
                name=name,
                movement_pattern=movement_pattern,
                notes=notes,
                num_sets=num_sets,
                reps=json.dumps(reps) if reps else None,  # Convert to JSON string
                weight=json.dumps(weight) if weight else None,  # Convert to JSON string
                rpe=rpe,
                tempo=tempo,
                total_volume=total_volume,
                equipment=equipment,
                difficulty=difficulty,
                estimated_duration=estimated_duration,
                rest_period=rest_period
            )
            
            self.db.add(exercise)
            self.db.flush()  # Get the exercise ID
            
            # Add muscle activations if provided
            if muscle_activations:
                for activation in muscle_activations:
                    muscle_activation = MuscleActivation(
                        exercise_id=exercise.id,
                        muscle_name=activation.get("muscle_name"),
                        activation_level=MuscleActivationLevel[activation.get("activation_level", "PRIMARY")],
                        estimated_volume=activation.get("estimated_volume")
                    )
                    self.db.add(muscle_activation)
            
            self.db.commit()
            self.db.refresh(exercise)
            return exercise
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing exercise data: {str(e)}")
            raise

    def get_exercise(self, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID with proper array handling"""
        try:
            exercise = self.db.query(Exercise).filter(Exercise.id == exercise_id).first()
            if exercise:
                # Load relationships
                _ = exercise.muscle_activations
            return exercise
        except Exception as e:
            logger.error(f"Error getting exercise: {str(e)}")
            return None

    def create_exercise(self, session_id: int, name: str, movement_pattern: str, 
                       sets: int, reps: int, weight: float, total_volume: float,
                       notes: Optional[str] = None, equipment: Optional[str] = None,
                       difficulty: Optional[str] = None, estimated_duration: Optional[int] = None,
                       rest_period: Optional[int] = None, rpe: Optional[float] = None,
                       tempo: Optional[str] = None) -> Exercise:
        """Create a new exercise record"""
        exercise = Exercise(
            session_id=session_id,
            name=name,
            movement_pattern=movement_pattern,
            num_sets=sets,
            reps=reps,
            weight=weight,
            total_volume=total_volume,
            notes=notes,
            equipment=equipment,
            difficulty=difficulty,
            estimated_duration=estimated_duration,
            rest_period=rest_period,
            rpe=rpe,
            tempo=tempo
        )
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def create_muscle_activation(self, exercise_id: int, muscle_name: str, activation_level: str, estimated_volume: float) -> MuscleActivation:
        """Create a muscle activation record and associate it with an exercise"""
        try:
            # Normalize the activation level
            level = activation_level.lower()
            if level not in [e.value for e in MuscleActivationLevel]:
                level = "secondary"  # Default to secondary if invalid
                
            # Find the enum member with this value
            enum_member = next(e for e in MuscleActivationLevel if e.value == level)
            
            muscle_activation = MuscleActivation(
                exercise_id=exercise_id,
                muscle_name=muscle_name.lower(),
                activation_level=enum_member,
                estimated_volume=estimated_volume
            )
            self.db.add(muscle_activation)
            self.db.commit()
            self.db.refresh(muscle_activation)
            return muscle_activation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating muscle activation: {str(e)}")
            raise

    def get_muscle_tracking(self, days: int = 30, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get tracking data for all muscles worked in the past N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query
        query = (
            self.db.query(
                MuscleActivation.muscle_name,
                func.sum(MuscleActivation.estimated_volume).label("total_volume"),
                func.count(MuscleActivation.id).label("exercise_count"),
                func.max(WorkoutSession.start_time).label("last_trained")
            )
            .select_from(MuscleActivation)
            .join(Exercise)
            .join(WorkoutSession)
            .filter(WorkoutSession.start_time >= cutoff_date)
            .filter(WorkoutSession.end_time.isnot(None))  # Only include completed sessions
        )
        
        # Add user filter if specified
        if user_id is not None:
            query = query.filter(WorkoutSession.user_id == user_id)
        
        # Execute query with grouping
        activations = (
            query.group_by(MuscleActivation.muscle_name)
            .all()
        )
        
        # Debug logging
        if not activations:
            print("No muscle activations found")
            # Check if there are any workout sessions
            sessions = (
                self.db.query(WorkoutSession)
                .filter(WorkoutSession.start_time >= cutoff_date)
                .filter(WorkoutSession.end_time.isnot(None))
                .all()
            )
            print(f"Found {len(sessions)} completed workout sessions")
        
        tracking_data = []
        for activation in activations:
            status = self._calculate_muscle_status(
                activation.total_volume,
                activation.exercise_count,
                activation.last_trained
            )
            tracking = {
                "muscle_name": activation.muscle_name,
                "total_volume": activation.total_volume,
                "exercise_count": activation.exercise_count,
                "last_trained": activation.last_trained,
                "status": status
            }
            tracking_data.append(tracking)
        
        return tracking_data

    def get_muscle_volume_data(self, timeframe: str = "weekly", user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get volume data for all muscles in the specified timeframe"""
        if timeframe == "weekly":
            cutoff_date = datetime.utcnow() - timedelta(days=7)
        else:  # monthly
            cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Debug: Print cutoff date
        print(f"Getting volume data since {cutoff_date}")
        
        try:
            # First check if we have any workout sessions
            sessions = (
                self.db.query(WorkoutSession)
                .filter(WorkoutSession.start_time >= cutoff_date)
                .filter(WorkoutSession.end_time.isnot(None))
            )
            
            if user_id is not None:
                sessions = sessions.filter(WorkoutSession.user_id == user_id)
            
            sessions = sessions.all()
            print(f"Found {len(sessions)} completed workout sessions")
            
            if not sessions:
                print("No workout sessions found in the timeframe")
                return []
            
            # Get all exercises for these sessions
            session_ids = [s.id for s in sessions]
            exercises = (
                self.db.query(Exercise)
                .filter(Exercise.session_id.in_(session_ids))
                .all()
            )
            print(f"Found {len(exercises)} exercises")
            
            if not exercises:
                print("No exercises found in the sessions")
                return []
            
            # Get muscle activations for these exercises
            exercise_ids = [e.id for e in exercises]
            volume_data = (
                self.db.query(
                    MuscleActivation.muscle_name,
                    func.sum(MuscleActivation.estimated_volume).label("total_volume"),
                    func.avg(MuscleActivation.activation_percentage).label("avg_activation_percentage"),
                    func.avg(MuscleActivation.volume_multiplier).label("avg_volume_multiplier"),
                    cast(WorkoutSession.start_time, Date).label("date")
                )
                .select_from(MuscleActivation)
                .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
                .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
                .filter(Exercise.id.in_(exercise_ids))
                .group_by(
                    MuscleActivation.muscle_name,
                    cast(WorkoutSession.start_time, Date)
                )
                .all()
            )
            
            print(f"Found volume data for {len(volume_data)} muscle-date combinations")
            
            return [
                {
                    "muscle_name": data.muscle_name,
                    "total_volume": float(data.total_volume),  # Convert Decimal to float
                    "avg_activation_percentage": float(data.avg_activation_percentage),
                    "avg_volume_multiplier": float(data.avg_volume_multiplier),
                    "date": data.date
                }
                for data in volume_data
            ]
            
        except Exception as e:
            logger.error(f"Error getting volume data: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _calculate_muscle_status(self, volume: float, count: int, last_trained: datetime) -> str:
        """Calculate the training status of a muscle based on volume and frequency"""
        days_since_trained = (datetime.utcnow() - last_trained).days
        
        if days_since_trained > 14:
            return "Undertrained"
        elif volume < 1000:  # Example threshold
            return "Maintenance"
        else:
            return "Optimal"
