"""
database/models/vehicle.py
==========================
Vehicle — deduplicated catalogue of observed vehicles.

A vehicle record represents a unique physical vehicle.
Multiple NumberPlate reads and TrafficRecords can reference one Vehicle.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.number_plate import NumberPlate
    from database.models.traffic_record import TrafficRecord
    from database.models.emergency_event import EmergencyEvent


class VehicleType(str, Enum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE = "police"
    BICYCLE = "bicycle"
    AUTO_RICKSHAW = "auto_rickshaw"
    UNKNOWN = "unknown"


class Vehicle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A unique observed vehicle entity."""

    __tablename__ = "vehicles"
    __table_args__ = (
        Index("ix_vehicles_type", "vehicle_type"),
        {"comment": "Deduplicated catalogue of observed vehicles"},
    )

    vehicle_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=VehicleType.UNKNOWN.value,
        comment="YOLO-classified vehicle type",
    )
    color: Mapped[str | None] = mapped_column(String(30), nullable=True, comment="Dominant body color")
    make: Mapped[str | None] = mapped_column(String(60), nullable=True, comment="Manufacturer brand")
    model_year: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Estimated model year")
    confidence: Mapped[float | None] = mapped_column(
        nullable=True, comment="Detection confidence score 0-1"
    )

    # Relationships
    number_plates: Mapped[list["NumberPlate"]] = relationship(
        "NumberPlate", back_populates="vehicle", lazy="selectin"
    )
    traffic_records: Mapped[list["TrafficRecord"]] = relationship(
        "TrafficRecord", back_populates="vehicle", lazy="selectin"
    )
    emergency_events: Mapped[list["EmergencyEvent"]] = relationship(
        "EmergencyEvent", back_populates="vehicle", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id!r} type={self.vehicle_type!r} color={self.color!r}>"
