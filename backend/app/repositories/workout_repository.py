from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..models.workout import WorkoutSession, Exercise, ExerciseSet, MuscleActivation
from ..services.exercise_analysis import ExerciseAnalysis

class WorkoutRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        session = WorkoutSession(
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_exercise_to_session(
        self,
        session_id: int,
        analysis: ExerciseAnalysis,
        sets_data: List[dict]
    ) -> Exercise:
        # Create exercise
        exercise = Exercise(
            session_id=session_id,
            name=analysis.exercise_name,
            movement_pattern=analysis.movement_pattern
        )
        self.db.add(exercise)
        self.db.flush()  # Get exercise ID

        # Add sets
        for set_data in sets_data:
            exercise_set = ExerciseSet(
                exercise_id=exercise.id,
                reps=set_data['reps'],
                weight=set_data['weight'],
                set_number=set_data['set_number']
            )
            self.db.add(exercise_set)

        # Add muscle activations
        for activation in analysis.muscle_activations:
            muscle_activation = MuscleActivation(
                exercise_id=exercise.id,
                muscle_name=activation.muscle_name,
                activation_level=activation.activation_level,
                estimated_volume=activation.estimated_volume
            )
            self.db.add(muscle_activation)

        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def get_user_workouts(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WorkoutSession]:
        query = self.db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user_id
        )
        
        if start_date:
            query = query.filter(WorkoutSession.start_time >= start_date)
        if end_date:
            query = query.filter(WorkoutSession.start_time <= end_date)
            
        return query.all()

    def get_muscle_activation_history(
        self,
        user_id: int,
        days: int = 7
    ) -> dict:
        """Get muscle activation and volume data for analytics"""
        from sqlalchemy import func
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all exercises in the time period
        exercises = self.db.query(Exercise).join(
            WorkoutSession
        ).filter(
            WorkoutSession.user_id == user_id,
            WorkoutSession.start_time >= start_date
        ).all()
        
        muscle_data = {}
        for exercise in exercises:
            for activation in exercise.muscle_activations:
                if activation.muscle_name not in muscle_data:
                    muscle_data[activation.muscle_name] = {
                        'total_volume': 0,
                        'last_trained': None,
                        'activation_counts': {
                            'PRIMARY': 0,
                            'SECONDARY': 0,
                            'TERTIARY': 0
                        }
                    }
                
                data = muscle_data[activation.muscle_name]
                data['total_volume'] += activation.estimated_volume
                data['activation_counts'][activation.activation_level] += 1
                
                exercise_time = exercise.timestamp or exercise.session.start_time
                if not data['last_trained'] or exercise_time > data['last_trained']:
                    data['last_trained'] = exercise_time
        
        return muscle_data
