from typing import Dict, List, Optional
from pydantic import BaseModel

class MuscleActivation(BaseModel):
    muscle_name: str
    activation_level: str  # PRIMARY, SECONDARY, TERTIARY
    estimated_volume: float

class ExerciseAnalysis(BaseModel):
    exercise_name: str
    muscle_activations: List[MuscleActivation]
    movement_pattern: str
    equipment_needed: List[str]
    notes: Optional[str] = None

class MockClaudeService:
    """
    Mock service for local development before AWS Bedrock integration
    Contains pre-defined exercise patterns for testing
    """
    def __init__(self):
        self.exercise_patterns = {
            "squat": {
                "movement_pattern": "squat",
                "muscle_activations": [
                    MuscleActivation(
                        muscle_name="quadriceps",
                        activation_level="PRIMARY",
                        estimated_volume=1.0
                    ),
                    MuscleActivation(
                        muscle_name="gluteus_maximus",
                        activation_level="PRIMARY",
                        estimated_volume=0.9
                    ),
                    MuscleActivation(
                        muscle_name="hamstrings",
                        activation_level="SECONDARY",
                        estimated_volume=0.6
                    ),
                    MuscleActivation(
                        muscle_name="core",
                        activation_level="TERTIARY",
                        estimated_volume=0.3
                    )
                ],
                "equipment_needed": ["barbell", "rack"],
            }
        }

    async def analyze_exercise(self, exercise_description: str) -> ExerciseAnalysis:
        """
        Mock exercise analysis for local development
        """
        # Simple keyword matching for testing
        exercise_type = next(
            (name for name in self.exercise_patterns.keys() 
             if name in exercise_description.lower()),
            "unknown"
        )
        
        if exercise_type in self.exercise_patterns:
            pattern = self.exercise_patterns[exercise_type]
            return ExerciseAnalysis(
                exercise_name=exercise_type,
                muscle_activations=pattern["muscle_activations"],
                movement_pattern=pattern["movement_pattern"],
                equipment_needed=pattern["equipment_needed"]
            )
        
        # Default response for unknown exercises
        return ExerciseAnalysis(
            exercise_name="unknown",
            muscle_activations=[],
            movement_pattern="unknown",
            equipment_needed=[]
        )

    async def analyze_workout_sentiment(self, workout_notes: str) -> Dict:
        """
        Mock sentiment analysis for local development
        """
        # Simple keyword-based sentiment analysis
        positive_words = ["great", "good", "strong", "energetic", "productive"]
        negative_words = ["tired", "weak", "bad", "painful", "exhausted"]
        
        words = workout_notes.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total
            
        return {
            "sentiment_score": sentiment_score,
            "analysis": "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
        }
