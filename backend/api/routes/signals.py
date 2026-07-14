from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import SignalRepository
from backend.api.schemas.signal import SignalRecordCreate, SignalRecordResponse

router = APIRouter()

@router.post("/", response_model=SignalRecordResponse, status_code=201)
async def create_signal_record(record_in: SignalRecordCreate, db: AsyncSession = Depends(get_db)):
    repo = SignalRepository(db)
    record = await repo.create(record_in.model_dump(exclude_none=True))
    await db.commit()
    return record

@router.get("/{camera_id}/last", response_model=SignalRecordResponse)
async def get_last_phase(camera_id: str, db: AsyncSession = Depends(get_db)):
    repo = SignalRepository(db)
    record = await repo.get_last_phase(camera_id)
    if not record:
        raise HTTPException(status_code=404, detail="No signal records found for this camera")
    return record

@router.get("/{camera_id}/history", response_model=list[SignalRecordResponse])
async def get_phase_history(camera_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    repo = SignalRepository(db)
    return await repo.get_phase_history(camera_id, limit=limit)

@router.get("/{camera_id}/emergencies", response_model=list[SignalRecordResponse])
async def get_emergency_overrides(camera_id: str, db: AsyncSession = Depends(get_db)):
    repo = SignalRepository(db)
    return await repo.get_emergency_overrides(camera_id)
