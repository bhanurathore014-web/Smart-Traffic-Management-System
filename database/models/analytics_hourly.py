"""
database/models/analytics_hourly.py
=====================================
AnalyticsHourly — pre-aggregated per-camera, per-hour traffic metrics.

This table is the primary source for dashboard charts and avoids
expensive real-time aggregation queries on the large traffic_records table.
It is populated by a background aggregation job.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.camera import Camera


class AnalyticsHourly(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Pre-aggregated hourly traffic stats for one camera."""

    __tablename__ = "analytics_hourly"
    __table_args__ = (
        UniqueConstraint("camera_id", "hour_bucket", name="uq_analytics_camera_hour"),
        CheckConstraint("vehicle_count >= 0", name="ck_analytics_count_positive"),
        CheckConstraint("avg_speed_kmh >= 0", name="ck_analytics_speed_positive"),
        CheckConstraint("peak_density >= 0.0 AND peak_density <= 1.0", name="ck_analytics_density_range"),
        # Hot paths
        Index("ix_analytics_camera_hour", "camera_id", "hour_bucket"),
        Index("ix_analytics_hour_bucket", "hour_bucket"),
        {"comment": "Pre-aggregated hourly metrics for dashboard charts"},
    )

    # FK
    camera_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        comment="Camera this hour bucket belongs to",
    )

    # Time bucket — always floored to the start of the hour (UTC)
    hour_bucket: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Hour start timestamp (UTC) e.g. 2024-01-01T08:00:00Z",
    )

    # Aggregated metrics
    vehicle_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Total vehicles detected in this hour"
    )
    avg_speed_kmh: Mapped[float | None] = mapped_column(nullable=True, comment="Mean speed km/h")
    peak_density: Mapped[float | None] = mapped_column(nullable=True, comment="Maximum density score 0-1")
    avg_density: Mapped[float | None] = mapped_column(nullable=True, comment="Mean density score 0-1")

    # Breakdown by vehicle type (JSON-compatible approach)
    car_count: Mapped[int] = mapped_column(Integer, default=0)
    truck_count: Mapped[int] = mapped_column(Integer, default=0)
    motorcycle_count: Mapped[int] = mapped_column(Integer, default=0)
    bus_count: Mapped[int] = mapped_column(Integer, default=0)
    emergency_count: Mapped[int] = mapped_column(Integer, default=0)

    # Signal efficiency
    avg_green_duration_s: Mapped[float | None] = mapped_column(
        nullable=True, comment="Mean green phase duration for the hour"
    )
    signal_cycles: Mapped[int] = mapped_column(Integer, default=0, comment="Number of full signal cycles")

    # Metadata
    is_complete: Mapped[bool] = mapped_column(
        default=False,
        comment="True once the hour has fully elapsed and data is final",
    )

    # Relationship
    camera: Mapped["Camera"] = relationship("Camera", back_populates="analytics")

    def __repr__(self) -> str:
        return (
            f"<AnalyticsHourly camera={self.camera_id!r} "
            f"hour={self.hour_bucket!r} count={self.vehicle_count}>"
        )
