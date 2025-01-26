from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import json
from typing import List, Optional, Dict, Any
from .database import Base
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MuscleActivationLevel(enum.Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('workout_sessions.id'))
    name = Column(String, index=True)
    movement_pattern = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Exercise set data
    num_sets = Column(Integer, nullable=True)
    reps = Column(JSON, nullable=True)  # array of reps per set
    weight = Column(JSON, nullable=True)  # array of weights per set
    rpe = Column(Float, nullable=True)
    tempo = Column(String, nullable=True)
    total_volume = Column(Float, nullable=True)
    
    # Metadata
    equipment = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    rest_period = Column(Integer, nullable=True)
    
    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercises")
    muscle_activations = relationship("MuscleActivation", back_populates="exercise")

    def to_dict(self):
        """Convert exercise to dictionary with proper array handling"""
        try:
            reps = json.loads(self.reps) if self.reps else []
            weight = json.loads(self.weight) if self.weight else []
        except (json.JSONDecodeError, TypeError):
            logger.error(f"Error parsing arrays for exercise {self.id}")
            reps = []
            weight = []
            
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'name': self.name,
            'movement_pattern': self.movement_pattern,
            'notes': self.notes,
            'num_sets': self.num_sets,
            'reps': reps,
            'weight': weight,
            'rpe': self.rpe,
            'tempo': self.tempo,
            'total_volume': self.total_volume,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'estimated_duration': self.estimated_duration,
            'rest_period': self.rest_period,
            'muscle_activations': [ma.to_dict() for ma in self.muscle_activations] if self.muscle_activations else []
        }
        return data

    def __init__(self, **kwargs):
        """Initialize exercise with proper array handling"""
        # Convert arrays to JSON strings when storing
        if "reps" in kwargs:
            if isinstance(kwargs["reps"], str):
                # Already a JSON string
                pass
            elif isinstance(kwargs["reps"], (list, tuple)):
                kwargs["reps"] = json.dumps(kwargs["reps"])
            else:
                kwargs["reps"] = None
                
        if "weight" in kwargs:
            if isinstance(kwargs["weight"], str):
                # Already a JSON string
                pass
            elif isinstance(kwargs["weight"], (list, tuple)):
                kwargs["weight"] = json.dumps(kwargs["weight"])
            else:
                kwargs["weight"] = None
                
        super().__init__(**kwargs)

class MuscleActivationData(BaseModel):
    muscle_name: str
    activation_level: MuscleActivationLevel
    estimated_volume: Optional[float] = None

class MuscleActivation(Base):
    __tablename__ = 'muscle_activations'
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    muscle_name = Column(String, index=True)
    activation_level = Column(Enum(MuscleActivationLevel))
    estimated_volume = Column(Float, nullable=True)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="muscle_activations")

    def to_dict(self) -> Dict[str, Any]:
        """Convert muscle activation to dictionary"""
        return {
            "id": self.id,
            "exercise_id": self.exercise_id,
            "muscle_name": self.muscle_name,
            "activation_level": self.activation_level.value if self.activation_level else None,
            "estimated_volume": self.estimated_volume
        }

class MuscleTracking(Base):
    __tablename__ = 'muscle_tracking'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    muscle_name = Column(String, index=True)
    status = Column(String)
    last_trained = Column(DateTime)
    total_volume = Column(Float, default=0.0)
    exercise_count = Column(Integer, default=0)
    weekly_volume = Column(Float, default=0.0)
    monthly_volume = Column(Float, default=0.0)
    coverage_rating = Column(String)
    recovery_status = Column(Float)
    week_start = Column(DateTime)
    
    # Relationships
    user = relationship("User")

class ExerciseTemplate(Base):
    __tablename__ = 'exercise_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    muscle_involvement = Column(JSON)
    equipment = Column(String, nullable=True)  # Changed from equipment_needed to match schema
    movement_pattern = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutSession(Base):
    __tablename__ = 'workout_sessions'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_analysis = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    total_volume = Column(Float, nullable=True)
    
    # Relationships
    exercises = relationship("Exercise", back_populates="workout_session")
    user = relationship("User", back_populates="workout_sessions")

class MuscleVolumeData(Base):
    __tablename__ = 'muscle_volume_data'
    
    id = Column(Integer, primary_key=True, index=True)
    muscle_name = Column(String, index=True)
    total_volume = Column(Float)
    date = Column(DateTime)
