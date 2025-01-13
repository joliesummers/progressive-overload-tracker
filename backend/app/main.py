from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from .routes.analytics import router as analytics_router
from .routes.exercise import router as exercise_router
from .routes.chat import router as chat_router

app = FastAPI(title="Progressive Overload API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to Progressive Overload API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
