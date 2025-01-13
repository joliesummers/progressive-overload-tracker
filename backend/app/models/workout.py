from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
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
    
    exercises = relationship("Exercise", back_populates="session")
    user = relationship("User", back_populates="workout_sessions")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    name = Column(String)
    movement_pattern = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    sets = relationship("ExerciseSet", back_populates="exercise")
    muscle_activations = relationship("MuscleActivation", back_populates="exercise")
    session = relationship("WorkoutSession", back_populates="exercises")

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
    estimated_volume = Column(Float)
    
    exercise = relationship("Exercise", back_populates="muscle_activations")
