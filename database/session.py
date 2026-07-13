"""
database/session.py
====================
Async SQLAlchemy engine and session factory.

Environment variables (read via pydantic-settings):
    DATABASE_URL        — async driver URL (aiosqlite | asyncpg)
    DB_POOL_SIZE        — connection pool size (default 10)
    DB_MAX_OVERFLOW     — pool overflow (default 20)
    DB_POOL_TIMEOUT     — seconds to wait for a connection (default 30)
    DB_ECHO             — log all SQL when DEBUG=true
"""

from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# Read settings — use os.getenv as a zero-dep fallback so this module
# can be imported before pydantic-settings is fully initialised.
# ---------------------------------------------------------------------------

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./database/smart_traffic_dev.db",
)
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_ECHO: bool = os.getenv("DEBUG", "false").lower() == "true"

# ---------------------------------------------------------------------------
# SQLite-specific: connect_args to enable WAL mode and foreign keys.
# asyncpg does not need connect_args.
# ---------------------------------------------------------------------------

_is_sqlite = DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {
    "echo": DB_ECHO,
    "future": True,
}

if _is_sqlite:
    # SQLite doesn't support pool_size / max_overflow
    _engine_kwargs["connect_args"] = {
        "check_same_thread": False,
        "timeout": 20,
    }
else:
    _engine_kwargs["pool_size"] = DB_POOL_SIZE
    _engine_kwargs["max_overflow"] = DB_MAX_OVERFLOW
    _engine_kwargs["pool_timeout"] = DB_POOL_TIMEOUT
    _engine_kwargs["pool_pre_ping"] = True   # detect stale connections

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

async_engine: AsyncEngine = create_async_engine(DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,   # keep objects usable after commit
    autoflush=False,
    autocommit=False,
)


async def dispose_engine() -> None:
    """Cleanly dispose the connection pool.

    Call this from the FastAPI ``lifespan`` shutdown handler.
    """
    await async_engine.dispose()
