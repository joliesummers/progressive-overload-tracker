# Progressive Overload Workout Tracker

A smart workout tracking application that uses AI to help users optimize their fitness journey through intelligent workout analysis, muscle activation tracking, and progressive overload monitoring.

## Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [AI Integration](#ai-integration)
- [API Documentation](#api-documentation)
- [Development](#development)

## Quick Start

1. Clone the repository
2. Set up environment variables:
```env
# Create .env file with required credentials
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-agent-alias-id
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=progressive_overload
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

3. Start the services:
```bash
docker-compose up
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Features

- **Smart Workout Tracking**
  - Natural language workout input via chat interface
  - Automatic muscle group tracking and analysis
  - Progressive overload monitoring
  - Exercise and muscle-group specific progress tracking

- **AI-Powered Analysis**
  - Real-time workout feedback
  - Form and technique guidance
  - Training recommendations
  - Sentiment analysis for workout sessions

- **Comprehensive Analytics**
  - Muscle activation visualization
  - Performance metrics calculation
  - Historical data aggregation
  - Custom period analysis
  - AI-powered workout insights

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL 15
- **AI Model**: Claude 3.5 Haiku via Amazon Bedrock
- **Infrastructure**: AWS, Docker

## Setup

### Environment Configuration

Required environment variables:
```env
# AWS Configuration
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-agent-alias-id

# Database Configuration
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=progressive_overload
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Database Setup

The application uses PostgreSQL 15 as its primary database. The database connection is configured through environment variables and is automatically set up when running with Docker.

Default database configuration:
- Database Name: `progressive_overload`
- Host: `localhost` (or `db` when using Docker)
- Port: `5432`
- Default User: `postgres`

When using Docker, the database is automatically initialized with the correct schema. For manual setup:

1. Create the database:
```sql
CREATE DATABASE progressive_overload;
```

2. Run migrations:
```bash
# From the backend directory
alembic upgrade head
```

### Testing

Test the API endpoints:
```bash
# Test workout analysis
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I did 3 sets of squats with 135lbs today"}'

# Run test suite
python -m pytest backend/tests/
```

## AI Integration

The application leverages Claude 3.5 Haiku via AWS Bedrock for intelligent workout analysis:

### Features
- Natural language workout processing
- Automatic muscle activation detection
- Real-time training recommendations
- Progressive overload suggestions
- Form and technique guidance

### Message Flow
1. User submits workout description
2. Backend processes with specialized fitness analysis prompt
3. AI analyzes workout and provides structured response
4. System extracts muscle activation data
5. Frontend displays analysis with muscle visualization

## API Documentation

### Workout Endpoints
- `POST /api/workout/store-exercise`: Store exercise data
- `POST /api/workout/start-session`: Create workout session
- `PUT /api/workout/end-session`: End workout session
- `GET /api/workout/analysis`: Get workout analysis

### Chat Endpoints
- `POST /api/chat/`: Send workout for analysis
- `GET /api/chat/history`: Get chat history

## Development

### Code Examples

#### Frontend Chat Integration
```typescript
await bedrockService.sendMessage(
  "I did 3 sets of bench press at 185 lbs for 8 reps",
  (message) => console.log(message),
  (muscleData) => updateMuscleVisualization(muscleData)
);
```

#### Backend Workout Processing
```python
async def process_workout(workout_text: str):
    async for chunk in bedrock_service.stream_agent_response(workout_text):
        if chunk["type"] == "message":
            yield chunk
```

## Analytics Dashboard

### Muscle Activation Map

The Muscle Activation Map provides a visual representation of how well each muscle group is being trained. The visualization uses a radar chart where each axis represents a different muscle group. The further a point extends from the center, the better that muscle is being trained.

#### Activation Score Calculation

The activation score for each muscle is calculated using three key metrics, resulting in a score from 0-100:

1. **Volume Score (40% weight)**
   - Normalized based on the highest volume among all muscles
   - If a muscle has the highest volume, it gets 100 points
   - Other muscles are scored proportionally
   - Example: If Quads have 10,000 volume (highest) and Glutes have 5,000:
     * Quads = 100 points
     * Glutes = 50 points

2. **Frequency Score (40% weight)**
   - Based on the number of different exercises targeting the muscle
   - Each exercise contributes 25 points (capped at 100)
   - Score breakdown:
     * 1 exercise = 25 points
     * 2 exercises = 50 points
     * 3 exercises = 75 points
     * 4+ exercises = 100 points

3. **Recovery Score (20% weight)**
   - Based on the muscle's recovery status
   - Fully recovered = 100 points
   - Partially recovered = proportional points
   - Example: 50% recovered = 50 points

#### Final Score Calculation
```
Final Score = (Volume Score × 0.4) + (Frequency Score × 0.4) + (Recovery Score × 0.2)
```

#### Interpreting the Visualization

- **Longer Spikes** = Better trained muscles
- **Shorter Spikes** = Muscles needing more attention
- **Perfect Circle** = Perfectly balanced training
- **Irregular Shape** = Some muscle groups need more focus

Hover over any point to see detailed metrics including:
- Actual volume numbers
- Number of exercises targeting the muscle
- Current recovery status

Use this visualization to:
- Identify underworked muscle groups
- Ensure balanced training across all muscles
- Monitor recovery status
- Guide exercise selection for upcoming workouts

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
