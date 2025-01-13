from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.claude_service import ClaudeService

router = APIRouter()
claude_service = ClaudeService()

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "anthropic.claude-3-haiku-20240307-v1:0"

class ChatResponse(BaseModel):
    message: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_claude(request: ChatRequest) -> ChatResponse:
    """
    Send a message to Claude and get a response.
    This is a lightweight endpoint that simply forwards the message and returns the response.
    """
    try:
        # Get response from Claude
        response = await claude_service.get_completion(request.message)
        return ChatResponse(message=response)
        
    except Exception as e:
        print(f"Chat error details: {str(e)}")  
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get response from Claude: {str(e)}"
        )
