"""
database/ — async database layer for Smart Traffic Management System.

Public surface:
    Base            — SQLAlchemy declarative base
    async_engine    — configured AsyncEngine instance
    AsyncSessionLocal — session factory
    get_db          — FastAPI dependency (AsyncSession)
    All ORM models  — imported so Alembic can auto-detect them
"""

from database.base import Base
from database.session import AsyncSessionLocal, async_engine
from database.deps import get_db

# Re-export all models so alembic env.py only needs to import this package
from database.models import (  # noqa: F401
    Camera,
    Vehicle,
    NumberPlate,
    TrafficRecord,
    SignalRecord,
    EmergencyEvent,
    AnalyticsHourly,
    SystemConfig,
)

__all__ = [
    "Base",
    "async_engine",
    "AsyncSessionLocal",
    "get_db",
    # models
    "Camera",
    "Vehicle",
    "NumberPlate",
    "TrafficRecord",
    "SignalRecord",
    "EmergencyEvent",
    "AnalyticsHourly",
    "SystemConfig",
]
