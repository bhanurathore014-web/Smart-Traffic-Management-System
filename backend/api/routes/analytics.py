from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import AnalyticsRepository
from backend.api.schemas.analytics import AnalyticsHourlyResponse

router = APIRouter()

@router.get("/{camera_id}/trend", response_model=list[AnalyticsHourlyResponse])
async def get_analytics_trend(camera_id: str, hours: int = 24, db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    return await repo.get_trend(camera_id, hours=hours)

@router.get("/{camera_id}/latest", response_model=AnalyticsHourlyResponse)
async def get_latest_analytics(camera_id: str, db: AsyncSession = Depends(get_db)):
    repo = AnalyticsRepository(db)
    record = await repo.get_latest_for_camera(camera_id)
    if not record:
        raise HTTPException(status_code=404, detail="No analytics found for this camera")
    return record
