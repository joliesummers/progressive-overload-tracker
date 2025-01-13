import boto3
import json
from typing import Dict, List, Tuple
from ..core.settings import get_settings
from .exercise_analysis import ExerciseAnalysis, MuscleActivation

class ClaudeService:
    """Service for interacting with Claude via AWS Bedrock"""
    
    def __init__(self):
        settings = get_settings()
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.model_id = settings.bedrock_model_id

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

    async def analyze_exercise(self, exercise_description: str) -> List[ExerciseAnalysis]:
        """Analyze an exercise description to identify muscles worked and activation levels."""
        prompt = self._create_exercise_prompt(exercise_description)
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read())
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
        
        return exercise_analyses

    async def analyze_workout_sentiment(self, workout_notes: str) -> Tuple[float, str]:
        """Analyze workout notes for sentiment and extract key insights."""
        prompt = f"""Analyze the following workout notes for overall sentiment and key insights.
        Provide a sentiment score from -1.0 to 1.0, and a brief analysis of the workout experience.

        Notes: {workout_notes}"""

        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read())
        analysis = response_body['content'][0]['text']
        
        # Extract sentiment score and insights
        try:
            # Parse the response to extract score and analysis
            lines = analysis.strip().split('\n')
            sentiment_score = float(lines[0].split(':')[1].strip())
            insights = '\n'.join(lines[1:]).strip()
            return sentiment_score, insights
        except Exception as e:
            return 0.0, f"Error parsing sentiment analysis: {str(e)}"
