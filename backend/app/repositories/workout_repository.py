from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation, MuscleActivationLevel
from ..models.user import User
from sqlalchemy import func

class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_workout_session(self, session_id: int) -> Optional[WorkoutSession]:
        """Get a workout session by ID"""
        return self.db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()

    def get_user_workout_sessions(self, user_id: int) -> List[WorkoutSession]:
        """Get all workout sessions for a user"""
        return self.db.query(WorkoutSession).filter(WorkoutSession.user_id == user_id).all()

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        """Create a new workout session"""
        session = WorkoutSession(
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_exercise(self, session_id: int, name: str, sets: int, reps: int, weight: float) -> Exercise:
        """Add an exercise to a workout session"""
        exercise = Exercise(
            session_id=session_id,
            name=name,
            sets=sets,
            reps=reps,
            weight=weight,
            movement_pattern="",  # TODO: Add movement pattern
            equipment_needed=[]  # TODO: Add equipment
        )
        
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def get_session_exercises(self, session_id: int) -> List[Exercise]:
        """Get all exercises for a workout session"""
        return self.db.query(Exercise).filter(Exercise.session_id == session_id).all()

    def add_muscle_activation(self, exercise_id: int, muscle_name: str, activation_level: MuscleActivationLevel, volume: float) -> MuscleActivation:
        """Add a muscle activation record for an exercise"""
        activation = MuscleActivation(
            exercise_id=exercise_id,
            muscle_name=muscle_name,
            activation_level=activation_level,
            estimated_volume=volume
        )
        self.db.add(activation)
        self.db.commit()
        self.db.refresh(activation)
        return activation

    def get_exercise_muscle_activations(self, exercise_id: int) -> List[MuscleActivation]:
        """Get all muscle activations for an exercise"""
        return (
            self.db.query(MuscleActivation)
            .filter(MuscleActivation.exercise_id == exercise_id)
            .all()
        )

    def get_user_muscle_activations(self, user_id: int) -> List[MuscleActivation]:
        """Get all muscle activations for a user's exercises"""
        return (
            self.db.query(MuscleActivation)
            .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(WorkoutSession.user_id == user_id)
            .all()
        )

    def get_user_muscle_volume(self, user_id: int, muscle_name: str) -> float:
        """Get total volume for a specific muscle for a user"""
        result = (
            self.db.query(func.sum(MuscleActivation.estimated_volume))
            .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(
                WorkoutSession.user_id == user_id,
                MuscleActivation.muscle_name == muscle_name
            )
            .scalar()
        )
        return result or 0.0

    def get_user_muscle_frequency(self, user_id: int, muscle_name: str) -> int:
        """Get number of times a muscle has been trained by a user"""
        result = (
            self.db.query(func.count(Exercise.id.distinct()))
            .join(MuscleActivation, Exercise.id == MuscleActivation.exercise_id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(
                WorkoutSession.user_id == user_id,
                MuscleActivation.muscle_name == muscle_name
            )
            .scalar()
        )
        return result or 0

    def get_user_last_trained(self, user_id: int, muscle_name: str) -> Optional[datetime]:
        """Get the last time a muscle was trained by a user"""
        result = (
            self.db.query(WorkoutSession.start_time)
            .join(Exercise, WorkoutSession.id == Exercise.session_id)
            .join(MuscleActivation, Exercise.id == MuscleActivation.exercise_id)
            .filter(
                WorkoutSession.user_id == user_id,
                MuscleActivation.muscle_name == muscle_name
            )
            .order_by(WorkoutSession.start_time.desc())
            .first()
        )
        return result[0] if result else None
