"""
tests/db/conftest.py
=====================
Shared pytest fixtures for database tests.

Uses an in-memory SQLite database (aiosqlite) so tests are:
  • Fast      — no disk I/O
  • Isolated  — each test session gets a fresh schema
  • Zero-setup — no external DB required
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.base import Base
# Import all models so metadata is populated
import database.models  # noqa: F401


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def async_engine_fixture() -> AsyncEngine:  # type: ignore[misc]
    """Session-scoped async engine against an in-memory SQLite DB."""
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture()
async def db_session(async_engine_fixture: AsyncEngine) -> AsyncSession:  # type: ignore[misc]
    """Function-scoped session that rolls back after each test."""
    factory = async_sessionmaker(
        bind=async_engine_fixture,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session
        await session.rollback()
