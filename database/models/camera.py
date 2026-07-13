"""
database/models/camera.py
=========================
Camera — intersection-level CCTV device registry.

One camera represents one monitored intersection approach or lane group.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.traffic_record import TrafficRecord
    from database.models.signal_record import SignalRecord
    from database.models.emergency_event import EmergencyEvent
    from database.models.analytics_hourly import AnalyticsHourly


class CameraStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAULT = "fault"


class Camera(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represents a physical CCTV / smart camera at an intersection."""

    __tablename__ = "cameras"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_camera_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_camera_lng"),
        Index("ix_cameras_status", "status"),
        Index("ix_cameras_location", "location"),
        {"comment": "CCTV camera device registry"},
    )

    # Core identity
    name: Mapped[str] = mapped_column(String(120), nullable=False, comment="Human-readable camera name")
    location: Mapped[str] = mapped_column(String(255), nullable=False, comment="Street / intersection description")

    # Geolocation
    latitude: Mapped[float] = mapped_column(Float, nullable=False, comment="Decimal degrees latitude")
    longitude: Mapped[float] = mapped_column(Float, nullable=False, comment="Decimal degrees longitude")

    # Connectivity
    stream_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="RTSP / HLS stream URL")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="Camera IP (IPv4 or IPv6)")

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=CameraStatus.ACTIVE.value,
        comment="Operational status enum",
    )
    num_lanes: Mapped[int] = mapped_column(default=4, comment="Number of monitored lanes")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    traffic_records: Mapped[list["TrafficRecord"]] = relationship(
        "TrafficRecord", back_populates="camera", lazy="selectin"
    )
    signal_records: Mapped[list["SignalRecord"]] = relationship(
        "SignalRecord", back_populates="camera", lazy="selectin"
    )
    emergency_events: Mapped[list["EmergencyEvent"]] = relationship(
        "EmergencyEvent", back_populates="camera", lazy="selectin"
    )
    analytics: Mapped[list["AnalyticsHourly"]] = relationship(
        "AnalyticsHourly", back_populates="camera", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Camera id={self.id!r} name={self.name!r} status={self.status!r}>"
