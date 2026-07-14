from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import NumberPlateRepository
from backend.api.schemas.plate import NumberPlateCreate, NumberPlateResponse

router = APIRouter()

@router.post("/", response_model=NumberPlateResponse, status_code=201)
async def create_plate_read(plate_in: NumberPlateCreate, db: AsyncSession = Depends(get_db)):
    repo = NumberPlateRepository(db)
    plate = await repo.create(plate_in.model_dump(exclude_none=True))
    await db.commit()
    return plate

@router.get("/search/{plate_text}", response_model=list[NumberPlateResponse])
async def search_plate(plate_text: str, db: AsyncSession = Depends(get_db)):
    repo = NumberPlateRepository(db)
    return await repo.find_by_plate_text(plate_text)

@router.get("/{camera_id}/recent", response_model=list[NumberPlateResponse])
async def get_recent_plates(camera_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)):
    repo = NumberPlateRepository(db)
    return await repo.get_recent_detections(camera_id, limit=limit)

@router.get("/high-confidence", response_model=list[NumberPlateResponse])
async def get_high_confidence_plates(min_confidence: float = 0.85, db: AsyncSession = Depends(get_db)):
    repo = NumberPlateRepository(db)
    return await repo.get_high_confidence(min_confidence)
