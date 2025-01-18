import pytest
from datetime import datetime, timedelta
from app.services.bedrock_agent_service import BedrockAgentService

@pytest.fixture
def bedrock_service():
    return BedrockAgentService()

def test_get_volume_progression_weekly(bedrock_service):
    # Test weekly data
    data = bedrock_service.get_volume_progression('weekly')
    
    # Check if we get 7 days of data
    assert len(data) == 7
    
    # Check data structure
    for entry in data:
        assert 'date' in entry
        assert 'total_volume' in entry
        assert 'chest_volume' in entry
        assert 'back_volume' in entry
        assert 'legs_volume' in entry
        
        # Verify date format
        datetime.strptime(entry['date'], '%Y-%m-%d')
        
        # Verify volume values are positive numbers
        assert entry['total_volume'] > 0
        assert entry['chest_volume'] > 0
        assert entry['back_volume'] > 0
        assert entry['legs_volume'] > 0

def test_get_volume_progression_monthly(bedrock_service):
    # Test monthly data
    data = bedrock_service.get_volume_progression('monthly')
    
    # Check if we get 30 days of data
    assert len(data) == 30
    
    # Verify dates are in descending order
    dates = [datetime.strptime(entry['date'], '%Y-%m-%d') for entry in data]
    assert all(dates[i] >= dates[i+1] for i in range(len(dates)-1))

def test_calculate_daily_volume(bedrock_service):
    date = datetime.now().strftime('%Y-%m-%d')
    volume = bedrock_service._calculate_daily_volume(date)
    
    # Check if volume is within expected range
    assert 1000 <= volume <= 5000

def test_calculate_muscle_volume(bedrock_service):
    date = datetime.now().strftime('%Y-%m-%d')
    muscle_groups = ['Chest', 'Back', 'Legs']
    
    for muscle in muscle_groups:
        volume = bedrock_service._calculate_muscle_volume(date, muscle)
        # Check if volume is within expected range
        assert 200 <= volume <= 1000

def test_volume_progression_data_consistency(bedrock_service):
    data = bedrock_service.get_volume_progression('weekly')
    
    for entry in data:
        # Verify that total volume is greater than or equal to any individual muscle volume
        assert entry['total_volume'] >= entry['chest_volume']
        assert entry['total_volume'] >= entry['back_volume']
        assert entry['total_volume'] >= entry['legs_volume']
        
        # Verify that total volume is less than or equal to sum of all muscle volumes
        # (since some muscles might overlap in exercises)
        assert entry['total_volume'] <= (
            entry['chest_volume'] + 
            entry['back_volume'] + 
            entry['legs_volume']
        ) * 1.5  # Allow some overlap
