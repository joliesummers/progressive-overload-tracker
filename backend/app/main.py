from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .services import MockClaudeService, ExerciseAnalysis
from .routes.auth import router as auth_router
from .routes.analytics import router as analytics_router
from .routes.exercise import router as exercise_router

app = FastAPI(title="Progressive Overload API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
claude_service = MockClaudeService()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])

@app.get("/")
async def root():
    return {"message": "Welcome to Progressive Overload API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
