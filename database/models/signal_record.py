"""
database/models/signal_record.py
==================================
SignalRecord — traffic signal phase change log.

Every time the adaptive signal controller changes phase, one record is
written so we can reconstruct full signal history and measure green-time
optimisation gains.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.camera import Camera


class SignalPhase(str, Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    ALL_RED = "all_red"       # clearance phase
    EMERGENCY = "emergency"   # emergency vehicle override


class SignalTrigger(str, Enum):
    ADAPTIVE = "adaptive"         # AI-controlled
    FIXED = "fixed"               # Timer-based fallback
    EMERGENCY = "emergency"       # Emergency override
    MANUAL = "manual"             # Operator override


class SignalRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One signal phase transition at a camera/intersection."""

    __tablename__ = "signal_records"
    __table_args__ = (
        CheckConstraint("duration_seconds >= 0", name="ck_signal_duration_positive"),
        Index("ix_signal_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_signal_timestamp", "timestamp"),
        {"comment": "Signal phase change log — one row per phase transition"},
    )

    # FK
    camera_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        comment="Camera / intersection this phase applies to",
    )

    # Phase data
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Phase-start timestamp (UTC)",
    )
    phase: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Signal colour / phase enum",
    )
    duration_seconds: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
        comment="Planned duration of this phase in seconds",
    )
    actual_duration_seconds: Mapped[float | None] = mapped_column(
        nullable=True,
        comment="Actual duration recorded after phase ends",
    )
    triggered_by: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SignalTrigger.FIXED.value,
        comment="What caused this phase change",
    )
    lane_id: Mapped[int | None] = mapped_column(nullable=True, comment="Specific lane (null = intersection-wide)")
    vehicle_count_at_trigger: Mapped[int | None] = mapped_column(
        nullable=True, comment="Queue length that triggered adaptive change"
    )

    # Relationship
    camera: Mapped["Camera"] = relationship("Camera", back_populates="signal_records")

    def __repr__(self) -> str:
        return (
            f"<SignalRecord id={self.id!r} camera={self.camera_id!r} "
            f"phase={self.phase!r} duration={self.duration_seconds}s>"
        )
