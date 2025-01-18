import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.bedrock_agent_service import BedrockAgentService
import pytest_asyncio
import botocore.response
import aiohttp

class AsyncIterator:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)

class MockEventStream:
    def __init__(self, events):
        self.events = events
        self.iterator = AsyncIterator(events)

    def __aiter__(self):
        return self.iterator

class MockResponse:
    def __init__(self, events):
        self.events = events
        self._stream = MockEventStream(events)

    @property
    def raw_stream(self):
        return self._stream

    @property
    def status_code(self):
        return 200

@pytest_asyncio.fixture
async def bedrock_service():
    return BedrockAgentService()

@pytest.mark.asyncio
async def test_agent_basic_interaction(bedrock_service):
    test_input = "I did 3 sets of 10 reps at 135 lbs on bench press"
    mock_events = [{
        "chunk": {
            "bytes": json.dumps({
                "content": "Great work! Here's the analysis:\nPrimary muscles: Chest (80%), Front Deltoids (60%), Triceps (50%)\nSecondary muscles: Core (30%), Shoulders (20%)"
            }).encode()
        }
    }]
    
    with patch('aioboto3.Session', new_callable=AsyncMock) as mock_session:
        mock_client = AsyncMock()
        mock_client.invoke_agent = AsyncMock(return_value=MockResponse(mock_events))
        mock_session.return_value.client.return_value.__aenter__.return_value = mock_client
        
        result = await bedrock_service.invoke_agent(test_input)
        
        assert isinstance(result, dict)
        assert "completion" in result
        assert "muscle_data" in result
        assert result["muscle_data"]["total_volume"] > 0
        assert len(result["muscle_data"]["primary_muscles"]) > 0
        assert len(result["muscle_data"]["secondary_muscles"]) > 0

@pytest.mark.asyncio
async def test_agent_streaming(bedrock_service):
    test_input = "I did 3 sets of 10 reps at 135 lbs on bench press"
    mock_events = [
        {
            "chunk": {
                "bytes": json.dumps({
                    "content": "Processing your workout..."
                }).encode()
            }
        },
        {
            "chunk": {
                "bytes": json.dumps({
                    "content": "Analysis complete!"
                }).encode()
            }
        }
    ]
    
    with patch('aioboto3.Session', new_callable=AsyncMock) as mock_session:
        mock_client = AsyncMock()
        mock_client.invoke_agent = AsyncMock(return_value=MockResponse(mock_events))
        mock_session.return_value.client.return_value.__aenter__.return_value = mock_client
        
        responses = []
        async for response in bedrock_service.invoke_agent_streaming(test_input):
            responses.append(response)
        
        assert len(responses) == 2
        assert "Processing your workout..." in responses[0]
        assert "Analysis complete!" in responses[1]

@pytest.mark.asyncio
async def test_agent_retry_logic(bedrock_service):
    test_input = "I did 3 sets of 10 reps at 135 lbs on bench press"
    mock_events = [{
        "chunk": {
            "bytes": json.dumps({
                "content": "Success after retry!"
            }).encode()
        }
    }]
    
    with patch('aioboto3.Session', new_callable=AsyncMock) as mock_session:
        mock_client = AsyncMock()
        mock_client.invoke_agent = AsyncMock(side_effect=[
            Exception("First attempt failed"),
            Exception("Second attempt failed"),
            MockResponse(mock_events)
        ])
        mock_session.return_value.client.return_value.__aenter__.return_value = mock_client
        
        result = await bedrock_service.invoke_agent(test_input)
        assert isinstance(result, dict)
        assert "completion" in result
        assert "Success after retry!" in result["completion"]

@pytest.mark.asyncio
async def test_volume_progression(bedrock_service):
    result = await bedrock_service.get_volume_progression('weekly')
    assert isinstance(result, list)
    assert len(result) == 7  # One week of data
    for data_point in result:
        assert 'date' in data_point
        assert 'total_volume' in data_point
        assert 'chest_volume' in data_point
        assert 'back_volume' in data_point
        assert 'legs_volume' in data_point

if __name__ == "__main__":
    pytest.main([__file__])
