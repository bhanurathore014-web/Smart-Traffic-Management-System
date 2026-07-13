"""
database/base.py
================
Declarative base and shared column mixins.

All ORM models inherit from ``Base``.  The mixins are opt-in —
models import whichever combination they need.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn, mapped_column


# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base.

    All models must:
    * Subclass ``Base``.
    * Define ``__tablename__`` as a lowercase, plural snake_case string.
    """

    # Type annotation map used by Mapped[] columns
    type_annotation_map: dict[type, Any] = {
        str: String,
    }


# ---------------------------------------------------------------------------
# Shared Mixins
# ---------------------------------------------------------------------------

class UUIDPrimaryKeyMixin:
    """Adds a UUID v4 primary key column named ``id``."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        sort_order=-100,          # render first in DDL
        comment="UUID v4 primary key",
    )


class TimestampMixin:
    """Adds server-controlled ``created_at`` and ``updated_at`` columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        sort_order=98,
        comment="Row creation timestamp (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        sort_order=99,
        comment="Row last-update timestamp (UTC)",
    )


class SoftDeleteMixin:
    """Adds an optional ``deleted_at`` column for soft-delete patterns."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        sort_order=100,
        comment="Non-null when row is soft-deleted",
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
