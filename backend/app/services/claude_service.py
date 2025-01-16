import boto3
import json
from typing import Dict, List, Tuple
from ..core.settings import get_settings
from .exercise_analysis import ExerciseAnalysis, MuscleActivation
from sqlalchemy.orm import Session
from .workout_storage_service import WorkoutStorageService

class ClaudeService:
    """Service for interacting with Claude via AWS Bedrock"""
    
    def __init__(self, db: Session = None):
        settings = get_settings()
        print(f"Initializing ClaudeService with region: {settings.aws_region}, model: {settings.bedrock_model_id}")
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.model_id = settings.bedrock_model_id
        self.storage_service = WorkoutStorageService(db) if db else None

    def _create_exercise_prompt(self, exercise_description: str) -> str:
        return f"""You are an expert personal trainer and exercise physiologist. Analyze this workout and break it down into structured data.
        For each exercise, determine:
        1. The primary muscles worked (activation level: PRIMARY)
        2. The secondary muscles worked (activation level: SECONDARY)
        3. The stabilizer muscles (activation level: TERTIARY)
        4. The movement pattern category
        5. Required equipment
        
        Format your response as JSON with this structure:
        {{
            "exercises": [
                {{
                    "name": "exercise name",
                    "muscle_activations": [
                        {{
                            "muscle_name": "muscle",
                            "activation_level": "PRIMARY/SECONDARY/TERTIARY",
                            "estimated_volume": float (0-1)
                        }}
                    ],
                    "movement_pattern": "pattern",
                    "equipment_needed": ["equipment1", "equipment2"]
                }}
            ]
        }}

        Workout to analyze: {exercise_description}"""

    async def analyze_exercise(self, exercise_description: str, session_id: int = None) -> List[ExerciseAnalysis]:
        """Analyze an exercise description to identify muscles worked and activation levels."""
        prompt = self._create_exercise_prompt(exercise_description)
        
        print(f"Making request to Bedrock with model ID: {self.model_id}")
        print(f"Request body: {json.dumps({'anthropic_version': 'bedrock-2023-05-31', 'max_tokens': 4096, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.7}, indent=2)}")
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            })
        )
        
        print(f"Got response from Bedrock: {response}")
        response_body = json.loads(response.get('body').read())
        print(f"Parsed response body: {json.dumps(response_body, indent=2)}")
        
        analysis_json = json.loads(response_body['content'][0]['text'])
        
        # Convert JSON response to ExerciseAnalysis objects
        exercise_analyses = []
        for exercise in analysis_json['exercises']:
            muscle_activations = [
                MuscleActivation(
                    muscle_name=ma['muscle_name'],
                    activation_level=ma['activation_level'],
                    estimated_volume=ma['estimated_volume']
                )
                for ma in exercise['muscle_activations']
            ]
            
            analysis = ExerciseAnalysis(
                exercise_name=exercise['name'],
                muscle_activations=muscle_activations,
                movement_pattern=exercise['movement_pattern'],
                equipment_needed=exercise['equipment_needed']
            )
            exercise_analyses.append(analysis)
            
            # Store in database if session_id is provided and storage service is available
            if session_id and self.storage_service:
                self.storage_service.store_exercise_analysis(session_id, analysis)
        
        return exercise_analyses

    async def analyze_workout_sentiment(self, workout_notes: str) -> Tuple[float, str]:
        """Analyze workout notes for sentiment and extract key insights."""
        prompt = f"""Analyze the following workout notes for overall sentiment and key insights.
        Provide a sentiment score from -1.0 to 1.0, and a brief analysis of the workout experience.

        Notes: {workout_notes}"""

        print(f"Making request to Bedrock with model ID: {self.model_id}")
        print(f"Request body: {json.dumps({'anthropic_version': 'bedrock-2023-05-31', 'max_tokens': 4096, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.7}, indent=2)}")
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            })
        )
        
        print(f"Got response from Bedrock: {response}")
        response_body = json.loads(response.get('body').read())
        print(f"Parsed response body: {json.dumps(response_body, indent=2)}")
        
        analysis = response_body['content'][0]['text']
        
        # Extract sentiment score and insights
        try:
            # Parse the response to extract score and analysis
            lines = analysis.strip().split('\n')
            sentiment_score = float(lines[0].split(':')[1].strip())
            insights = '\n'.join(lines[1:]).strip()
            return sentiment_score, insights
        except Exception as e:
            print(f"Error parsing sentiment analysis: {str(e)}")
            return 0.0, f"Error parsing sentiment analysis: {str(e)}"

    async def get_completion(self, prompt: str) -> str:
        """Get a completion from Claude for a given prompt."""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": "You are a helpful AI assistant focused on fitness and exercise. Help users with their fitness-related questions and workout planning.",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            print(f"Making request to Bedrock with model ID: {self.model_id}")
            print(f"Request body: {json.dumps(request_body, indent=2)}")
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            print(f"Got response from Bedrock: {response}")
            response_body = json.loads(response.get('body').read())
            print(f"Parsed response body: {json.dumps(response_body, indent=2)}")
            
            return response_body['content'][0]['text'].strip()
            
        except Exception as e:
            print(f"Error in get_completion: {str(e)}")
            print(f"Error type: {type(e)}")
            if hasattr(e, '__dict__'):
                print(f"Error attributes: {e.__dict__}")
            if isinstance(e, boto3.exceptions.Boto3Error):
                print(f"Boto3 error response: {e.response if hasattr(e, 'response') else 'No response'}")
            raise Exception(f"Failed to get completion from Claude: {str(e)}")
