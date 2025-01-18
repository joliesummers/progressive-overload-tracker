# Progressive Overload Workout Tracker

A smart workout tracking application that uses AI to help users track their muscle coverage and progressive overload over time.

## Features
- Natural language workout input via chat interface
- Automatic muscle group tracking and analysis
- Progressive overload monitoring
- Sentiment analysis for workout sessions
- Comprehensive workout analytics and visualization
- Advanced Progress Tracking (Added 2025-01-16)
  - Automated performance metrics calculation
  - Historical data aggregation
  - AI-powered workout insights
  - Exercise and muscle-group specific progress tracking
  - Custom performance period analysis

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: React with TypeScript
- Database: PostgreSQL 15
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

## AI Chat Integration

The app features an intelligent chat interface powered by Claude 3.5 Haiku via Amazon Bedrock. The chat system provides workout analysis, muscle activation insights, and training recommendations.

### Chat Features
- Natural language workout analysis
- Automatic muscle activation detection
- Real-time training recommendations
- Progressive overload suggestions
- Form and technique guidance

### Technical Implementation

#### AI Model
- **Model**: Claude 3.5 Haiku
- **Provider**: Amazon Bedrock
- **API Version**: `bedrock-2023-05-31`
- **Model ID**: `anthropic.claude-3-haiku-20240307-v1:0`

#### Message Flow
1. User sends workout description via chat interface
2. Backend formats message with specialized fitness analysis prompt
3. Claude 3.5 Haiku analyzes the workout and provides structured response
4. System extracts muscle activation data and recommendations
5. Frontend displays analysis with muscle visualization

#### Response Format
The system provides structured workout analysis including:
- Detailed workout summary (sets, reps, weight)
- Primary and secondary muscle activation percentages
- Training intensity analysis
- Form notes and recommendations
- Progressive overload guidance

### Environment Setup

Add the following to your `.env` file:
```env
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Example Usage

```typescript
// Frontend: Send message to chat
await bedrockService.sendMessage(
  "I did 3 sets of bench press at 185 lbs for 8 reps",
  (message) => {
    // Handle message chunks
    console.log(message);
  },
  (muscleData) => {
    // Handle muscle activation data
    updateMuscleVisualization(muscleData);
  }
);
```

```python
# Backend: Process workout
async def process_workout(workout_text: str):
    async for chunk in bedrock_service.stream_agent_response(workout_text):
        if chunk["type"] == "message":
            # Handle workout analysis
            yield chunk
        elif chunk["type"] == "muscle_data":
            # Handle muscle activation data
            yield chunk
```

### Error Handling
The system includes robust error handling for:
- API connection issues
- Malformed responses
- Rate limiting
- Token limits
- Response validation

For more details on the implementation, see the [Chat Integration Status](TODO.md#chat-integration-status) section in TODO.md.

## Data Pipeline

The Progressive Overload app uses a sophisticated data pipeline for processing workout data:

1. Input Processing
   - Natural language processing via Claude Sonnet 3.5
   - Automatic exercise and set parsing
   - Muscle activation analysis

2. Storage Layer
   - PostgreSQL database with SQLAlchemy ORM
   - Efficient transaction management
   - Robust error handling

3. Output Processing
   - Performance metric tracking
   - Historical data aggregation
   - AI-powered insight generation
   - Progress analysis across exercises and muscle groups
   - Custom time period analysis

### Progress Tracking Models

The app uses several models to track user progress:

```python
# Progress Metrics
- Exercise-specific metrics (volume, max weight, total reps)
- Muscle group activation tracking
- Performance aggregates over time
- AI-generated workout insights

# Example Usage
from app.services.output_processing_service import OutputProcessingService

# Initialize service
output_service = OutputProcessingService(db_session)

# Get user insights
insights = output_service.get_user_insights(user_id=1, limit=5)

# Aggregate performance data
weekly_stats = output_service.aggregate_performance(user_id=1, days=7)
```

## Getting Started
Instructions for setting up development environment coming soon.

## License
MIT License
