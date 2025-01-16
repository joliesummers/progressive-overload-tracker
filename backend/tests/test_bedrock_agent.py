import os
import sys
import pytest
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.services.bedrock_agent_service import BedrockAgentService

# Load environment variables
load_dotenv()

@pytest.fixture
def agent_service():
    """Create a BedrockAgentService instance for testing"""
    return BedrockAgentService()

def test_agent_basic_interaction(agent_service):
    """Test basic interaction with the Bedrock agent"""
    test_input = "I just did 3 sets of bench press at 135 lbs for 8 reps each"
    
    # Test basic agent invocation
    response = agent_service.invoke_agent_with_retry(test_input)
    assert response is not None
    assert len(response) > 0
    print(f"\nBasic Agent Response:\n{response}")

def test_agent_streaming(agent_service):
    """Test streaming response from the Bedrock agent"""
    test_input = "Analyze my workout: 4 sets of squats at 225 lbs for 5 reps each"
    
    # Collect streaming response
    chunks = []
    for chunk in agent_service.invoke_agent_streaming(test_input):
        chunks.append(chunk)
        print(chunk, end='', flush=True)
    
    # Verify streaming response
    assert len(chunks) > 0
    complete_response = ''.join(chunks)
    assert len(complete_response) > 0

def test_agent_session_persistence(agent_service):
    """Test agent session persistence with multiple interactions"""
    session_id = "test-session-1"
    
    # First interaction
    response1 = agent_service.invoke_agent(
        "I did bench press today",
        session_id
    )
    assert response1 is not None
    
    # Follow-up question in same session
    response2 = agent_service.invoke_agent(
        "How many exercises did I do?",
        session_id
    )
    assert response2 is not None
    
    print(f"\nSession Test Results:")
    print(f"Initial Response: {response1}")
    print(f"Follow-up Response: {response2}")

def test_agent_error_handling(agent_service):
    """Test error handling and retry logic"""
    # Test with invalid session ID format
    with pytest.raises(Exception):
        agent_service.invoke_agent("Test message", "invalid/session/id")
    
    # Test retry logic with a valid request
    response = agent_service.invoke_agent_with_retry(
        "Test retry logic: analyze 3 sets of deadlifts at 315 lbs"
    )
    assert response is not None

if __name__ == "__main__":
    # Create service instance
    service = BedrockAgentService()
    
    # Run tests
    print("\nRunning Basic Interaction Test:")
    test_agent_basic_interaction(service)
    
    print("\nRunning Streaming Test:")
    test_agent_streaming(service)
    
    print("\nRunning Session Persistence Test:")
    test_agent_session_persistence(service)
    
    try:
        print("\nRunning Error Handling Test:")
        test_agent_error_handling(service)
    except Exception as e:
        print(f"Expected error occurred: {str(e)}")
