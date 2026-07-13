"""database/repositories/traffic_record.py — High-throughput detection queries."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from database.models.traffic_record import TrafficRecord
from database.repositories.base import BaseRepository


class TrafficRecordRepository(BaseRepository[TrafficRecord]):
    model = TrafficRecord

    async def bulk_insert_detections(self, rows: list[dict]) -> int:
        """Bulk-insert detection events with minimal ORM overhead.

        Each dict must contain at minimum: camera_id, timestamp, direction.
        Returns number of rows inserted.
        """
        return await self.bulk_create(rows)

    async def get_density_by_window(
        self,
        camera_id: str,
        start: datetime,
        end: datetime,
    ) -> dict:
        """Return count and avg_speed for a time window (used for real-time density)."""
        stmt = (
            select(
                func.count(TrafficRecord.id).label("count"),
                func.avg(TrafficRecord.speed_kmh).label("avg_speed"),
            )
            .where(TrafficRecord.camera_id == camera_id)
            .where(TrafficRecord.timestamp >= start)
            .where(TrafficRecord.timestamp <= end)
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return {
            "count": row.count or 0,
            "avg_speed": round(float(row.avg_speed or 0), 2),
        }

    async def get_recent(
        self, camera_id: str, *, limit: int = 50
    ) -> list[TrafficRecord]:
        """Latest N records for a given camera, newest first."""
        stmt = (
            select(TrafficRecord)
            .where(TrafficRecord.camera_id == camera_id)
            .order_by(TrafficRecord.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        camera_id: str,
        start: datetime,
        end: datetime,
        *,
        limit: int = 1000,
    ) -> list[TrafficRecord]:
        """Records for a camera between two timestamps."""
        stmt = (
            select(TrafficRecord)
            .where(TrafficRecord.camera_id == camera_id)
            .where(TrafficRecord.timestamp.between(start, end))
            .order_by(TrafficRecord.timestamp)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
