from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.database import get_db
from ..services.report_service import ReportService
from pydantic import BaseModel
from datetime import datetime
from io import StringIO

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

class ExerciseRecommendationResponse(BaseModel):
    exercise_name: str
    reason: str
    priority: float
    target_muscles: List[str]
    suggested_volume: Optional[float]

class ProgressReportResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_volume: float
    session_count: int
    top_exercises: List[dict]
    muscle_coverage: dict
    achievements: List[str]
    areas_for_improvement: List[str]

@router.get("/progress", response_model=ProgressReportResponse)
async def get_progress_report(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get a comprehensive progress report"""
    report_service = ReportService(db)
    return report_service.generate_progress_report(1, days)  # TODO: Get real user_id

@router.get("/recommendations", response_model=List[ExerciseRecommendationResponse])
async def get_recommendations(
    db: Session = Depends(get_db)
):
    """Get personalized exercise recommendations"""
    report_service = ReportService(db)
    return report_service.generate_recommendations(1)  # TODO: Get real user_id

@router.get("/export")
async def export_progress_data(
    format: str = Query(default="json", regex="^(json|csv)$"),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Export progress data in specified format"""
    report_service = ReportService(db)
    data = report_service.export_progress_data(1, format)  # TODO: Get real user_id
    
    if format == "json":
        return StreamingResponse(
            StringIO(data),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="progress_report_{datetime.utcnow().date()}.json"'
            }
        )
    else:  # CSV
        return StreamingResponse(
            StringIO(data),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="progress_report_{datetime.utcnow().date()}.csv"'
            }
        )
