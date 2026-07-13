"""
database/models/traffic_record.py
==================================
TrafficRecord — core detection event table.

Every time a vehicle is confirmed crossing a camera's counting line,
one TrafficRecord is written.  This is the highest-volume table.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.camera import Camera
    from database.models.vehicle import Vehicle
    from database.models.number_plate import NumberPlate


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UNKNOWN = "unknown"


class TrafficRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single vehicle-detection crossing event."""

    __tablename__ = "traffic_records"
    __table_args__ = (
        CheckConstraint("speed_kmh >= 0", name="ck_traffic_speed_positive"),
        CheckConstraint("lane_number >= 1", name="ck_traffic_lane_min"),
        CheckConstraint("detection_confidence >= 0.0 AND detection_confidence <= 1.0", name="ck_traffic_conf"),
        # Hot query paths
        Index("ix_traffic_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_traffic_timestamp", "timestamp"),
        Index("ix_traffic_vehicle_id", "vehicle_id"),
        {"comment": "Vehicle detection crossing events — high-volume append-mostly table"},
    )

    # Foreign keys
    camera_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        comment="Camera that recorded this event",
    )
    vehicle_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        comment="Detected vehicle (null if unclassified)",
    )
    number_plate_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("number_plates.id", ondelete="SET NULL"),
        nullable=True,
        comment="Associated plate read (null if not captured)",
    )

    # Event data
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Event time (UTC)",
    )
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=Direction.UNKNOWN.value,
        comment="Travel direction enum",
    )
    lane_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="Lane index 1-N")
    speed_kmh: Mapped[float | None] = mapped_column(nullable=True, comment="Estimated speed km/h")
    detection_confidence: Mapped[float | None] = mapped_column(nullable=True, comment="YOLO confidence 0-1")

    # Bounding box (stored for debugging / analytics)
    bbox_x1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_y1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_x2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_y2: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Tracker state
    tracker_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="ByteTrack track ID")

    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="traffic_records")
    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle", back_populates="traffic_records")
    number_plate: Mapped["NumberPlate | None"] = relationship(
        "NumberPlate", back_populates="traffic_records"
    )

    def __repr__(self) -> str:
        return (
            f"<TrafficRecord id={self.id!r} camera={self.camera_id!r} "
            f"ts={self.timestamp!r} dir={self.direction!r}>"
        )
