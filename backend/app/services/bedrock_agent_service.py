import os
import json
import time
import re
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
        self.agent_id = os.getenv('BEDROCK_AGENT_ID')
        self.agent_alias_id = os.getenv('BEDROCK_AGENT_ALIAS_ID')
        
        # Initialize exercise muscle map
        self.exercise_muscle_map = {
            "squat": {
                "primary": ["Quadriceps", "Glutes", "Hamstrings"],
                "secondary": ["Core", "Lower Back", "Calves"]
            },
            "bench press": {
                "primary": ["Chest", "Front Deltoids", "Triceps"],
                "secondary": ["Core", "Shoulders", "Biceps"]
            },
            "deadlift": {
                "primary": ["Lower Back", "Hamstrings", "Glutes"],
                "secondary": ["Upper Back", "Traps", "Core", "Forearms"]
            },
            "shoulder press": {
                "primary": ["Shoulders", "Triceps"],
                "secondary": ["Upper Back", "Core"]
            }
        }
        
        if not self.aws_access_key or not self.aws_secret_key:
            raise ValueError("AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) are required")
        if not self.agent_id:
            raise ValueError("BEDROCK_AGENT_ID environment variable is required")
        if not self.agent_alias_id:
            raise ValueError("BEDROCK_AGENT_ALIAS_ID environment variable is required")
            
        self.session = aioboto3.Session(
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        logger.info("Successfully initialized Bedrock client")
            
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    async def _get_client(self):
        """Get an async Bedrock client"""
        return await self.session.client('bedrock-agent-runtime').__aenter__()

    async def invoke_agent_with_retry(self, message: str, max_retries: int = 3) -> Dict[str, Any]:
        """Invoke the Bedrock agent with retry logic"""
        retry_count = 0
        last_exception = None
        
        while retry_count < max_retries:
            try:
                logger.debug(f"Attempting to invoke Bedrock agent (attempt {retry_count + 1}/{max_retries})")
                logger.debug(f"Using AWS credentials - Region: {self.aws_region}, Model ID: {self.settings.bedrock_model_id}")
                
                async with aioboto3.Session().client(
                    'bedrock-runtime',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.aws_region
                ) as bedrock_runtime:
                    logger.debug("Created Bedrock runtime client")
                    
                    try:
                        # Format message for Claude
                        formatted_message = self._format_claude_message(message)
                        
                        # Prepare request body for Claude
                        request_body = {
                            "prompt": formatted_message,
                            "max_tokens_to_sample": 2048,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "stop_sequences": []
                        }
                        
                        logger.debug(f"Formatted message being sent to Claude: {formatted_message}")
                        logger.debug(f"Full request body: {json.dumps(request_body, indent=2)}")
                        
                        # Invoke model with streaming
                        response = await bedrock_runtime.invoke_model_with_response_stream(
                            modelId=self.settings.bedrock_model_id,
                            body=json.dumps(request_body),
                            contentType='application/json',
                            accept='application/json'
                        )
                        logger.debug(f"Raw Bedrock response: {response}")
                        
                        # Extract completion from response
                        completion = await self._extract_completion(response)
                        logger.debug(f"Extracted completion: {completion}")
                        
                        return {
                            "completion": completion,
                            "session_id": str(uuid.uuid4()),
                            "request_id": response.get("ResponseMetadata", {}).get("RequestId", "")
                        }
                        
                    except ClientError as e:
                        error_code = e.response['Error']['Code']
                        error_message = e.response['Error']['Message']
                        logger.error(f"Bedrock ClientError: {error_code} - {error_message}")
                        last_exception = e
                        retry_count += 1
                        if retry_count < max_retries:
                            await asyncio.sleep(self.retry_delay * (2 ** retry_count))  # Exponential backoff
                        continue
                        
            except Exception as e:
                logger.error(f"Error invoking Bedrock agent: {str(e)}")
                last_exception = e
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** retry_count))  # Exponential backoff
                continue
                
        # If we've exhausted all retries, raise the last exception
        logger.error(f"Failed to invoke Bedrock agent after {max_retries} attempts")
        raise last_exception

    async def invoke_agent(self, message: str, session_id: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Invoke the Bedrock agent with a message
        
        Args:
            message: Message to send to the agent
            session_id: Optional session ID for continuing a conversation
            
        Returns:
            Response from the agent
        """
        try:
            return await self.invoke_agent_with_retry(message)
        except Exception as e:
            logger.error(f"Error invoking Bedrock agent: {str(e)}")
            raise

    async def invoke_agent_streaming(self, message: str) -> Generator[str, None, None]:
        """
        Stream responses from the Bedrock agent
        
        Args:
            message: Message to send to the agent
            
        Yields:
            Streamed responses from the agent
        """
        client = None
        try:
            client = await self._get_client()
            session_id = f"session-{int(time.time())}"
            response = await client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=message
            )

            # Get the response stream
            stream = getattr(response, 'raw_stream', None)
            if not stream:
                raise ValueError("No response stream found in response")

            async for event in stream:
                if event and 'chunk' in event:
                    try:
                        chunk = json.loads(event["chunk"]["bytes"].decode())
                        if "content" in chunk:
                            yield chunk["content"]
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode chunk: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            raise
        finally:
            if client:
                await client.__aexit__(None, None, None)

    async def invoke_model_with_stream(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Invoke the Bedrock model with streaming response"""
        try:
            async with aioboto3.Session().client(
                'bedrock-runtime',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            ) as bedrock_runtime:
                # Format message for Claude
                formatted_message = self._format_claude_message(message)
                
                # Prepare request body for Claude Messages API
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "assistant",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                logger.debug(f"Formatted message being sent to Claude: {formatted_message}")
                logger.debug(f"Full request body: {json.dumps(request_body, indent=2)}")
                
                # Invoke model with streaming
                response = await bedrock_runtime.invoke_model_with_response_stream(
                    modelId=self.settings.bedrock_model_id,
                    body=json.dumps(request_body),
                    contentType='application/json',
                    accept='application/json'
                )
                
                async for event in response['body']:
                    if event:
                        try:
                            # Parse the chunk
                            chunk = json.loads(event['chunk']['bytes'].decode())
                            logger.debug(f"Received chunk: {chunk}")
                            
                            if 'type' in chunk and chunk['type'] == 'message_start':
                                continue
                            
                            if 'type' in chunk and chunk['type'] == 'content_block_start':
                                continue
                            
                            if 'type' in chunk and chunk['type'] == 'content_block_delta':
                                if 'delta' in chunk and 'text' in chunk['delta']:
                                    yield {"type": "message", "message": chunk['delta']['text']}
                            
                            if 'type' in chunk and chunk['type'] == 'message_delta':
                                if 'delta' in chunk and 'text' in chunk['delta']:
                                    yield {"type": "message", "message": chunk['delta']['text']}
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode chunk: {e}")
                            continue
                        
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield {"type": "error", "error": str(e)}

    async def stream_agent_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent responses with muscle data extraction"""
        try:
            async with aioboto3.Session().client(
                'bedrock-runtime',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            ) as bedrock_runtime:
                # Format system prompt
                system_message = """You are a workout analysis assistant. For each workout description, analyze the exercise and return a JSON response in this EXACT format:

{
    "exercise": {
        "name": "string (e.g., 'Bench Press', 'Squat')",
        "movement_pattern": "string (e.g., 'Push', 'Pull', 'Squat', 'Hinge')",
        "sets": {
            "count": number,
            "reps": number,
            "weight": number (in lbs),
            "rpe": number (optional, Rate of Perceived Exertion 1-10),
            "tempo": "string (optional, e.g., '3-1-3' for eccentric-pause-concentric)"
        },
        "total_volume": number (sets * reps * weight),
        "notes": "string (optional analysis of form, tips, etc.)",
        "metadata": {
            "equipment": "string (e.g., 'Barbell', 'Dumbbell', 'Kettlebell', etc.)",
            "difficulty": "string (e.g., 'Beginner', 'Intermediate', 'Advanced')",
            "estimated_duration": number (in minutes),
            "rest_period": number (recommended rest between sets in seconds)
        }
    },
    "muscle_activations": [
        {
            "muscle_name": "string (standardized names like 'Quadriceps', 'Hamstrings', etc.)",
            "activation_level": "PRIMARY" or "SECONDARY" or "TERTIARY",
            "estimated_volume": number (percentage of total volume, should sum to 100%)"
        }
    ]
}

IMPORTANT:
1. Always return valid JSON that exactly matches this schema
2. For muscle_activations:
   - PRIMARY muscles are the main movers (60-100% activation)
   - SECONDARY muscles are supporting muscles (30-60% activation)
   - TERTIARY muscles are stabilizers (0-30% activation)
3. The total of estimated_volume across all muscles should equal 100%
4. Use standardized muscle names consistently
5. Calculate total_volume as (sets * reps * weight)
6. In metadata:
   - equipment should be standardized (Barbell, Dumbbell, Kettlebell, Machine, Bodyweight, etc.)
   - difficulty is based on movement complexity and load
   - estimated_duration includes all sets and recommended rest periods
   - rest_period is based on exercise intensity and movement pattern

Example for "3 sets of 12 reps bench press at 135 lbs":
{
    "exercise": {
        "name": "Bench Press",
        "movement_pattern": "Push",
        "sets": {
            "count": 3,
            "reps": 12,
            "weight": 135
        },
        "total_volume": 4860,
        "notes": "Compound pushing movement targeting chest development",
        "metadata": {
            "equipment": "Barbell",
            "difficulty": "Intermediate",
            "estimated_duration": 8,
            "rest_period": 90
        }
    },
    "muscle_activations": [
        {
            "muscle_name": "Chest",
            "activation_level": "PRIMARY",
            "estimated_volume": 50
        },
        {
            "muscle_name": "Triceps",
            "activation_level": "SECONDARY",
            "estimated_volume": 30
        },
        {
            "muscle_name": "Front Deltoids",
            "activation_level": "SECONDARY",
            "estimated_volume": 20
        }
    ]
}"""

                # Prepare request body for Claude Messages API
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [
                        {
                            "role": "assistant",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": message
                        }
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
                
                logger.debug(f"Request body: {json.dumps(request_body, indent=2)}")
                
                try:
                    # Invoke model without streaming
                    response = await bedrock_runtime.invoke_model(
                        modelId=self.settings.bedrock_model_id,
                        body=json.dumps(request_body).encode(),
                        contentType='application/json',
                        accept='application/json'
                    )
                    
                    # Get response body
                    if not isinstance(response, dict) or 'body' not in response:
                        raise ValueError(f"Unexpected response format: {response}")
                    
                    # Read response body
                    response_body = response['body']
                    if hasattr(response_body, 'read'):
                        response_bytes = await response_body.read()
                    else:
                        response_bytes = response_body
                        
                    if not response_bytes:
                        raise ValueError("Empty response from Bedrock")
                        
                    logger.debug(f"Raw response bytes: {response_bytes}")
                    response_str = response_bytes.decode('utf-8')
                    logger.debug(f"Decoded response string: {response_str}")
                    
                    response_data = json.loads(response_str)
                    logger.debug(f"Parsed response data: {response_data}")
                    
                    if 'content' in response_data:
                        # Extract text from content array
                        message = ""
                        for content_item in response_data['content']:
                            if content_item.get('type') == 'text':
                                message += content_item.get('text', '')
                        
                        # First yield the message
                        yield {"type": "message", "message": message}
                        
                        # Then try to extract and yield muscle data
                        try:
                            muscle_data = await self._extract_muscle_data(message)
                            if muscle_data:
                                yield {"type": "muscle_data", "muscle_data": muscle_data}
                        except Exception as e:
                            logger.error(f"Error extracting muscle data: {str(e)}")
                    else:
                        logger.error(f"Unexpected response format: {response_data}")
                        yield {"type": "error", "error": "Unexpected response format from Bedrock"}
                        
                except Exception as e:
                    logger.error(f"Error processing Bedrock response: {str(e)}")
                    logger.error(f"Exception type: {type(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    yield {"type": "error", "error": f"Error processing Bedrock response: {str(e)}"}
                        
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            yield {"type": "error", "error": str(e)}

    def _format_claude_message(self, message: str) -> str:
        """Format a message for Claude model with proper system prompt"""
        system_message = """You are a workout analysis assistant. For each workout description, analyze the exercise and return a JSON response in this EXACT format:

{
    "exercise": {
        "name": "string (e.g., 'Bench Press', 'Squat')",
        "movement_pattern": "string (e.g., 'Push', 'Pull', 'Squat', 'Hinge')",
        "sets": {
            "count": number,
            "reps": number,
            "weight": number (in lbs),
            "rpe": number (optional, Rate of Perceived Exertion 1-10),
            "tempo": "string (optional, e.g., '3-1-3' for eccentric-pause-concentric)"
        },
        "total_volume": number (sets * reps * weight),
        "notes": "string (optional analysis of form, tips, etc.)",
        "metadata": {
            "equipment": "string (e.g., 'Barbell', 'Dumbbell', 'Kettlebell', etc.)",
            "difficulty": "string (e.g., 'Beginner', 'Intermediate', 'Advanced')",
            "estimated_duration": number (in minutes),
            "rest_period": number (recommended rest between sets in seconds)
        }
    },
    "muscle_activations": [
        {
            "muscle_name": "string (standardized names like 'Quadriceps', 'Hamstrings', etc.)",
            "activation_level": "PRIMARY" or "SECONDARY" or "TERTIARY",
            "estimated_volume": number (percentage of total volume, should sum to 100%)"
        }
    ]
}

IMPORTANT:
1. Always return valid JSON that exactly matches this schema
2. For muscle_activations:
   - PRIMARY muscles are the main movers (60-100% activation)
   - SECONDARY muscles are supporting muscles (30-60% activation)
   - TERTIARY muscles are stabilizers (0-30% activation)
3. The total of estimated_volume across all muscles should equal 100%
4. Use standardized muscle names consistently
5. Calculate total_volume as (sets * reps * weight)
6. In metadata:
   - equipment should be standardized (Barbell, Dumbbell, Kettlebell, Machine, Bodyweight, etc.)
   - difficulty is based on movement complexity and load
   - estimated_duration includes all sets and recommended rest periods
   - rest_period is based on exercise intensity and movement pattern

Example for "3 sets of 12 reps bench press at 135 lbs":
{
    "exercise": {
        "name": "Bench Press",
        "movement_pattern": "Push",
        "sets": {
            "count": 3,
            "reps": 12,
            "weight": 135
        },
        "total_volume": 4860,
        "notes": "Compound pushing movement targeting chest development",
        "metadata": {
            "equipment": "Barbell",
            "difficulty": "Intermediate",
            "estimated_duration": 8,
            "rest_period": 90
        }
    },
    "muscle_activations": [
        {
            "muscle_name": "Chest",
            "activation_level": "PRIMARY",
            "estimated_volume": 50
        },
        {
            "muscle_name": "Triceps",
            "activation_level": "SECONDARY",
            "estimated_volume": 30
        },
        {
            "muscle_name": "Front Deltoids",
            "activation_level": "SECONDARY",
            "estimated_volume": 20
        }
    ]
}"""

        return f"\n\nAssistant: {system_message}\n\nHuman: {message}\n\nAssistant:"

    async def _extract_completion(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract completion from streaming response"""
        try:
            completion_text = ""
            async for event in response['body']:
                try:
                    # Parse chunk
                    chunk = json.loads(event['chunk']['bytes'].decode())
                    if "completion" in chunk:
                        completion_text += chunk["completion"]
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode chunk: {event}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
                    continue

            # Try to parse JSON from the completion text
            try:
                # Find JSON object in text (it might be surrounded by other text)
                json_match = re.search(r'\{[^{]*"exercise"[^}]*\}', completion_text)
                if json_match:
                    workout_data = json.loads(json_match.group())
                    return workout_data
                else:
                    logger.error("No valid JSON found in response")
                    return {"error": "No valid JSON found in response"}
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from completion: {completion_text}")
                return {"error": "Failed to parse JSON from response"}

        except Exception as e:
            logger.error(f"Error extracting completion: {str(e)}")
            return {"error": str(e)}

    async def _extract_muscle_data(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured muscle data from agent response"""
        try:
            # Try to find and parse JSON in the response
            json_match = re.search(r'\{[^{]*"exercise"[^}]*\}', text)
            if json_match:
                workout_data = json.loads(json_match.group())
                return workout_data
            else:
                logger.error("No valid JSON found in response")
                return None
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from text: {text}")
            return None
        except Exception as e:
            logger.error(f"Error extracting muscle data: {str(e)}")
            return None

    async def get_volume_progression(self, timeframe: str = 'weekly') -> List[Dict[str, Any]]:
        """Get volume progression data over time.
        
        Args:
            timeframe (str): 'weekly' or 'monthly' timeframe
            
        Returns:
            List of volume data points with date and total volume
        """
        try:
            days = 7 if timeframe == 'weekly' else 30
            
            # Query your database or data source for workout data
            # This is a placeholder for the actual implementation
            volume_data = []
            
            for day in range(days):
                # Calculate date for this data point
                current_date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                
                # Get volume data for this date
                daily_volume = {
                    'date': current_date,
                    'total_volume': await self._calculate_daily_volume(current_date),
                    'chest_volume': await self._calculate_muscle_volume(current_date, 'Chest'),
                    'back_volume': await self._calculate_muscle_volume(current_date, 'Back'),
                    'legs_volume': await self._calculate_muscle_volume(current_date, 'Legs'),
                }
                volume_data.append(daily_volume)
            
            return sorted(volume_data, key=lambda x: x['date'])
            
        except Exception as e:
            logger.error(f"Error getting volume progression: {str(e)}")
            raise
            
    async def _calculate_daily_volume(self, date: str) -> float:
        """Calculate total volume for a specific date."""
        # Placeholder - implement actual calculation based on your data source
        return random.uniform(1000, 5000)  # For testing purposes
        
    async def _calculate_muscle_volume(self, date: str, muscle_group: str) -> float:
        """Calculate volume for a specific muscle group on a date."""
        # Placeholder - implement actual calculation based on your data source
        return random.uniform(200, 1000)  # For testing purposes

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
    async for response in service.invoke_agent_streaming(test_input):
        print(response)
    
    print("=" * 50)
    print("\nTesting retry logic:")
    response = await service.invoke_agent_with_retry(test_input)
    print("\nResponse with retry:")
    print(response)
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_model())
