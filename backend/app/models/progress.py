from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class MetricType(enum.Enum):
    VOLUME = "volume"
    MAX_WEIGHT = "max_weight"
    TOTAL_REPS = "total_reps"
    FREQUENCY = "frequency"
    INTENSITY = "intensity"

class ProgressMetric(Base):
    """Stores progress metrics for exercises and muscle groups"""
    __tablename__ = "progress_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=True)  # Null for muscle-group metrics
    muscle_group = Column(String, nullable=True)   # Null for exercise-specific metrics
    metric_type = Column(Enum(MetricType), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress_metrics")

class PerformanceAggregate(Base):
    """Stores aggregated performance data over time periods"""
    __tablename__ = "performance_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=True)
    muscle_group = Column(String, nullable=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_volume = Column(Float, nullable=False, default=0.0)
    average_intensity = Column(Float, nullable=False, default=0.0)
    session_count = Column(Integer, nullable=False, default=0)
    max_weight = Column(Float, nullable=True)
    total_reps = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="performance_aggregates")

class UserInsight(Base):
    """Stores generated insights about user's workout patterns and progress"""
    __tablename__ = "user_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # e.g., "progress", "recovery", "balance"
    insight_text = Column(String, nullable=False)
    relevance_score = Column(Float, nullable=False)  # Higher score = more important
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration for time-sensitive insights
    
    # Relationships
    user = relationship("User", back_populates="insights")
