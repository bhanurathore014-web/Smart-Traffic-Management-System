"""
database/repositories/base.py
==============================
Generic async repository providing standard CRUD operations.

All domain repositories subclass ``BaseRepository[ModelT]`` and
inherit these methods, overriding or extending where needed.
"""

from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Thread-safe async CRUD repository for a single SQLAlchemy model."""

    model: type[ModelT]  # subclasses must set this

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get(self, record_id: str) -> ModelT | None:
        """Fetch a single row by primary key."""
        result = await self.session.get(self.model, record_id)
        return result

    async def get_or_raise(self, record_id: str) -> ModelT:
        """Fetch by primary key or raise ``ValueError``."""
        obj = await self.get(record_id)
        if obj is None:
            raise ValueError(f"{self.model.__name__} with id={record_id!r} not found")
        return obj

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None,
        **filters: Any,
    ) -> Sequence[ModelT]:
        """Return a paginated, optionally filtered list of rows."""
        stmt = select(self.model)

        # Apply equality filters
        for attr, value in filters.items():
            col = getattr(self.model, attr, None)
            if col is not None and value is not None:
                stmt = stmt.where(col == value)

        if order_by is not None:
            stmt = stmt.order_by(order_by)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        """Return total row count matching filters."""
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        for attr, value in filters.items():
            col = getattr(self.model, attr, None)
            if col is not None and value is not None:
                stmt = stmt.where(col == value)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, data: dict[str, Any]) -> ModelT:
        """Insert a single row from a dict of field values."""
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.flush()          # get DB-generated defaults
        await self.session.refresh(obj)
        return obj

    async def bulk_create(self, rows: list[dict[str, Any]]) -> int:
        """High-throughput bulk insert via Core INSERT.

        Returns the number of rows inserted.
        Avoids ORM overhead; no ``refresh`` is performed.
        """
        if not rows:
            return 0
        await self.session.execute(self.model.__table__.insert(), rows)
        return len(rows)

    async def update(self, record_id: str, data: dict[str, Any]) -> ModelT:
        """Partial update — only columns present in *data* are changed."""
        obj = await self.get_or_raise(record_id)
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update_where(self, filters: dict[str, Any], data: dict[str, Any]) -> int:
        """Bulk update rows matching *filters*.  Returns rows affected."""
        stmt = update(self.model)
        for attr, value in filters.items():
            col = getattr(self.model, attr, None)
            if col is not None:
                stmt = stmt.where(col == value)
        stmt = stmt.values(**data)
        result = await self.session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]

    async def delete(self, record_id: str) -> bool:
        """Hard-delete a row. Returns True if deleted, False if not found."""
        obj = await self.get(record_id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def delete_where(self, **filters: Any) -> int:
        """Bulk hard-delete. Returns number of rows deleted."""
        stmt = delete(self.model)
        for attr, value in filters.items():
            col = getattr(self.model, attr, None)
            if col is not None:
                stmt = stmt.where(col == value)
        result = await self.session.execute(stmt)
        return result.rowcount  # type: ignore[return-value]
