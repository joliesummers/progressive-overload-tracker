from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from ..models.workout import WorkoutSession, Exercise, ExerciseSet, MuscleActivation, ActivationLevel

class WorkoutStorageService:
    """Service for storing workout data in the database"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        """Create a new workout session for a user"""
        session = WorkoutSession(
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def store_exercise_data(self, session_id: int, exercise_name: str, muscle_data: Dict[str, Any]) -> Exercise:
        """Store exercise and muscle activation data from the Bedrock agent response"""
        # Create exercise record
        exercise = Exercise(
            session_id=session_id,
            name=exercise_name,
            movement_pattern="",  # TODO: Add movement pattern from agent response if available
            timestamp=datetime.utcnow(),
            total_volume=muscle_data.get("total_volume", 0.0)
        )
        self.db.add(exercise)
        self.db.flush()  # Get the exercise ID without committing

        # Store primary muscles
        for muscle_name, activation_ratio in muscle_data.get("primary_muscles", []):
            muscle_activation = MuscleActivation(
                exercise_id=exercise.id,
                muscle_name=muscle_name,
                activation_level=ActivationLevel.PRIMARY,
                estimated_volume=muscle_data["total_volume"] * activation_ratio
            )
            self.db.add(muscle_activation)

        # Store secondary muscles
        for muscle_name, activation_ratio in muscle_data.get("secondary_muscles", []):
            muscle_activation = MuscleActivation(
                exercise_id=exercise.id,
                muscle_name=muscle_name,
                activation_level=ActivationLevel.SECONDARY,
                estimated_volume=muscle_data["total_volume"] * activation_ratio
            )
            self.db.add(muscle_activation)

        # Update workout session total volume
        session = self.db.query(WorkoutSession).filter_by(id=session_id).first()
        if session:
            session.total_volume = (session.total_volume or 0.0) + muscle_data["total_volume"]
            
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def end_workout_session(self, session_id: int, sentiment_score: float = None, sentiment_analysis: str = None):
        """End a workout session and update sentiment analysis if provided"""
        session = self.db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        if session:
            session.end_time = datetime.utcnow()
            if sentiment_score is not None:
                session.sentiment_score = sentiment_score
            if sentiment_analysis is not None:
                session.sentiment_analysis = sentiment_analysis
            self.db.commit()
            session.calculate_total_volume(self.db)
