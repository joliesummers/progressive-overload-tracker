import asyncio
import os
from dotenv import load_dotenv
from app.services.claude_service import ClaudeService

async def test_bedrock_connection():
    """Test the connection to AWS Bedrock with Claude"""
    try:
        # Initialize the service
        claude = ClaudeService()
        
        # Test simple exercise analysis
        test_exercise = "3 sets of 10 pushups"
        result = await claude.analyze_exercise(test_exercise)
        
        print("\n=== Bedrock Connection Test Results ===")
        print("Connection: Success ✅")
        print("\nTest Exercise Analysis:")
        for exercise in result:
            print(f"\nExercise: {exercise.exercise_name}")
            print(f"Movement Pattern: {exercise.movement_pattern}")
            print("\nMuscle Activations:")
            for muscle in exercise.muscle_activations:
                print(f"- {muscle.muscle_name}: {muscle.activation_level} (Volume: {muscle.estimated_volume})")
            print("\nEquipment Needed:", ", ".join(exercise.equipment_needed))
            
    except Exception as e:
        print("\n=== Bedrock Connection Test Results ===")
        print("Connection: Failed ❌")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    asyncio.run(test_bedrock_connection())
