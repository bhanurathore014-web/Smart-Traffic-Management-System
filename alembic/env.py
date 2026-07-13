"""
alembic/env.py
===============
Async-aware Alembic environment for the Smart Traffic Management System.

Supports both:
  • Offline mode  (generates SQL without a live DB connection)
  • Online mode   (applies migrations using AsyncEngine + run_sync)

Usage:
    alembic upgrade head
    alembic revision --autogenerate -m "add column"
    alembic downgrade -1
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Import Base + all models so Alembic can detect schema changes
# ---------------------------------------------------------------------------
from database.base import Base
import database.models  # noqa: F401 — side-effect: registers all models

# ---------------------------------------------------------------------------
# Alembic Config object (gives access to alembic.ini)
# ---------------------------------------------------------------------------
config = context.config

# Inject ALEMBIC_DATABASE_URL from environment (supports sync drivers)
alembic_db_url = os.getenv(
    "ALEMBIC_DATABASE_URL",
    "sqlite:///./database/smart_traffic_dev.db",
)
config.set_main_option("sqlalchemy.url", alembic_db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This generates SQL scripts without connecting to the database.
    Useful for generating SQL to review or run manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (async)
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        # Render as batch for SQLite ALTER TABLE support
        render_as_batch=alembic_db_url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations via run_sync."""
    # Build async URL from the sync ALEMBIC_DATABASE_URL
    async_url = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./database/smart_traffic_dev.db",
    )

    # Override the config URL with the async variant for the engine
    connectable = async_engine_from_config(
        {"sqlalchemy.url": async_url, "sqlalchemy.poolclass": pool.NullPool},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncio."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
