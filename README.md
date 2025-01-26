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

## AWS Bedrock Integration

The application uses AWS Bedrock Agent for natural language processing of workout data. The agent analyzes workout descriptions and extracts information about:
- Primary and secondary muscles worked
- Volume calculations for each muscle group
- Exercise recommendations

### Configuration
Required environment variables for Bedrock:
```
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=<your-model-id>
BEDROCK_AGENT_ID=<your-agent-id>
BEDROCK_AGENT_ALIAS_ID=<your-agent-alias-id>
```

### API Endpoints
The chat functionality is accessible through:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/chat/` (note the trailing slash)

### Testing
Test the chat endpoint using curl:
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I did 3 sets of squats with 135lbs today"}'
```

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

### Data Flow Architecture

The application follows a streamlined data flow for processing workout information:

1. **Chat Input → Bedrock Processing**
   - User inputs workout information via chat interface
   - Chat route (`/backend/app/routes/chat.py`) forwards input to BedrockAgentService
   - Amazon Bedrock processes the natural language input

2. **AI Analysis → JSON Structure**
   - Bedrock returns structured JSON containing:
     - Exercise details (name, sets, reps, weight)
     - Movement patterns
     - Equipment used
     - Performance metrics (RPE, tempo)
     - Duration and rest periods
     - Muscle activation data

3. **Integration → Storage**
   - IntegrationService processes the Bedrock response
   - WorkoutStorageService saves data to PostgreSQL database
   - Stores complete exercise data including:
     - Basic metrics (sets, reps, weight)
     - Performance data (RPE, tempo)
     - Metadata (equipment, difficulty, duration)
     - Muscle activation records

4. **Analytics Access**
   - Stored data is available through analytics endpoints
   - Supports comprehensive workout analysis
   - Enables progress tracking and visualization

### Expected JSON Format

```json
{
  "exercise": {
    "name": "string",
    "movement_pattern": "string",
    "total_volume": 0.0,
    "notes": "string",
    "sets": {
      "count": 0,
      "reps": 0,
      "weight": 0.0,
      "rpe": 0.0,
      "tempo": "string"
    },
    "metadata": {
      "equipment": "string",
      "difficulty": "string",
      "estimated_duration": 0,
      "rest_period": 0
    }
  },
  "muscle_activations": [
    {
      "muscle_name": "string",
      "activation_level": "PRIMARY|SECONDARY",
      "estimated_volume": 0.0
    }
  ]
}
```

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

## Data Storage Implementation

### Database Schema
The `exercises` table stores detailed information about each exercise performed in a workout session:

```sql
Table "public.exercises"
Column             Type              Nullable  Description
------------------+------------------+---------+------------
id                integer           not null  Primary key
session_id        integer                    References workout_sessions(id)
name              varchar                    Exercise name
movement_pattern  varchar                    Type of movement (e.g., push, pull)
notes             varchar                    Additional notes
num_sets          integer                    Number of sets performed
reps              json                       Array of reps per set
weight            json                       Array of weights per set
rpe               double precision           Rate of Perceived Exertion
tempo             varchar                    Exercise tempo (e.g., "3-1-3")
total_volume      double precision           Total volume for the exercise
equipment         varchar                    Equipment used
difficulty        varchar                    Exercise difficulty level
estimated_duration integer                   Estimated duration in minutes
rest_period       integer                    Rest period in seconds
```

Key features:
- All fields are nullable to accommodate varying inputs
- `reps` and `weight` use JSON type to store arrays
- Proper indexing on id and name columns
- Foreign key relationship with workout_sessions table

### Data Handling
- Arrays (reps and weights) are stored as JSON in the database and automatically converted to Python lists in the application code
- The Exercise model includes a `to_dict()` method for proper serialization
- Comprehensive error handling and logging throughout the storage service
- Full integration with AWS Bedrock for exercise analysis

### Exercise Data Storage

The application stores exercise data using a one-to-many relationship between exercises and muscle activations. Each exercise can have multiple muscle activations, with each activation recording:
- Primary/secondary muscle involvement
- Activation percentage
- Estimated volume
- Volume multiplier based on activation level

Example Exercise Storage:
```json
{
    "exercise": {
        "name": "Bench Press",
        "movement_pattern": "Push",
        "sets": {
            "count": 3,
            "reps": 8,
            "weight": 135,
            "rpe": 7
        },
        "total_volume": 3240
    },
    "muscle_activations": [
        {
            "muscle_name": "Pectoralis Major",
            "activation_level": "PRIMARY",
            "estimated_volume": 1620
        },
        {
            "muscle_name": "Triceps Brachii",
            "activation_level": "PRIMARY",
            "estimated_volume": 972
        }
    ]
}
```

### Volume Calculation

The system calculates muscle-specific volume using:
1. Base volume (sets × reps × weight)
2. Activation level multipliers:
   - PRIMARY: 100% of volume
   - SECONDARY: 50% of volume
3. Muscle-specific activation percentages

### API Endpoints

Key endpoints for data storage:
- `POST /api/workout/store-exercise`: Store exercise data with muscle activations
- `POST /api/workout/start-session`: Create a new workout session
- `PUT /api/workout/end-session`: End an active workout session

## Getting Started
Instructions for setting up development environment coming soon.

## License
MIT License
