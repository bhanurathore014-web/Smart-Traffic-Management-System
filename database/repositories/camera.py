"""database/repositories/camera.py — Camera-specific queries."""

from __future__ import annotations

from sqlalchemy import select

from database.models.camera import Camera, CameraStatus
from database.repositories.base import BaseRepository


class CameraRepository(BaseRepository[Camera]):
    model = Camera

    async def get_active_cameras(self) -> list[Camera]:
        """Return all cameras with status=active."""
        stmt = select(Camera).where(Camera.status == CameraStatus.ACTIVE.value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_location(self, location_fragment: str) -> list[Camera]:
        """Case-insensitive partial match on location field."""
        stmt = select(Camera).where(
            Camera.location.ilike(f"%{location_fragment}%")
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_status(self, camera_id: str, status: CameraStatus) -> Camera:
        """Update a single camera's status."""
        return await self.update(camera_id, {"status": status.value})
