"""
database/models/emergency_event.py
====================================
EmergencyEvent — emergency vehicle detection and signal override log.

Records every detected emergency vehicle, the priority action taken,
and when the incident was resolved.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.camera import Camera
    from database.models.vehicle import Vehicle


class EmergencyType(str, Enum):
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE = "police"
    VVIP = "vvip"
    UNKNOWN = "unknown"


class EmergencyStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class EmergencyEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Detected emergency vehicle event with priority override record."""

    __tablename__ = "emergency_events"
    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 5", name="ck_emergency_priority_range"),
        CheckConstraint("detection_confidence >= 0.0 AND detection_confidence <= 1.0", name="ck_emergency_conf"),
        Index("ix_emergency_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_emergency_status", "status"),
        {"comment": "Emergency vehicle detection events and signal override log"},
    )

    # FK
    camera_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        comment="Camera that detected the emergency vehicle",
    )
    vehicle_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        comment="Linked vehicle record (null if unresolvable)",
    )

    # Event data
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Event detection time (UTC)",
    )
    emergency_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EmergencyType.UNKNOWN.value,
        comment="Type of emergency vehicle",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Override priority 1 (highest) to 5 (lowest)",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EmergencyStatus.ACTIVE.value,
        comment="Resolution status",
    )
    detection_confidence: Mapped[float | None] = mapped_column(
        nullable=True, comment="YOLO confidence 0-1"
    )

    # Resolution
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when event was resolved / vehicle passed",
    )
    green_corridor_activated: Mapped[bool] = mapped_column(
        default=False, comment="Whether a green corridor was triggered"
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="emergency_events")
    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle", back_populates="emergency_events")

    @property
    def duration_seconds(self) -> float | None:
        """Seconds from detection to resolution."""
        if self.resolved_at and self.timestamp:
            return (self.resolved_at - self.timestamp).total_seconds()
        return None

    def __repr__(self) -> str:
        return (
            f"<EmergencyEvent id={self.id!r} type={self.emergency_type!r} "
            f"priority={self.priority} status={self.status!r}>"
        )
