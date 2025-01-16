import os
import json
import time
import re
import boto3
from typing import Generator, Optional, Dict, Any, Union, List, Tuple
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.eventstream import EventStream
import logging
import uuid

logger = logging.getLogger(__name__)

class BedrockAgentService:
    def __init__(self):
        load_dotenv()
        
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
            
        try:
            self.client = boto3.client(
                'bedrock-agent-runtime',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            logger.info("Successfully initialized Bedrock client")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
            raise ValueError(f"Failed to initialize AWS Bedrock client: {str(e)}")
            
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _extract_muscle_data(self, text: str) -> Dict[str, Any]:
        """Extract structured muscle data from agent response"""
        logger.debug(f"Extracting muscle data from text: {text}")
        
        result = {
            "primary_muscles": [],
            "secondary_muscles": [],
            "total_volume": 0.0
        }
        
        try:
            # Parse the structured response
            primary_muscles = []
            secondary_muscles = []
            total_volume = 0.0
            
            # Extract volume from exercise description (sets * reps * weight)
            volume_match = re.search(r'(\d+)\s*sets?\s*of\s*(\d+)\s*reps?\s*.*?(\d+)\s*lbs?\s*(?:per\s*hand)?', text, re.IGNORECASE)
            if volume_match:
                sets = int(volume_match.group(1))
                reps = int(volume_match.group(2))
                weight = int(volume_match.group(3))
                # If "per hand" is mentioned, double the weight
                if 'per hand' in text.lower():
                    weight *= 2
                total_volume = sets * reps * weight
                logger.debug(f"Calculated total volume from exercise: {total_volume}")
                result["total_volume"] = total_volume
            
            # Extract primary muscles with improved pattern matching
            primary_section = re.search(r'Primary.*?:(.*?)(?=Secondary|$)', text, re.DOTALL | re.IGNORECASE)
            if primary_section:
                primary_text = primary_section.group(1).strip()
                muscle_matches = re.finditer(r'([A-Za-z\s]+?)(?:\s*,|\s*\(|$)', primary_text)
                for match in muscle_matches:
                    muscle_name = match.group(1).strip()
                    if muscle_name and not muscle_name.lower().startswith(('and', 'with')):
                        primary_muscles.append((muscle_name, 0.6))  # Primary muscles get 60% activation
            
            # Extract secondary muscles with improved pattern matching
            secondary_section = re.search(r'Secondary.*?:(.*?)(?=\n\n|$)', text, re.DOTALL | re.IGNORECASE)
            if secondary_section:
                secondary_text = secondary_section.group(1).strip()
                muscle_matches = re.finditer(r'([A-Za-z\s]+?)(?:\s*,|\s*\(|$)', secondary_text)
                for match in muscle_matches:
                    muscle_name = match.group(1).strip()
                    if muscle_name and not muscle_name.lower().startswith(('and', 'with')):
                        secondary_muscles.append((muscle_name, 0.4))  # Secondary muscles get 40% activation
            
            result["primary_muscles"] = primary_muscles
            result["secondary_muscles"] = secondary_muscles
            
            logger.debug(f"Extracted muscle data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting muscle data: {str(e)}", exc_info=True)
            return result

    def _process_event_stream(self, event_stream: EventStream) -> Union[str, Dict[str, Any]]:
        """Process an EventStream response and extract the completion text and muscle data"""
        completion_text = ""
        for event in event_stream:
            if 'chunk' in event:
                chunk_text = event['chunk']['bytes'].decode()
                try:
                    chunk_data = json.loads(chunk_text)
                    if 'completion' in chunk_data:
                        completion_text += chunk_data['completion']
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text
                    completion_text += chunk_text
        
        logger.debug(f"Raw completion text: {completion_text}")
        
        # Extract structured data if possible
        try:
            if 'message' in completion_text:
                # Parse JSON response
                response_data = json.loads(completion_text)
                message = response_data['message']
            else:
                message = completion_text
                
            # First calculate volume from the input message
            input_volume = 0
            volume_match = re.search(r'(\d+)\s*sets?\s*of\s*(\d+)\s*reps?\s*.*?(\d+)\s*lbs?\s*(?:per\s*hand)?', message, re.IGNORECASE)
            if volume_match:
                sets = int(volume_match.group(1))
                reps = int(volume_match.group(2))
                weight = int(volume_match.group(3))
                if 'per hand' in message.lower():
                    weight *= 2
                input_volume = sets * reps * weight
                logger.debug(f"Calculated input volume: {input_volume}")
            
            # Then extract muscle data with the calculated volume
            muscle_data = self._extract_muscle_data(message)
            muscle_data["total_volume"] = input_volume
            
            return {
                "message": message,
                "muscle_data": muscle_data
            }
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}", exc_info=True)
            return completion_text

    def invoke_agent_with_retry(self, message: str, session_id: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Invoke the Bedrock agent with retry logic"""
        if not session_id:
            session_id = f"session-{int(time.time())}"
            
        for attempt in range(self.max_retries):
            try:
                return self.invoke_agent(message, session_id)
            except ClientError as e:
                if attempt < self.max_retries - 1:
                    logger.info(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                    print(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise e
    
    def invoke_agent(self, message: str, session_id: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Invoke the Bedrock agent using the Agent Runtime API"""
        try:
            # Calculate volume from the input message first
            input_volume = 0
            volume_match = re.search(r'(\d+)\s*sets?\s*of\s*(\d+)\s*reps?\s*.*?(\d+)\s*lbs?\s*(?:per\s*hand)?', message, re.IGNORECASE)
            if volume_match:
                sets = int(volume_match.group(1))
                reps = int(volume_match.group(2))
                weight = int(volume_match.group(3))
                if 'per hand' in message.lower():
                    weight *= 2
                input_volume = sets * reps * weight
                logger.debug(f"Calculated input volume: {input_volume}")

            # Invoke agent
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id or str(uuid.uuid4()),
                inputText=message
            )
            
            # Process response
            event_stream = response.get('completion')
            if event_stream:
                result = self._process_event_stream(event_stream)
                if isinstance(result, dict) and 'muscle_data' in result:
                    result['muscle_data']['total_volume'] = input_volume
                return result
            
            return "No response from agent"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Bedrock error: {error_code} - {error_message}")
            raise ValueError(f"AWS Bedrock error: {error_message}")
            
        except Exception as e:
            logger.error(f"Error invoking agent: {str(e)}")
            raise ValueError(f"Error invoking agent: {str(e)}")

    def invoke_agent_streaming(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Invoke the agent with streaming response"""
        if not session_id:
            session_id = f"session-{int(time.time())}"
            
        try:
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=message
            )
            
            for event in response['completion']:
                if 'chunk' in event:
                    chunk_text = event['chunk']['bytes'].decode()
                    try:
                        chunk_data = json.loads(chunk_text)
                        if 'completion' in chunk_data:
                            yield chunk_data['completion']
                    except json.JSONDecodeError:
                        yield chunk_text
        except Exception as e:
            logger.error(f"Error invoking agent: {str(e)}", exc_info=True)
            print(f"Error invoking agent: {str(e)}")
            raise e

def test_model():
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
    for response in service.invoke_agent_streaming(test_input):
        print(response)
    
    print("=" * 50)
    print("\nTesting retry logic:")
    response = service.invoke_agent_with_retry(test_input)
    print("\nResponse with retry:")
    print(response)
    print("=" * 50)

if __name__ == "__main__":
    test_model()
