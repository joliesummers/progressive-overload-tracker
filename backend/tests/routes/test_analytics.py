import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.exercise import Exercise, MuscleActivation, MuscleVolumeData

def test_get_muscle_volume_weekly(test_client: TestClient, test_db: Session):
    # Create test data
    now = datetime.utcnow()
    
    # Create exercises across different days
    exercises = []
    for days_ago in range(10):  # Create 10 days of data
        exercise = Exercise(
            name="Bench Press",
            timestamp=now - timedelta(days=days_ago),
            sets=3,
            reps=10,
            weight=100.0
        )
        test_db.add(exercise)
        test_db.flush()
        
        # Add muscle activations for each exercise
        activations = [
            MuscleActivation(
                exercise_id=exercise.id,
                muscle_name="Chest",
                activation_level="PRIMARY",
                estimated_volume=300.0  # 3 sets * 10 reps * 100kg
            ),
            MuscleActivation(
                exercise_id=exercise.id,
                muscle_name="Triceps",
                activation_level="SECONDARY",
                estimated_volume=150.0  # Half the primary muscle volume
            )
        ]
        test_db.add_all(activations)
        exercises.append(exercise)
    
    test_db.commit()

    # Test weekly data
    response = test_client.get("/api/analytics/muscle-volume?timeframe=weekly")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify data structure
    for item in data:
        assert isinstance(item, dict)
        assert "muscle_name" in item
        assert "total_volume" in item
        assert "date" in item
        
        # Verify data types
        assert isinstance(item["muscle_name"], str)
        assert isinstance(item["total_volume"], float)
        assert isinstance(item["date"], str)
        
        # Verify date is within the last 7 days
        item_date = datetime.fromisoformat(item["date"])
        assert (now - item_date).days <= 7

def test_get_muscle_volume_monthly(test_client: TestClient, test_db: Session):
    # Create test data
    now = datetime.utcnow()
    
    # Create exercises across different days
    exercises = []
    for days_ago in range(35):  # Create 35 days of data
        exercise = Exercise(
            name="Deadlift",
            timestamp=now - timedelta(days=days_ago),
            sets=3,
            reps=5,
            weight=200.0
        )
        test_db.add(exercise)
        test_db.flush()
        
        # Add muscle activations for each exercise
        activations = [
            MuscleActivation(
                exercise_id=exercise.id,
                muscle_name="Back",
                activation_level="PRIMARY",
                estimated_volume=600.0  # 3 sets * 5 reps * 200kg
            ),
            MuscleActivation(
                exercise_id=exercise.id,
                muscle_name="Hamstrings",
                activation_level="SECONDARY",
                estimated_volume=300.0
            )
        ]
        test_db.add_all(activations)
        exercises.append(exercise)
    
    test_db.commit()

    # Test monthly data
    response = test_client.get("/api/analytics/muscle-volume?timeframe=monthly")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify data structure and constraints
    for item in data:
        assert isinstance(item, dict)
        assert all(key in item for key in ["muscle_name", "total_volume", "date"])
        
        # Verify date is within the last 30 days
        item_date = datetime.fromisoformat(item["date"])
        assert (now - item_date).days <= 30

def test_get_muscle_volume_invalid_timeframe(test_client: TestClient):
    response = test_client.get("/api/analytics/muscle-volume?timeframe=invalid")
    assert response.status_code == 422  # FastAPI validation error

def test_get_muscle_volume_empty_data(test_client: TestClient, test_db: Session):
    # Test with no data in database
    response = test_client.get("/api/analytics/muscle-volume?timeframe=weekly")
    assert response.status_code == 200
    assert response.json() == []
