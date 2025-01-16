from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.chat import router as chat_router
from .routes.analytics import router as analytics_router
from .routes.exercise import router as exercise_router
from .routes.workout import router as workout_router
from .routes.test import router as test_router
from .models.database import engine, Base
from .models.user import User
from .models.workout import WorkoutSession, Exercise, ExerciseSet, MuscleActivation
from .middleware.request_logging import request_logging_middleware
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Add middleware in order
app.middleware("http")(request_logging_middleware)  # Add request logging first

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Print startup message
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Progressive Overload Backend API")
    
    # Log registered routes with detailed information
    logger.debug("=== Registered Routes ===")
    for route in app.routes:
        logger.debug(f"\nRoute: {route.path}")
        logger.debug(f"  Methods: {route.methods}")
        logger.debug(f"  Name: {route.name}")
        logger.debug(f"  Endpoint: {route.endpoint.__name__ if hasattr(route, 'endpoint') else 'N/A'}")
        logger.debug(f"  Response Model: {getattr(route, 'response_model', 'N/A')}")
        logger.debug(f"  Tags: {getattr(route, 'tags', [])}")
        logger.debug("  Dependencies:")
        for dep in getattr(route, 'dependencies', []):
            logger.debug(f"    - {dep}")
    logger.debug("=====================")

# Include routers with debug logging
logger.debug("Registering routers...")

@app.get("/api/direct-test", include_in_schema=True)
async def direct_test():
    """Test endpoint directly on app"""
    return {"message": "direct test"}

# Register analytics router
logger.debug("Registering analytics router...")
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

# Register test router
logger.debug("Registering test router...")
app.include_router(test_router, prefix="/api/test", tags=["test"])

logger.debug("Registering chat router...")
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

logger.debug("Registering exercise router...")
app.include_router(exercise_router, prefix="/api/exercise", tags=["exercise"])

logger.debug("Registering workout router...")
app.include_router(workout_router, prefix="/api/workout", tags=["workout"])

# Debug print all routes after all routers are registered
logger.debug("=== All Registered Routes ===")
for route in app.routes:
    logger.debug(f"Route: {route.path} [{','.join(route.methods)}] -> {route.endpoint.__name__}")
logger.debug("===========================")

@app.get("/api/")
async def root():
    return {"message": "Progressive Overload Backend API"}
