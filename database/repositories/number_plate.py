"""database/repositories/number_plate.py — Number plate lookup queries."""

from __future__ import annotations

from sqlalchemy import select

from database.models.number_plate import NumberPlate
from database.repositories.base import BaseRepository


class NumberPlateRepository(BaseRepository[NumberPlate]):
    model = NumberPlate

    async def find_by_plate_text(self, plate_text: str) -> list[NumberPlate]:
        """Find all reads matching an exact plate text (case-insensitive)."""
        normalized = plate_text.upper().replace(" ", "").replace("-", "")
        stmt = (
            select(NumberPlate)
            .where(NumberPlate.plate_text_normalized == normalized)
            .order_by(NumberPlate.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_detections(
        self, camera_id: str, *, limit: int = 20
    ) -> list[NumberPlate]:
        """Recent plate reads associated with traffic records from a camera.

        Joins through traffic_records to filter by camera.
        """
        from database.models.traffic_record import TrafficRecord

        stmt = (
            select(NumberPlate)
            .join(TrafficRecord, TrafficRecord.number_plate_id == NumberPlate.id)
            .where(TrafficRecord.camera_id == camera_id)
            .order_by(NumberPlate.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_high_confidence(self, min_confidence: float = 0.85) -> list[NumberPlate]:
        """Return plates with confidence above threshold."""
        stmt = (
            select(NumberPlate)
            .where(NumberPlate.confidence >= min_confidence)
            .order_by(NumberPlate.confidence.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
