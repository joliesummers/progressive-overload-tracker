from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)  # Store hashed password
    
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    progress_metrics = relationship("ProgressMetric", back_populates="user")
    performance_aggregates = relationship("PerformanceAggregate", back_populates="user")
    insights = relationship("UserInsight", back_populates="user")
