"""database/repositories/analytics.py — Hourly analytics upsert and trend queries."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from database.models.analytics_hourly import AnalyticsHourly
from database.repositories.base import BaseRepository


def _floor_to_hour(dt: datetime) -> datetime:
    """Floor a datetime to the start of its UTC hour."""
    utc = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return utc.replace(minute=0, second=0, microsecond=0)


class AnalyticsRepository(BaseRepository[AnalyticsHourly]):
    model = AnalyticsHourly

    async def upsert_hourly_bucket(
        self,
        camera_id: str,
        hour_bucket: datetime,
        data: dict,
    ) -> AnalyticsHourly:
        """Insert or update a single hour bucket.

        Idempotent: calling multiple times with the same (camera_id, hour_bucket)
        updates rather than duplicates.
        """
        bucket = _floor_to_hour(hour_bucket)

        # Try to find existing row
        stmt = select(AnalyticsHourly).where(
            AnalyticsHourly.camera_id == camera_id,
            AnalyticsHourly.hour_bucket == bucket,
        )
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return await self.update(existing.id, data)
        else:
            return await self.create({"camera_id": camera_id, "hour_bucket": bucket, **data})

    async def get_trend(
        self,
        camera_id: str,
        *,
        hours: int = 24,
    ) -> list[AnalyticsHourly]:
        """Return the last N hours of analytics for a camera, oldest first."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = (
            select(AnalyticsHourly)
            .where(AnalyticsHourly.camera_id == camera_id)
            .where(AnalyticsHourly.hour_bucket >= since)
            .order_by(AnalyticsHourly.hour_bucket)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_cameras_latest(self) -> list[AnalyticsHourly]:
        """Return the most recent complete hour bucket for each camera."""
        # Subquery: max hour_bucket per camera
        from sqlalchemy import func

        subq = (
            select(
                AnalyticsHourly.camera_id,
                func.max(AnalyticsHourly.hour_bucket).label("max_bucket"),
            )
            .where(AnalyticsHourly.is_complete.is_(True))
            .group_by(AnalyticsHourly.camera_id)
            .subquery()
        )
        stmt = select(AnalyticsHourly).join(
            subq,
            (AnalyticsHourly.camera_id == subq.c.camera_id)
            & (AnalyticsHourly.hour_bucket == subq.c.max_bucket),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_complete(self, camera_id: str, hour_bucket: datetime) -> None:
        """Mark a bucket as finalized (called when the hour has fully elapsed)."""
        bucket = _floor_to_hour(hour_bucket)
        await self.update_where(
            {"camera_id": camera_id, "hour_bucket": bucket},
            {"is_complete": True},
        )
