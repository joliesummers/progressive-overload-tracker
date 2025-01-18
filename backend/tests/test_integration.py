import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.integration_service import IntegrationService
from app.services.cache_service import CacheService
from app.services.report_service import ReportService
from app.services.analysis_service import AnalysisService
from app.models.database import get_db, Base, engine
from app.main import app
import json

# Set up test database
Base.metadata.create_all(bind=engine)

# Test client setup
client = TestClient(app)

# Sample workout data
SAMPLE_WORKOUTS = [
    "Did 3 sets of bench press: 135lbs for 8 reps, 155lbs for 6 reps, and 175lbs for 4 reps",
    "Completed 4 sets of squats with 225lbs, 12 reps each set",
    "Deadlift session: 3 sets at 275lbs for 5 reps each"
]

@pytest.fixture
def db():
    """Database session fixture"""
    try:
        db = next(get_db())
        yield db
    finally:
        db.close()

@pytest.fixture
def integration_service(db):
    """Integration service fixture"""
    return IntegrationService(db)

@pytest.fixture
def cache_service():
    """Cache service fixture"""
    return CacheService()

@pytest.mark.asyncio
async def test_complete_workout_pipeline(integration_service, db):
    """Test the complete workout processing pipeline"""
    # Process a workout
    result = await integration_service.process_workout(1, SAMPLE_WORKOUTS[0])
    
    assert result["session_id"] is not None
    assert result["exercises_processed"] > 0
    assert len(result["insights"]) > 0
    assert len(result["next_steps"]) > 0
    
    # Verify cache
    cached_result = integration_service.cache_service.get(
        integration_service.cache_service.generate_key(
            "workout_analysis",
            user_id=1,
            workout_text=SAMPLE_WORKOUTS[0]
        )
    )
    assert cached_result is not None

@pytest.mark.asyncio
async def test_dashboard_data(integration_service):
    """Test dashboard data generation"""
    # Get dashboard data
    dashboard = await integration_service.get_user_dashboard(1)
    
    assert "progress_report" in dashboard
    assert "muscle_balance" in dashboard
    assert "workout_frequency" in dashboard
    assert "recommendations" in dashboard

def test_analysis_features(db):
    """Test individual analysis features"""
    analysis_service = AnalysisService(db)
    
    # Test progression analysis
    progression = analysis_service.analyze_volume_progression(1)
    assert isinstance(progression, dict)
    
    # Test muscle balance
    balance = analysis_service.analyze_muscle_balance(1)
    assert isinstance(balance, list)
    
    # Test workout frequency
    frequency = analysis_service.analyze_workout_frequency(1)
    assert isinstance(frequency, dict)
    assert "total_sessions" in frequency
    assert "consistency_score" in frequency

def test_report_generation(db):
    """Test report generation features"""
    report_service = ReportService(db)
    
    # Generate progress report
    report = report_service.generate_progress_report(1)
    assert report.period_start < report.period_end
    assert isinstance(report.total_volume, float)
    assert isinstance(report.achievements, list)
    
    # Test recommendations
    recommendations = report_service.generate_recommendations(1)
    assert isinstance(recommendations, list)
    if recommendations:
        assert hasattr(recommendations[0], "exercise_name")
        assert hasattr(recommendations[0], "reason")

def test_cache_operations(cache_service):
    """Test cache operations"""
    test_key = "test:key"
    test_data = {"test": "data"}
    
    # Set cache
    cache_service.set(test_key, test_data)
    
    # Get cache
    cached = cache_service.get(test_key)
    assert cached == test_data
    
    # Delete cache
    cache_service.delete(test_key)
    assert cache_service.get(test_key) is None

@pytest.mark.asyncio
async def test_api_endpoints():
    """Test API endpoints"""
    # Test chat endpoint
    chat_response = client.post(
        "/chat",
        json={"message": SAMPLE_WORKOUTS[0]}
    )
    assert chat_response.status_code == 200
    assert "workout_data" in chat_response.json()
    
    # Test progress report endpoint
    progress_response = client.get("/reports/progress")
    assert progress_response.status_code == 200
    
    # Test recommendations endpoint
    recommendations_response = client.get("/reports/recommendations")
    assert recommendations_response.status_code == 200
    
    # Test analysis endpoints
    analysis_response = client.get("/analysis/muscle-balance")
    assert analysis_response.status_code == 200

@pytest.mark.asyncio
async def test_error_handling(integration_service):
    """Test error handling"""
    # Test with invalid workout text
    with pytest.raises(ValueError):
        await integration_service.process_workout(1, "")
    
    # Test with invalid user
    with pytest.raises(Exception):
        await integration_service.process_workout(-1, SAMPLE_WORKOUTS[0])

async def run_all_tests(db):
    """Run all tests"""
    integration_service = IntegrationService(db)
    cache_service = CacheService()
    
    print("\nRunning integration tests...")
    
    # Run pipeline test
    print("\nTesting complete workout pipeline...")
    await test_complete_workout_pipeline(integration_service, db)
    print("✓ Pipeline test passed")
    
    # Run dashboard test
    print("\nTesting dashboard generation...")
    await test_dashboard_data(integration_service)
    print("✓ Dashboard test passed")
    
    # Run analysis test
    print("\nTesting analysis features...")
    test_analysis_features(db)
    print("✓ Analysis test passed")
    
    # Run report test
    print("\nTesting report generation...")
    test_report_generation(db)
    print("✓ Report test passed")
    
    # Run cache test
    print("\nTesting cache operations...")
    test_cache_operations(cache_service)
    print("✓ Cache test passed")
    
    # Run API test
    print("\nTesting API endpoints...")
    await test_api_endpoints()
    print("✓ API test passed")
    
    # Run error handling test
    print("\nTesting error handling...")
    await test_error_handling(integration_service)
    print("✓ Error handling test passed")
    
    print("\nAll tests completed successfully! 🎉")
