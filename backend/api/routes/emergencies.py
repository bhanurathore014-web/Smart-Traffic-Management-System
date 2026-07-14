from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import EmergencyEventRepository
from backend.api.schemas.emergency import EmergencyEventCreate, EmergencyEventUpdate, EmergencyEventResponse

router = APIRouter()

@router.post("/", response_model=EmergencyEventResponse, status_code=201)
async def report_emergency(event_in: EmergencyEventCreate, db: AsyncSession = Depends(get_db)):
    repo = EmergencyEventRepository(db)
    event = await repo.create(event_in.model_dump(exclude_none=True))
    await db.commit()
    return event

@router.get("/active", response_model=list[EmergencyEventResponse])
async def list_active_emergencies(db: AsyncSession = Depends(get_db)):
    repo = EmergencyEventRepository(db)
    return await repo.get_active_emergencies()

@router.post("/{event_id}/resolve", response_model=EmergencyEventResponse)
async def resolve_emergency(event_id: str, db: AsyncSession = Depends(get_db)):
    repo = EmergencyEventRepository(db)
    try:
        event = await repo.resolve_event(event_id)
        await db.commit()
        return event
    except ValueError:
        raise HTTPException(status_code=404, detail="Emergency event not found")

@router.patch("/{event_id}", response_model=EmergencyEventResponse)
async def update_emergency(event_id: str, event_in: EmergencyEventUpdate, db: AsyncSession = Depends(get_db)):
    repo = EmergencyEventRepository(db)
    try:
        update_data = event_in.model_dump(exclude_unset=True)
        if not update_data:
            return await repo.get_or_raise(event_id)
        event = await repo.update(event_id, update_data)
        await db.commit()
        return event
    except ValueError:
        raise HTTPException(status_code=404, detail="Emergency event not found")
