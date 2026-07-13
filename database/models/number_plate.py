"""
database/models/number_plate.py
================================
NumberPlate — OCR read of a vehicle's registration plate.

One vehicle may produce many plate reads across cameras / time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from database.models.vehicle import Vehicle
    from database.models.traffic_record import TrafficRecord


class NumberPlate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An individual OCR number-plate detection result."""

    __tablename__ = "number_plates"
    __table_args__ = (
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="ck_plate_confidence"),
        Index("ix_number_plates_plate_text", "plate_text"),         # hot: lookup by plate
        Index("ix_number_plates_vehicle_id", "vehicle_id"),
        {"comment": "OCR-extracted number plate reads"},
    )

    # FK
    vehicle_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        comment="Parent vehicle (null if unresolved)",
    )

    # Plate data
    plate_text: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=False,              # covered by ix_number_plates_plate_text
        comment="Raw OCR plate string e.g. MH-12-AB-1234",
    )
    plate_text_normalized: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Uppercase, spaces/hyphens stripped for matching",
    )
    region: Mapped[str | None] = mapped_column(String(60), nullable=True, comment="State / RTO region code")
    confidence: Mapped[float] = mapped_column(nullable=False, default=0.0, comment="OCR confidence 0-1")
    ocr_engine: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="easyocr | paddleocr"
    )

    # Image storage
    crop_image_path: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="Path to saved plate crop image"
    )

    # Relationships
    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle", back_populates="number_plates")
    traffic_records: Mapped[list["TrafficRecord"]] = relationship(
        "TrafficRecord", back_populates="number_plate", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<NumberPlate id={self.id!r} plate={self.plate_text!r} conf={self.confidence:.2f}>"
