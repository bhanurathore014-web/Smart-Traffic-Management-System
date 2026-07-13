"""
database/deps.py
=================
FastAPI dependency that yields an AsyncSession per request.

Usage in a router:
    from database.deps import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/cameras")
    async def list_cameras(db: AsyncSession = Depends(get_db)):
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and ensure it is closed after the request.

    Rolls back on exception; commits are the caller's responsibility.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
