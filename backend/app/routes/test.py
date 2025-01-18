from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# Create router with explicit configuration
logger.debug("Creating test router...")
router = APIRouter(prefix="/test", tags=["test"])

@router.get(
    "/minimal",
    response_model=dict,
    summary="Minimal Test",
    description="Minimal test endpoint",
    status_code=200,
    include_in_schema=True,
    operation_id="minimal_test"
)
async def minimal_test():
    """Minimal test endpoint"""
    logger.debug("Received request for minimal test endpoint")
    return {"message": "minimal test"}
