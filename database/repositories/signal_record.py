"""database/repositories/signal_record.py — Signal record queries."""

from __future__ import annotations

from sqlalchemy import select

from database.models.signal_record import SignalRecord
from database.repositories.base import BaseRepository


class SignalRepository(BaseRepository[SignalRecord]):
    model = SignalRecord

    async def get_last_phase(self, camera_id: str) -> SignalRecord | None:
        """Return the most recently started signal record for a camera."""
        stmt = (
            select(SignalRecord)
            .where(SignalRecord.camera_id == camera_id)
            .order_by(SignalRecord.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_phase_history(
        self, camera_id: str, *, limit: int = 50
    ) -> list[SignalRecord]:
        """Recent N signal phase records for a camera, newest first."""
        stmt = (
            select(SignalRecord)
            .where(SignalRecord.camera_id == camera_id)
            .order_by(SignalRecord.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_emergency_overrides(self, camera_id: str) -> list[SignalRecord]:
        """Return all emergency-triggered phase records for a camera."""
        from database.models.signal_record import SignalTrigger

        stmt = (
            select(SignalRecord)
            .where(SignalRecord.camera_id == camera_id)
            .where(SignalRecord.triggered_by == SignalTrigger.EMERGENCY.value)
            .order_by(SignalRecord.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
