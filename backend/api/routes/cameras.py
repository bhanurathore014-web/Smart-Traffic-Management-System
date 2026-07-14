from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.deps import get_db
from database.repositories import CameraRepository
from backend.api.schemas.camera import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter()

@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    camera = await repo.create(camera_in.model_dump())
    return camera

@router.get("/", response_model=list[CameraResponse])
async def list_cameras(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    cameras = await repo.list(skip=skip, limit=limit)
    return cameras

@router.get("/active", response_model=list[CameraResponse])
async def list_active_cameras(db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    return await repo.get_active_cameras()

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    camera = await repo.get(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(camera_id: str, camera_in: CameraUpdate, db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    try:
        update_data = camera_in.model_dump(exclude_unset=True)
        if not update_data:
            return await repo.get_or_raise(camera_id)
        camera = await repo.update(camera_id, update_data)
        await db.commit()
        return camera
    except ValueError:
        raise HTTPException(status_code=404, detail="Camera not found")

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(camera_id: str, db: AsyncSession = Depends(get_db)):
    repo = CameraRepository(db)
    deleted = await repo.delete(camera_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Camera not found")
    await db.commit()
