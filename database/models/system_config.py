"""
database/models/system_config.py
==================================
SystemConfig — runtime-tunable key/value store.

Used to change operational thresholds (density limits, green-time bounds,
YOLO confidence) without a code deploy.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class SystemConfig(Base):
    """Runtime key-value configuration table.

    Primary key is the config ``key`` string — no UUID needed here since
    rows are directly accessed by well-known key names.
    """

    __tablename__ = "system_config"
    __table_args__ = {"comment": "Runtime-tunable operational configuration"}

    key: Mapped[str] = mapped_column(
        String(120),
        primary_key=True,
        comment="Unique configuration key e.g. 'signal.min_green_seconds'",
    )
    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="String-serialised value (JSON allowed for complex types)",
    )
    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="string",
        comment="Type hint: string | int | float | bool | json",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Human-readable description of this config key"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp (UTC)",
    )
    updated_by: Mapped[str | None] = mapped_column(
        String(80), nullable=True, comment="Operator / system that last changed this value"
    )

    def as_int(self) -> int:
        return int(self.value)

    def as_float(self) -> float:
        return float(self.value)

    def as_bool(self) -> bool:
        return self.value.lower() in {"true", "1", "yes"}

    def __repr__(self) -> str:
        return f"<SystemConfig key={self.key!r} value={self.value!r}>"
