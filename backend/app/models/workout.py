from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship, Session
from datetime import datetime
from typing import List
from .database import Base
import enum

class ActivationLevel(str, enum.Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_volume = Column(Float, default=0.0)  # Total volume for the entire session
    
    exercises = relationship("Exercise", back_populates="session")
    user = relationship("User", back_populates="workout_sessions")
    
    def calculate_total_volume(self, db: Session):
        """Calculate and update the total volume for this workout session"""
        result = db.query(func.sum(MuscleActivation.estimated_volume))\
            .join(Exercise)\
            .filter(Exercise.session_id == self.id)\
            .scalar()
        self.total_volume = result or 0.0
        db.commit()

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    name = Column(String)
    movement_pattern = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_volume = Column(Float, default=0.0)  # Total volume for this exercise
    
    sets = relationship("ExerciseSet", back_populates="exercise")
    muscle_activations = relationship("MuscleActivation", back_populates="exercise")
    session = relationship("WorkoutSession", back_populates="exercises")
    
    def calculate_total_volume(self, db: Session):
        """Calculate and update the total volume for this exercise"""
        result = db.query(func.sum(MuscleActivation.estimated_volume))\
            .filter(MuscleActivation.exercise_id == self.id)\
            .scalar()
        self.total_volume = result or 0.0
        db.commit()
        
        # Update session total volume
        if self.session:
            self.session.calculate_total_volume(db)

class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    reps = Column(Integer)
    weight = Column(Float)
    set_number = Column(Integer)
    
    exercise = relationship("Exercise", back_populates="sets")

class MuscleActivation(Base):
    __tablename__ = "muscle_activations"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    muscle_name = Column(String)
    activation_level = Column(Enum(ActivationLevel))
    estimated_volume = Column(Float, default=0.0)
    
    exercise = relationship("Exercise", back_populates="muscle_activations")
    
    @classmethod
    def create_from_agent_data(cls, db: Session, exercise_id: int, muscle_data: dict):
        """Create muscle activations from agent response data"""
        activations = []
        
        # Add primary muscles
        for muscle_name, volume in muscle_data.get('primary_muscles', []):
            activation = cls(
                exercise_id=exercise_id,
                muscle_name=muscle_name,
                activation_level=ActivationLevel.PRIMARY,
                estimated_volume=volume
            )
            activations.append(activation)
            
        # Add secondary muscles
        for muscle_name, volume in muscle_data.get('secondary_muscles', []):
            activation = cls(
                exercise_id=exercise_id,
                muscle_name=muscle_name,
                activation_level=ActivationLevel.SECONDARY,
                estimated_volume=volume * 0.6  # Reduce volume for secondary muscles
            )
            activations.append(activation)
            
        # Add tertiary muscles
        for muscle_name, volume in muscle_data.get('tertiary_muscles', []):
            activation = cls(
                exercise_id=exercise_id,
                muscle_name=muscle_name,
                activation_level=ActivationLevel.TERTIARY,
                estimated_volume=volume * 0.3  # Reduce volume for tertiary muscles
            )
            activations.append(activation)
        
        if not activations:
            return None
            
        try:
            db.add_all(activations)
            db.commit()
            
            # Update exercise and session volumes
            exercise = db.query(Exercise).get(exercise_id)
            if exercise:
                exercise.calculate_total_volume(db)
                if exercise.session:
                    exercise.session.calculate_total_volume(db)
            
            return activations
        except Exception as e:
            db.rollback()
            raise e
