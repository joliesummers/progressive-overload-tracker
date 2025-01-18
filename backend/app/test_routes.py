from fastapi import FastAPI, APIRouter
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create a simple model
class TestData(BaseModel):
    name: str
    value: float
    timestamp: datetime

# Create router
router = APIRouter()

@router.get(
    "/test/endpoint1",
    response_model=dict,
    summary="Test Endpoint 1",
    tags=["test"]
)
async def test_endpoint1():
    """Test endpoint 1"""
    logger.debug("Received request for endpoint 1")
    return {"status": "ok", "endpoint": 1}

@router.get(
    "/test/endpoint2",
    response_model=dict,
    summary="Test Endpoint 2",
    tags=["test"]
)
async def test_endpoint2():
    """Test endpoint 2"""
    logger.debug("Received request for endpoint 2")
    return {"status": "ok", "endpoint": 2}

@router.get(
    "/test/data",
    response_model=List[TestData],
    summary="Test Data Endpoint",
    tags=["test"]
)
async def test_data():
    """Test data endpoint with complex response model"""
    logger.debug("Received request for data endpoint")
    return [
        TestData(
            name="test1",
            value=1.0,
            timestamp=datetime.utcnow()
        ),
        TestData(
            name="test2",
            value=2.0,
            timestamp=datetime.utcnow()
        )
    ]

# Include router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
