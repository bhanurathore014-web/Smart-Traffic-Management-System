"""database/repositories/emergency_event.py — Emergency event queries."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from database.models.emergency_event import EmergencyEvent, EmergencyStatus
from database.repositories.base import BaseRepository


class EmergencyEventRepository(BaseRepository[EmergencyEvent]):
    model = EmergencyEvent

    async def get_active_emergencies(self) -> list[EmergencyEvent]:
        """Return all unresolved emergency events, highest priority first."""
        stmt = (
            select(EmergencyEvent)
            .where(EmergencyEvent.status == EmergencyStatus.ACTIVE.value)
            .order_by(EmergencyEvent.priority, EmergencyEvent.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def resolve_event(self, event_id: str) -> EmergencyEvent:
        """Mark an emergency event as resolved with current timestamp."""
        return await self.update(
            event_id,
            {
                "status": EmergencyStatus.RESOLVED.value,
                "resolved_at": datetime.now(timezone.utc),
            },
        )

    async def get_recent_by_camera(
        self, camera_id: str, *, limit: int = 10
    ) -> list[EmergencyEvent]:
        """Latest emergency events for a specific camera."""
        stmt = (
            select(EmergencyEvent)
            .where(EmergencyEvent.camera_id == camera_id)
            .order_by(EmergencyEvent.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
