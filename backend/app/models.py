from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class MuscleActivationLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    workouts = relationship("WorkoutSession", back_populates="user")

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float)
    sentiment_analysis = Column(String)
    notes = Column(String)
    user = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", back_populates="workout_session")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    name = Column(String)
    sets = Column(Integer)
    reps = Column(Integer)
    weight = Column(Float)
    rpe = Column(Float, nullable=True)  # Rate of Perceived Exertion
    tempo = Column(String, nullable=True)  # e.g., "3-1-3" for eccentric-pause-concentric
    notes = Column(String, nullable=True)
    workout_session = relationship("WorkoutSession", back_populates="exercises")
    muscle_activations = relationship("ExerciseMuscleActivation", back_populates="exercise")

class ExerciseMuscleActivation(Base):
    __tablename__ = "exercise_muscle_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    muscle_name = Column(String)
    activation_level = Column(Enum(MuscleActivationLevel))
    estimated_volume = Column(Float)  # Calculated based on sets, reps, weight
    exercise = relationship("Exercise", back_populates="muscle_activations")

class ExerciseTemplate(Base):
    __tablename__ = "exercise_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    muscle_involvement = Column(JSON)  # Structured JSON with muscle activation patterns
    equipment_needed = Column(JSON)
    movement_pattern = Column(String)  # e.g., "push", "pull", "hinge", "squat"
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MuscleTracking(Base):
    __tablename__ = "muscle_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    muscle_name = Column(String)
    weekly_volume = Column(Float)  # Total volume for the week
    monthly_volume = Column(Float)  # Total volume for the month
    last_worked = Column(DateTime)
    coverage_rating = Column(String)  # Excellent/Good/Adequate/Not enough
    recovery_status = Column(Float)  # Estimated recovery status based on volume and time
    week_start = Column(DateTime)  # Start of the tracking week
