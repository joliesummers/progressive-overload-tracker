from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from ..services.analysis_service import AnalysisService
import json
import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExerciseRecommendation:
    exercise_name: str
    reason: str
    priority: float  # 0-1, higher means more important
    target_muscles: List[str]
    suggested_volume: Optional[float] = None

@dataclass
class ProgressReport:
    period_start: datetime
    period_end: datetime
    total_volume: float
    session_count: int
    top_exercises: List[Dict[str, Any]]
    muscle_coverage: Dict[str, float]
    achievements: List[str]
    areas_for_improvement: List[str]

class ReportService:
    """Service for generating reports and recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analysis_service = AnalysisService(db)
        
    def generate_progress_report(self, user_id: int, days: int = 30) -> ProgressReport:
        """Generate a comprehensive progress report"""
        now = datetime.utcnow()
        period_start = now - timedelta(days=days)
        
        # Get progression data
        progression_data = self.analysis_service.analyze_volume_progression(user_id, days)
        
        # Get muscle balance data
        muscle_balance = self.analysis_service.analyze_muscle_balance(user_id, days)
        
        # Get workout frequency data
        frequency_data = self.analysis_service.analyze_workout_frequency(user_id, days)
        
        # Calculate achievements and improvements
        achievements = []
        improvements = []
        
        # Check volume progression
        for exercise, metrics in progression_data.items():
            if metrics.percent_change > 10:
                achievements.append(f"Increased {exercise} volume by {metrics.percent_change:.1f}%")
            elif metrics.percent_change < -10:
                improvements.append(f"Volume for {exercise} has decreased by {abs(metrics.percent_change):.1f}%")
                
        # Check muscle balance
        muscle_coverage = {m.muscle_name: m.relative_emphasis for m in muscle_balance}
        for muscle in muscle_balance:
            if muscle.relative_emphasis < 5:  # Less than 5% of total volume
                improvements.append(f"Consider increasing {muscle.muscle_name} training volume")
                
        # Check workout consistency
        if frequency_data["consistency_score"] > 80:
            achievements.append("Maintained high workout consistency")
        elif frequency_data["consistency_score"] < 50:
            improvements.append("Work on maintaining a more consistent workout schedule")
            
        # Get top exercises by volume
        top_exercises = [
            {
                "name": exercise,
                "volume_change": metrics.percent_change,
                "current_volume": metrics.current_value
            }
            for exercise, metrics in sorted(
                progression_data.items(),
                key=lambda x: x[1].current_value,
                reverse=True
            )[:5]  # Top 5 exercises
        ]
        
        return ProgressReport(
            period_start=period_start,
            period_end=now,
            total_volume=sum(m.current_value for m in progression_data.values()),
            session_count=frequency_data["total_sessions"],
            top_exercises=top_exercises,
            muscle_coverage=muscle_coverage,
            achievements=achievements,
            areas_for_improvement=improvements
        )
        
    def generate_recommendations(self, user_id: int) -> List[ExerciseRecommendation]:
        """Generate personalized exercise recommendations"""
        # Get muscle balance data
        muscle_balance = self.analysis_service.analyze_muscle_balance(user_id)
        
        # Get rest periods
        rest_periods = self.analysis_service.calculate_rest_periods(user_id)
        
        recommendations = []
        
        # Find undertrained muscles
        undertrained_muscles = [
            m for m in muscle_balance
            if m.relative_emphasis < 10  # Less than 10% of total volume
        ]
        
        # Standard exercise patterns for muscle groups
        exercise_patterns = {
            "Chest": ["Bench Press", "Dumbbell Flyes", "Push-Ups"],
            "Back": ["Pull-Ups", "Rows", "Lat Pulldowns"],
            "Legs": ["Squats", "Deadlifts", "Lunges"],
            "Shoulders": ["Overhead Press", "Lateral Raises", "Face Pulls"],
            "Arms": ["Bicep Curls", "Tricep Extensions", "Hammer Curls"],
            "Core": ["Planks", "Ab Wheel", "Russian Twists"]
        }
        
        # Recommend exercises for undertrained muscles
        for muscle in undertrained_muscles:
            target_group = next(
                (group for group, muscles in exercise_patterns.items() 
                 if muscle.muscle_name in group),
                None
            )
            
            if target_group:
                # Filter out recently performed exercises
                available_exercises = [
                    ex for ex in exercise_patterns[target_group]
                    if ex not in rest_periods or rest_periods[ex].days >= 2
                ]
                
                if available_exercises:
                    recommendations.append(ExerciseRecommendation(
                        exercise_name=available_exercises[0],
                        reason=f"Increase {muscle.muscle_name} training volume",
                        priority=1.0 - (muscle.relative_emphasis / 100),
                        target_muscles=[muscle.muscle_name],
                        suggested_volume=1000 if muscle.relative_emphasis < 5 else 500
                    ))
                    
        # Sort recommendations by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
        
    def export_progress_data(self, user_id: int, format: str = "json") -> str:
        """Export progress data in specified format"""
        report = self.generate_progress_report(user_id)
        
        if format == "json":
            return json.dumps({
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "metrics": {
                    "total_volume": report.total_volume,
                    "session_count": report.session_count
                },
                "top_exercises": report.top_exercises,
                "muscle_coverage": report.muscle_coverage,
                "achievements": report.achievements,
                "areas_for_improvement": report.areas_for_improvement
            }, indent=2)
            
        elif format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Metric", "Value"])
            
            # Write basic metrics
            writer.writerow(["Period Start", report.period_start.isoformat()])
            writer.writerow(["Period End", report.period_end.isoformat()])
            writer.writerow(["Total Volume", report.total_volume])
            writer.writerow(["Session Count", report.session_count])
            
            # Write muscle coverage
            writer.writerow([])
            writer.writerow(["Muscle", "Coverage %"])
            for muscle, coverage in report.muscle_coverage.items():
                writer.writerow([muscle, f"{coverage:.1f}%"])
                
            # Write achievements
            writer.writerow([])
            writer.writerow(["Achievements"])
            for achievement in report.achievements:
                writer.writerow([achievement])
                
            return output.getvalue()
            
        else:
            raise ValueError(f"Unsupported export format: {format}")
