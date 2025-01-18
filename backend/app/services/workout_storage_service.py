from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
from ..models.exercise import (
    WorkoutSession, 
    Exercise, 
    MuscleActivation,
    MuscleActivationLevel,
    exercise_muscle_association
)

class WorkoutStorageService:
    """Service for storing workout data in the database"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_workout_session(self, user_id: int) -> WorkoutSession:
        """Create a new workout session for a user"""
        session = WorkoutSession(
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_workout_session(self, session_id: int) -> WorkoutSession:
        """End a workout session and calculate total volume"""
        session = self.db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        if not session:
            raise ValueError(f"No workout session found with id {session_id}")
        
        # Calculate total volume for the session
        total_volume = (
            self.db.query(func.sum(MuscleActivation.estimated_volume))
            .join(exercise_muscle_association, MuscleActivation.id == exercise_muscle_association.c.muscle_id)
            .join(Exercise, exercise_muscle_association.c.exercise_id == Exercise.id)
            .filter(Exercise.session_id == session_id)
            .scalar() or 0.0
        )
        
        session.end_time = datetime.utcnow()
        session.total_volume = total_volume
        self.db.commit()
        self.db.refresh(session)
        return session

    def store_exercise_data(self, session_id: int, exercise_name: str, muscle_data: Dict[str, Any]) -> Exercise:
        """Store exercise and muscle activation data from the Bedrock agent response"""
        try:
            # Extract exercise data
            exercise_data = muscle_data.get("exercise", {})
            sets_data = exercise_data.get("sets", {})
            metadata = exercise_data.get("metadata", {})
            
            print(f"Creating exercise record for session {session_id}")
            print(f"Exercise data: {exercise_data}")
            
            # Create exercise record
            exercise = self.create_exercise(
                session_id=session_id,
                name=exercise_name,
                movement_pattern=exercise_data.get("movement_pattern"),
                sets=sets_data.get("count", 0),
                reps=sets_data.get("reps", 0),
                weight=sets_data.get("weight", 0.0),
                total_volume=exercise_data.get("total_volume", 0.0),
                notes=exercise_data.get("notes"),
                equipment=metadata.get("equipment"),
                difficulty=metadata.get("difficulty"),
                estimated_duration=metadata.get("estimated_duration"),
                rest_period=metadata.get("rest_period"),
                rpe=sets_data.get("rpe"),
                tempo=sets_data.get("tempo")
            )
            
            print(f"Created exercise with ID: {exercise.id}")
            
            # Store muscle activations
            print(f"Processing {len(muscle_data.get('muscle_activations', []))} muscle activations")
            for activation in muscle_data.get("muscle_activations", []):
                print(f"Creating activation for {activation.get('muscle_name')} at {activation.get('activation_level')}")
                self.create_muscle_activation(
                    exercise_id=exercise.id,
                    muscle_name=activation.get("muscle_name"),
                    activation_level=activation.get("activation_level", "SECONDARY"),
                    estimated_volume=activation.get("estimated_volume", 0.0)
                )
            
            self.db.commit()
            print("Successfully stored all exercise data and muscle activations")
            return exercise
            
        except Exception as e:
            self.db.rollback()
            print(f"Error storing exercise data: {str(e)}")
            raise ValueError(f"Failed to store exercise data: {str(e)}")

    def create_exercise(self, session_id: int, name: str, movement_pattern: str, 
                       sets: int, reps: int, weight: float, total_volume: float,
                       notes: Optional[str] = None, equipment: Optional[str] = None,
                       difficulty: Optional[str] = None, estimated_duration: Optional[int] = None,
                       rest_period: Optional[int] = None, rpe: Optional[float] = None,
                       tempo: Optional[str] = None) -> Exercise:
        """Create a new exercise record"""
        exercise = Exercise(
            session_id=session_id,
            name=name,
            movement_pattern=movement_pattern,
            num_sets=sets,
            reps=reps,
            weight=weight,
            total_volume=total_volume,
            notes=notes,
            equipment=equipment,
            difficulty=difficulty,
            estimated_duration=estimated_duration,
            rest_period=rest_period,
            rpe=rpe,
            tempo=tempo
        )
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def create_muscle_activation(self, exercise_id: int, muscle_name: str,
                               activation_level: str, estimated_volume: float) -> MuscleActivation:
        """Create a new muscle activation record and associate it with an exercise"""
        try:
            # Create and persist the muscle activation
            muscle_activation = MuscleActivation(
                muscle_name=muscle_name,
                activation_level=MuscleActivationLevel[activation_level],
                estimated_volume=estimated_volume
            )
            self.db.add(muscle_activation)
            self.db.flush()  # Get the muscle activation ID

            # Create and persist the association
            stmt = exercise_muscle_association.insert().values(
                exercise_id=exercise_id,
                muscle_id=muscle_activation.id
            )
            self.db.execute(stmt)
            self.db.commit()  # Commit both the activation and association
            
            return muscle_activation
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create muscle activation: {str(e)}")

    def get_muscle_tracking(self, days: int = 30, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get tracking data for all muscles worked in the past N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query
        query = (
            self.db.query(
                MuscleActivation.muscle_name,
                func.sum(MuscleActivation.estimated_volume).label("total_volume"),
                func.count(MuscleActivation.id).label("exercise_count"),
                func.max(WorkoutSession.start_time).label("last_trained")
            )
            .select_from(MuscleActivation)
            .join(exercise_muscle_association, MuscleActivation.id == exercise_muscle_association.c.muscle_id)
            .join(Exercise, exercise_muscle_association.c.exercise_id == Exercise.id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(WorkoutSession.start_time >= cutoff_date)
            .filter(WorkoutSession.end_time.isnot(None))  # Only include completed sessions
        )
        
        # Add user filter if specified
        if user_id is not None:
            query = query.filter(WorkoutSession.user_id == user_id)
        
        # Execute query with grouping
        activations = (
            query.group_by(MuscleActivation.muscle_name)
            .all()
        )
        
        # Debug logging
        if not activations:
            print("No muscle activations found")
            # Check if there are any workout sessions
            sessions = (
                self.db.query(WorkoutSession)
                .filter(WorkoutSession.start_time >= cutoff_date)
                .filter(WorkoutSession.end_time.isnot(None))
                .all()
            )
            print(f"Found {len(sessions)} completed workout sessions")
        
        tracking_data = []
        for activation in activations:
            status = self._calculate_muscle_status(
                activation.total_volume,
                activation.exercise_count,
                activation.last_trained
            )
            tracking = {
                "muscle_name": activation.muscle_name,
                "total_volume": activation.total_volume,
                "exercise_count": activation.exercise_count,
                "last_trained": activation.last_trained,
                "status": status
            }
            tracking_data.append(tracking)
        
        return tracking_data

    def get_muscle_volume_data(self, timeframe: str = "weekly", user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get volume data for all muscles in the specified timeframe"""
        if timeframe == "weekly":
            cutoff_date = datetime.utcnow() - timedelta(days=7)
        else:  # monthly
            cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Base query
        query = (
            self.db.query(
                MuscleActivation.muscle_name,
                func.sum(MuscleActivation.estimated_volume).label("total_volume"),
                cast(WorkoutSession.start_time, Date).label("date")
            )
            .select_from(MuscleActivation)
            .join(exercise_muscle_association, MuscleActivation.id == exercise_muscle_association.c.muscle_id)
            .join(Exercise, exercise_muscle_association.c.exercise_id == Exercise.id)
            .join(WorkoutSession, Exercise.session_id == WorkoutSession.id)
            .filter(WorkoutSession.start_time >= cutoff_date)
            .filter(WorkoutSession.end_time.isnot(None))  # Only include completed sessions
        )
        
        # Add user filter if specified
        if user_id is not None:
            query = query.filter(WorkoutSession.user_id == user_id)
        
        # Execute query with grouping
        volume_data = (
            query.group_by(
                MuscleActivation.muscle_name,
                cast(WorkoutSession.start_time, Date)
            )
            .all()
        )
        
        # Debug logging
        if not volume_data:
            print("No volume data found")
            # Check if there are any workout sessions
            sessions = (
                self.db.query(WorkoutSession)
                .filter(WorkoutSession.start_time >= cutoff_date)
                .filter(WorkoutSession.end_time.isnot(None))
                .all()
            )
            print(f"Found {len(sessions)} completed workout sessions")
        
        return [
            {
                "muscle_name": data.muscle_name,
                "total_volume": data.total_volume,
                "date": data.date
            }
            for data in volume_data
        ]

    def _calculate_muscle_status(self, volume: float, count: int, last_trained: datetime) -> str:
        """Calculate the training status of a muscle based on volume and frequency"""
        days_since_trained = (datetime.utcnow() - last_trained).days
        
        if days_since_trained > 14:
            return "Undertrained"
        elif volume < 1000:  # Example threshold
            return "Maintenance"
        else:
            return "Optimal"
