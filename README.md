# Progressive Overload Workout Tracker

A smart workout tracking application that uses AI to help users track their muscle coverage and progressive overload over time.

## Features
- Natural language workout input via chat interface
- Automatic muscle group tracking and analysis
- Progressive overload monitoring
- Sentiment analysis for workout sessions
- Comprehensive workout analytics and visualization

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: React with TypeScript
- Database: PostgreSQL
- AI: Claude Sonnet 3.5 via Amazon Bedrock
- Infrastructure: AWS, Docker

## Bedrock Agent Integration

The Progressive Overload app uses a custom Amazon Bedrock agent for intelligent workout analysis and tracking. The agent is integrated through the `BedrockAgentService` class.

### Setup

1. Ensure you have the following environment variables in your `.env` file:
```env
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_AGENT_ID=your-agent-id
```

2. The agent service is automatically initialized when the backend starts.

### Usage Examples

#### Basic Agent Interaction
```python
from app.services.bedrock_agent_service import BedrockAgentService

# Initialize the service
agent = BedrockAgentService()

# Send a workout for analysis
response = agent.invoke_agent_with_retry(
    "I just completed 3 sets of bench press at 135 lbs for 8 reps each"
)
print(response)
```

#### Streaming Response
```python
# Get real-time responses from the agent
for chunk in agent.invoke_agent_streaming(
    "Analyze my workout: 4 sets of squats at 225 lbs for 5 reps"
):
    print(chunk, end='', flush=True)
```

#### Session Management
```python
# Maintain context across multiple interactions
session_id = "workout-session-1"

# First interaction
response1 = agent.invoke_agent(
    "I did bench press today",
    session_id
)

# Follow-up question in the same session
response2 = agent.invoke_agent(
    "How many exercises did I do?",
    session_id
)
```

### Testing

Run the test suite:
```bash
# Run all tests
python -m pytest backend/tests/test_bedrock_agent.py

# Run specific test
python -m pytest backend/tests/test_bedrock_agent.py -k test_agent_basic_interaction
```

### Features

- **Retry Logic**: Automatically handles transient errors with exponential backoff
- **Session Management**: Maintains conversation context across multiple interactions
- **Streaming Support**: Real-time response streaming for better user experience
- **Error Handling**: Robust error handling for various API failure scenarios

## Getting Started
Instructions for setting up development environment coming soon.

## License
MIT License
