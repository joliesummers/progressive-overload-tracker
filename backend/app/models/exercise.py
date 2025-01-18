from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base

class MuscleActivationLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"

# Association table for exercise-muscle relationships
exercise_muscle_association = Table(
    'exercise_muscle_association',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercises.id')),
    Column('muscle_id', Integer, ForeignKey('muscle_activations.id')),
)

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('workout_sessions.id'))
    name = Column(String, index=True)
    movement_pattern = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Exercise set data
    num_sets = Column(Integer)  
    reps = Column(Integer)
    weight = Column(Float, nullable=True)
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion
    tempo = Column(String, nullable=True)  # e.g., "3-1-3" for eccentric-pause-concentric
    total_volume = Column(Float, nullable=True)
    
    # Metadata
    equipment = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    rest_period = Column(Integer, nullable=True)  # in seconds
    
    # Relationships
    workout_session = relationship("WorkoutSession", back_populates="exercises")
    muscle_activations = relationship(
        "MuscleActivation", 
        secondary=exercise_muscle_association,
        back_populates="exercises"
    )
    exercise_sets = relationship("ExerciseSet", back_populates="exercise")  

class MuscleActivation(Base):
    __tablename__ = 'muscle_activations'
    
    id = Column(Integer, primary_key=True, index=True)
    muscle_name = Column(String, index=True)
    activation_level = Column(Enum(MuscleActivationLevel))
    estimated_volume = Column(Float)
    
    # Relationships
    exercises = relationship(
        "Exercise", 
        secondary=exercise_muscle_association,
        back_populates="muscle_activations"
    )

class MuscleTracking(Base):
    __tablename__ = 'muscle_tracking'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    muscle_name = Column(String, index=True)
    status = Column(String)  # "Optimal", "Maintenance", "Undertrained"
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
    muscle_involvement = Column(JSON)  # Dictionary mapping muscles to activation levels
    equipment_needed = Column(JSON)  # List of required equipment
    movement_pattern = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutSession(Base):
    __tablename__ = 'workout_sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_analysis = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    total_volume = Column(Float, nullable=True)
    
    # Relationships
    exercises = relationship("Exercise", back_populates="workout_session")
    user = relationship("User", back_populates="workout_sessions")

class ExerciseSet(Base):
    __tablename__ = 'exercise_sets'

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey('exercises.id'))
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float, nullable=True)
    rpe = Column(Float, nullable=True)
    tempo = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    # Relationships
    exercise = relationship("Exercise", back_populates="exercise_sets")

class MuscleVolumeData(Base):
    __tablename__ = 'muscle_volume_data'

    id = Column(Integer, primary_key=True, index=True)
    muscle_name = Column(String, index=True)
    total_volume = Column(Float)
    date = Column(DateTime)
