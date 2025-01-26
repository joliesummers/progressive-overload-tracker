from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from ..models.progress import ProgressMetric, PerformanceAggregate, MetricType
from ..models.exercise import WorkoutSession, Exercise, MuscleActivation, MuscleActivationLevel
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProgressionMetrics:
    current_value: float
    previous_value: float
    percent_change: float
    trend: str  # "increasing", "decreasing", "stable"

@dataclass
class MuscleBalance:
    muscle_name: str
    total_volume: float
    relative_emphasis: float  # percentage of total volume
    frequency: int  # number of times trained
    last_trained: datetime

class AnalysisService:
    """Service for analyzing workout data and calculating advanced metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_progressive_overload(self, user_id: int, exercise_name: str, 
                                    days: int = 30) -> ProgressionMetrics:
        """Calculate progressive overload metrics for a specific exercise"""
        now = datetime.utcnow()
        period_start = now - timedelta(days=days)
        mid_point = now - timedelta(days=days//2)
        
        # Get volume metrics for the exercise
        metrics = (
            self.db.query(ProgressMetric)
            .filter(
                ProgressMetric.user_id == user_id,
                ProgressMetric.exercise_name == exercise_name,
                ProgressMetric.metric_type == MetricType.VOLUME,
                ProgressMetric.timestamp >= period_start
            )
            .order_by(ProgressMetric.timestamp.asc())
            .all()
        )
        
        if not metrics:
            return None
            
        # Calculate average volume for first and second half of the period
        first_half = [m.value for m in metrics if m.timestamp < mid_point]
        second_half = [m.value for m in metrics if m.timestamp >= mid_point]
        
        if not first_half or not second_half:
            return None
            
        prev_avg = np.mean(first_half)
        current_avg = np.mean(second_half)
        percent_change = ((current_avg - prev_avg) / prev_avg) * 100
        
        trend = "stable"
        if percent_change > 5:
            trend = "increasing"
        elif percent_change < -5:
            trend = "decreasing"
            
        return ProgressionMetrics(
            current_value=current_avg,
            previous_value=prev_avg,
            percent_change=percent_change,
            trend=trend
        )
    
    def analyze_volume_progression(self, user_id: int, 
                                 timeframe_days: int = 90) -> Dict[str, ProgressionMetrics]:
        """Analyze volume progression for all exercises"""
        # Get all exercises for the user
        exercises = (
            self.db.query(Exercise.name)
            .join(WorkoutSession)
            .filter(WorkoutSession.user_id == user_id)
            .distinct()
            .all()
        )
        
        results = {}
        for (exercise_name,) in exercises:
            metrics = self.calculate_progressive_overload(user_id, exercise_name, timeframe_days)
            if metrics:
                results[exercise_name] = metrics
                
        return results
    
    def calculate_rest_periods(self, user_id: int, days: int = 30) -> Dict[str, timedelta]:
        """Calculate average rest periods between exercises"""
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Get all workouts ordered by time
        workouts = (
            self.db.query(WorkoutSession)
            .filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.start_time >= period_start
            )
            .order_by(WorkoutSession.start_time.asc())
            .all()
        )
        
        if len(workouts) < 2:
            return {}
            
        rest_periods = {}
        for i in range(1, len(workouts)):
            rest_time = workouts[i].start_time - workouts[i-1].end_time
            rest_periods[workouts[i].id] = rest_time
            
        return rest_periods

    def generate_performance_insights(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate insights based on user's workout data"""
        insights = []
        
        # Volume progression insight
        volume_metrics = (
            self.db.query(ProgressMetric)
            .filter(
                ProgressMetric.user_id == user_id,
                ProgressMetric.metric_type == MetricType.VOLUME
            )
            .order_by(ProgressMetric.timestamp.desc())
            .limit(10)
            .all()
        )
        
        if volume_metrics:
            recent_volume = volume_metrics[0].value
            avg_volume = sum(m.value for m in volume_metrics) / len(volume_metrics)
            
            if recent_volume > avg_volume * 1.1:  # 10% above average
                insights.append({
                    "category": "progress",
                    "message": "Your recent workout volume is 10% above your average - great progress!",
                    "relevance_score": 0.8
                })
        
        # Add muscle balance insights
        muscle_balance = self.analyze_muscle_balance(user_id)
        if muscle_balance:
            # Find undertrained muscles
            total_volume = sum(m.total_volume for m in muscle_balance)
            for muscle, data in muscle_balance:
                if data.relative_emphasis < 0.1 and total_volume > 0:  # Less than 10% of total volume
                    insights.append({
                        "category": "balance",
                        "message": f"Consider increasing training volume for {muscle} - currently undertrained",
                        "relevance_score": 0.7
                    })
        
        return insights
    
    def analyze_muscle_balance(self, user_id: int, days: int = 30) -> List[MuscleBalance]:
        """Analyze muscle group balance and training frequency"""
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Get all muscle activations in the period
        activations = (
            self.db.query(
                MuscleActivation.muscle_name,
                func.sum(MuscleActivation.estimated_volume).label("total_volume"),
                func.count(MuscleActivation.id).label("frequency"),
                func.max(WorkoutSession.end_time).label("last_trained")
            )
            .join(Exercise, MuscleActivation.exercise_id == Exercise.id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.start_time >= period_start
            )
            .group_by(MuscleActivation.muscle_name)
            .all()
        )
        
        if not activations:
            return []
            
        # Calculate total volume across all muscles
        total_volume = sum(activation[1] for activation in activations)
        
        return [
            MuscleBalance(
                muscle_name=muscle_name,
                total_volume=volume,
                relative_emphasis=(volume / total_volume) * 100 if total_volume > 0 else 0,
                frequency=freq,
                last_trained=last_trained
            )
            for muscle_name, volume, freq, last_trained in activations
        ]
        
    def analyze_workout_frequency(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze workout frequency patterns"""
        period_start = datetime.utcnow() - timedelta(days=days)
        
        # Get all workout sessions in the period
        sessions = (
            self.db.query(WorkoutSession)
            .filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.start_time >= period_start
            )
            .order_by(WorkoutSession.start_time.asc())
            .all()
        )
        
        if not sessions:
            return {
                "total_sessions": 0,
                "average_frequency": 0,
                "consistency_score": 0
            }
            
        # Calculate metrics
        total_sessions = len(sessions)
        days_between = (sessions[-1].start_time - sessions[0].start_time).days
        average_frequency = total_sessions / (days_between + 1)  # sessions per day
        
        # Calculate consistency score (0-100)
        # Higher score means more consistent intervals between workouts
        intervals = []
        for i in range(1, len(sessions)):
            interval = (sessions[i].start_time - sessions[i-1].start_time).total_seconds()
            intervals.append(interval)
            
        if intervals:
            std_dev = np.std(intervals)
            mean_interval = np.mean(intervals)
            # Lower coefficient of variation = more consistent
            cv = (std_dev / mean_interval) if mean_interval > 0 else float('inf')
            consistency_score = max(0, min(100, 100 * (1 - cv)))
        else:
            consistency_score = 0
            
        return {
            "total_sessions": total_sessions,
            "average_frequency": round(average_frequency * 7, 2),  # Convert to sessions per week
            "consistency_score": round(consistency_score, 2),
            "days_tracked": days_between + 1
        }
