from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Union
from ..services.bedrock_agent_service import BedrockAgentService

router = APIRouter()
agent_service = BedrockAgentService()

class ChatRequest(BaseModel):
    message: str

class MuscleData(BaseModel):
    primary_muscles: List[tuple[str, float]]
    secondary_muscles: List[tuple[str, float]]
    total_volume: float

class ChatResponse(BaseModel):
    message: str
    muscle_data: Optional[MuscleData] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the Bedrock agent and get a response with structured muscle data if available.
    """
    try:
        # Get response from agent
        response = agent_service.invoke_agent_with_retry(request.message)
        
        if isinstance(response, dict) and 'muscle_data' in response:
            return ChatResponse(
                message=response['text'],
                muscle_data=MuscleData(**response['muscle_data'])
            )
        else:
            return ChatResponse(message=response)
        
    except Exception as e:
        print(f"Chat error details: {str(e)}")  
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get response from agent: {str(e)}"
        )
