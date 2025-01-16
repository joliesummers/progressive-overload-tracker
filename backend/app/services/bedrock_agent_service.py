import os
import json
import time
import re
import boto3
from typing import Generator, Optional, Dict, Any, Union, List, Tuple
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from botocore.eventstream import EventStream

class BedrockAgentService:
    def __init__(self):
        load_dotenv()
        self.client = boto3.client(
            'bedrock-agent-runtime',
            region_name=os.getenv('AWS_REGION', 'us-west-2'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.agent_id = os.getenv('BEDROCK_AGENT_ID')
        self.agent_alias_id = os.getenv('BEDROCK_AGENT_ALIAS_ID')
        
        if not self.agent_id:
            raise ValueError("BEDROCK_AGENT_ID environment variable is required")
        if not self.agent_alias_id:
            raise ValueError("BEDROCK_AGENT_ALIAS_ID environment variable is required")
            
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _extract_muscle_data(self, text: str) -> Dict[str, Any]:
        """Extract structured muscle data from agent response"""
        result = {
            "primary_muscles": [],
            "secondary_muscles": [],
            "total_volume": 0.0
        }
        
        # Extract primary muscles
        primary_match = re.search(r"Primary Muscles[:\s]+(.*?)(?=Secondary Muscles|\n\n|$)", text, re.DOTALL)
        if primary_match:
            muscles = re.findall(r"[•\-\*]\s*([^•\-\*\n]+)(?:\(?([\d,.]+)\s*lbs?\)?)?", primary_match.group(1))
            result["primary_muscles"] = [(m[0].strip(), float(m[1].replace(',', '')) if m[1] else 0.0) for m in muscles]
        
        # Extract secondary muscles
        secondary_match = re.search(r"Secondary Muscles[:\s]+(.*?)(?=\n\n|$)", text, re.DOTALL)
        if secondary_match:
            muscles = re.findall(r"[•\-\*]\s*([^•\-\*\n]+)(?:\(?([\d,.]+)\s*lbs?\)?)?", secondary_match.group(1))
            result["secondary_muscles"] = [(m[0].strip(), float(m[1].replace(',', '')) if m[1] else 0.0) for m in muscles]
        
        # Extract total volume
        volume_match = re.search(r"Total.*Volume:?\s*([\d,]+\.?\d*)\s*lbs?", text)
        if volume_match:
            result["total_volume"] = float(volume_match.group(1).replace(',', ''))
        
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
        
        # Extract structured data if possible
        try:
            muscle_data = self._extract_muscle_data(completion_text)
            return {
                "text": completion_text,
                "muscle_data": muscle_data
            }
        except Exception as e:
            print(f"Error extracting muscle data: {str(e)}")
            return completion_text

    def invoke_agent_with_retry(self, message: str, session_id: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """Invoke the Bedrock agent with retry logic"""
        if not session_id:
            session_id = f"session-{int(time.time())}"
            
        for attempt in range(self.max_retries):
            try:
                return self.invoke_agent(message, session_id)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                        continue
                raise e
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise e
        raise Exception("Max retries exceeded")

    def invoke_agent(self, message: str, session_id: str) -> Union[str, Dict[str, Any]]:
        """Invoke the Bedrock agent using the Agent Runtime API"""
        try:
            params = {
                'agentId': self.agent_id,
                'agentAliasId': self.agent_alias_id,
                'sessionId': session_id,
                'inputText': message
            }
            
            print(f"Invoking agent with params: {params}")  # Debug log
            response = self.client.invoke_agent(**params)
            
            if isinstance(response['completion'], EventStream):
                return self._process_event_stream(response['completion'])
            return response['completion']
            
        except Exception as e:
            print(f"Error invoking agent: {str(e)}")
            raise e

    def invoke_agent_streaming(self, message: str, session_id: Optional[str] = None) -> Generator[Union[str, Dict[str, Any]], None, None]:
        """Invoke the agent with streaming response"""
        if not session_id:
            session_id = f"session-{int(time.time())}"
            
        try:
            params = {
                'agentId': self.agent_id,
                'agentAliasId': self.agent_alias_id,
                'sessionId': session_id,
                'inputText': message,
                'enableTrace': True
            }
            
            print(f"Invoking agent streaming with params: {params}")  # Debug log
            response = self.client.invoke_agent(**params)
            
            if isinstance(response['completion'], EventStream):
                buffer = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk_text = event['chunk']['bytes'].decode()
                        try:
                            chunk_data = json.loads(chunk_text)
                            if 'completion' in chunk_data:
                                buffer += chunk_data['completion']
                        except json.JSONDecodeError:
                            # If not JSON, treat as plain text
                            buffer += chunk_text
                        
                        # Try to extract muscle data from the accumulated buffer
                        try:
                            muscle_data = self._extract_muscle_data(buffer)
                            yield {
                                "text": buffer,
                                "muscle_data": muscle_data
                            }
                            buffer = ""  # Reset buffer after successful extraction
                        except:
                            # If we can't extract muscle data yet, just yield the text
                            yield buffer
                            buffer = ""
            else:
                # If not streaming, simulate streaming with chunks
                completion = response['completion']
                chunk_size = 50
                for i in range(0, len(completion), chunk_size):
                    yield completion[i:i + chunk_size]
                    
        except Exception as e:
            print(f"Error in streaming response: {str(e)}")
            raise e

def test_model():
    agent = BedrockAgentService()
    test_cases = [
        # Test case with potential token limit
        """Please analyze this full workout session in detail:
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
    ]
    
    print("\nTesting Bedrock Model Responses with Streaming:")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        try:
            print(f"\nTest Case {i}:")
            print(f"Input: {test_input}")
            print("-" * 30)
            print("\nStreaming Response:")
            
            # Test streaming response
            for chunk in agent.invoke_agent_streaming(test_input):
                print(chunk, end='', flush=True)
            
            print("\n" + "=" * 50)
            
            # Test with retry logic
            print("\nTesting retry logic:")
            response = agent.invoke_agent_with_retry(test_input)
            print(f"\nResponse with retry:\n{response}")
            print("=" * 50)
            
        except Exception as e:
            print(f"Error in test case {i}: {str(e)}")
            continue
    
    return True

if __name__ == "__main__":
    test_model()
