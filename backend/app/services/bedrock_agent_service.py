import os
import json
import time
import boto3
import aioboto3
from typing import Generator, Optional, Dict, Any, Union, List, Tuple, AsyncGenerator
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.eventstream import EventStream
import logging
import uuid
from datetime import datetime, timedelta
import random
import asyncio
from ..core.settings import Settings
import traceback

logger = logging.getLogger(__name__)

class BedrockAgentService:
    def __init__(self):
        load_dotenv()
        
        # Load settings
        self.settings = Settings()
        
        # Validate AWS credentials
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-west-2')
        
        if not self.aws_access_key or not self.aws_secret_key:
            raise ValueError("AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) are required")
            
        self.session = aioboto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        logger.info("Successfully initialized Bedrock client")
            
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.agent_id = self.settings.agent_id
        self.agent_alias_id = self.settings.agent_alias_id

    async def _get_bedrock_client(self):
        """Get an async Bedrock client with proper credentials"""
        return aioboto3.Session().client(
            'bedrock-agent-runtime',  # Use bedrock-agent-runtime for Agent API
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )

    async def invoke_agent(self, message: str, max_retries: int = 3) -> Dict[str, Any]:
        """Invoke the Bedrock agent with retry logic"""
        retry_count = 0
        last_exception = None
        session_id = str(uuid.uuid4())
        
        while retry_count < max_retries:
            try:
                logger.debug(f"Attempting to invoke Bedrock agent (attempt {retry_count + 1}/{max_retries})")
                
                async with await self._get_bedrock_client() as bedrock_runtime:
                    logger.debug("Created Bedrock runtime client")
                    
                    # Get system prompt and format input
                    system_prompt = self._get_system_prompt()
                    formatted_input = f"{system_prompt}\n\nUser workout: {message}\n\nResponse:"
                    
                    # Prepare request parameters
                    params = {
                        "agentId": self.agent_id,
                        "agentAliasId": self.agent_alias_id,
                        "sessionId": session_id,  # Keep same session ID across retries
                        "inputText": formatted_input,
                        "enableTrace": True
                    }
                    
                    logger.debug(f"Request params: {json.dumps(params, indent=2)}")
                    
                    try:
                        # Invoke agent with timeout
                        response = await asyncio.wait_for(
                            bedrock_runtime.invoke_agent(**params),
                            timeout=30.0  # 30 second timeout
                        )
                        
                        # Parse response from event stream
                        logger.debug(f"Raw response type: {type(response)}")
                        logger.debug(f"Raw response: {response}")
                        
                        # Read from event stream
                        response_text = None
                        if "completion" in response:
                            try:
                                async for event in response["completion"]:
                                    logger.debug(f"Event: {event}")
                                    if "chunk" in event and "bytes" in event["chunk"]:
                                        chunk_data = json.loads(event["chunk"]["bytes"].decode())
                                        logger.debug(f"Chunk data: {chunk_data}")
                                        
                                        if isinstance(chunk_data, dict):
                                            # Extract the actual response from the chunk data
                                            if "display_message" in chunk_data and "structured_data" in chunk_data:
                                                response_text = chunk_data
                                                break
                                            
                                            # If the response is nested in a content field
                                            if "content" in chunk_data:
                                                content = chunk_data["content"]
                                                if isinstance(content, str):
                                                    # Try to parse the content as JSON
                                                    try:
                                                        content_json = json.loads(content)
                                                        if isinstance(content_json, dict) and "display_message" in content_json and "structured_data" in content_json:
                                                            response_text = content_json
                                                            break
                                                    except json.JSONDecodeError:
                                                        pass
                            except Exception as e:
                                logger.error(f"Error processing event stream: {str(e)}")
                                logger.error(f"Traceback: {traceback.format_exc()}")
                                raise
                        
                        if not response_text:
                            raise ValueError("Failed to extract valid response from event stream")
                        
                        return response_text
                        
                    except asyncio.TimeoutError:
                        logger.error("Timeout waiting for Bedrock response")
                        raise
                        
            except Exception as e:
                logger.error(f"Error invoking Bedrock agent: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                last_exception = e
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(self.retry_delay * retry_count)  # Exponential backoff
                else:
                    raise last_exception

    def _get_system_prompt(self) -> str:
        """Get the system prompt for workout analysis"""
        return """You are a workout analysis assistant. For each workout description, analyze the exercise and return a JSON response in this EXACT format:
{
    "display_message": "string (human-readable breakdown of the workout with muscle activation and volume)",
    "structured_data": {
        "exercises": [{
            "name": "string (e.g., 'Bench Press', 'Squat')",
            "movement_pattern": "string (e.g., 'Push', 'Pull', 'Squat', 'Hinge')",
            "num_sets": number,
            "reps": [number] (array of reps per set),
            "weight": [number] (array of weights in lbs per set),
            "rpe": number (optional, Rate of Perceived Exertion 1-10),
            "tempo": "string (optional, e.g., '3-1-3' for eccentric-pause-concentric)",
            "total_volume": number (total volume for all sets),
            "notes": "string (optional analysis of form, tips, etc.)",
            "equipment": "string (e.g., 'Barbell', 'Dumbbell')",
            "difficulty": "string (e.g., 'Beginner', 'Intermediate')",
            "estimated_duration": number (in minutes),
            "rest_period": number (in seconds),
            "muscle_activations": [{
                "muscle_name": "string",
                "activation_level": "string (PRIMARY, SECONDARY, TERTIARY)",
                "estimated_volume": number
            }]
        }]
    }
}
"""

async def test_model():
    """Test the Bedrock model with sample inputs"""
    print("\nTesting Bedrock Model Responses with Streaming:")
    print("=" * 50)
    
    test_input = """Please analyze this full workout session in detail:
        1. Bench Press: 3x8 @ 135lbs
        2. Squats: 4x6 @ 225lbs
        3. Lat Pulldowns: 3x10 @ 120lbs
        
        For each exercise, please provide:
        1. Muscles worked (primary and secondary)
        2. Total volume calculation
        3. Intensity level (based on typical 1RM)
        4. Recovery recommendations
        5. Form tips and common mistakes to avoid
        6. Progressive overload suggestions
        7. Alternative exercises"""
    
    print("\nTest Case 1:")
    print(f"Input: {test_input}")
    print("-" * 30 + "\n")
    
    service = BedrockAgentService()
    
    print("Streaming Response:")
    response = await service.invoke_agent(test_input)
    print(response)
    
    print("=" * 50)
    print("\nTesting retry logic:")
    response = await service.invoke_agent(test_input)
    print("\nResponse with retry:")
    print(response)
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_model())
