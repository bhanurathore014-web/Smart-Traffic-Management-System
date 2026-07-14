from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import TrafficRecordRepository
from backend.api.schemas.traffic import TrafficRecordCreate, TrafficRecordResponse, DensityResponse

router = APIRouter()

@router.post("/bulk", status_code=201)
async def bulk_insert_traffic(records: list[TrafficRecordCreate], db: AsyncSession = Depends(get_db)):
    repo = TrafficRecordRepository(db)
    count = await repo.bulk_insert_detections([r.model_dump(exclude_none=True) for r in records])
    await db.commit()
    return {"inserted": count}

@router.get("/{camera_id}/recent", response_model=list[TrafficRecordResponse])
async def get_recent_traffic(camera_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = TrafficRecordRepository(db)
    return await repo.get_recent(camera_id, limit=limit)

@router.get("/{camera_id}/density", response_model=DensityResponse)
async def get_traffic_density(camera_id: str, start: datetime, end: datetime, db: AsyncSession = Depends(get_db)):
    repo = TrafficRecordRepository(db)
    density = await repo.get_density_by_window(camera_id, start, end)
    return density
