"""
tests/db/test_repositories.py
================================
Unit tests for all 6 domain repositories + BaseRepository.

Uses the shared in-memory SQLite fixture from conftest.py.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.camera import Camera, CameraStatus
from database.models.vehicle import Vehicle
from database.models.number_plate import NumberPlate
from database.models.traffic_record import TrafficRecord
from database.models.signal_record import SignalRecord, SignalPhase, SignalTrigger
from database.models.emergency_event import EmergencyEvent, EmergencyStatus, EmergencyType
from database.models.analytics_hourly import AnalyticsHourly
from database.repositories import (
    CameraRepository,
    TrafficRecordRepository,
    NumberPlateRepository,
    AnalyticsRepository,
    EmergencyEventRepository,
    SignalRepository,
)


def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _make_camera(session: AsyncSession, **kwargs) -> Camera:
    defaults = dict(
        id=_uid(), name="Cam", location="Loc", latitude=19.0, longitude=72.8, status="active"
    )
    defaults.update(kwargs)
    cam = Camera(**defaults)
    session.add(cam)
    await session.flush()
    return cam


async def _make_vehicle(session: AsyncSession) -> Vehicle:
    v = Vehicle(id=_uid(), vehicle_type="car", confidence=0.9)
    session.add(v)
    await session.flush()
    return v


# ---------------------------------------------------------------------------
# BaseRepository / CameraRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_camera_repo_create_and_get(db_session: AsyncSession) -> None:
    repo = CameraRepository(db_session)
    cam = await repo.create({
        "id": _uid(),
        "name": "Test Cam",
        "location": "Andheri",
        "latitude": 19.11,
        "longitude": 72.87,
        "status": "active",
    })
    fetched = await repo.get(cam.id)
    assert fetched is not None
    assert fetched.name == "Test Cam"


@pytest.mark.asyncio
async def test_camera_repo_list_and_count(db_session: AsyncSession) -> None:
    repo = CameraRepository(db_session)
    for i in range(3):
        await repo.create({
            "id": _uid(),
            "name": f"Cam {i}",
            "location": f"Loc {i}",
            "latitude": 19.0 + i,
            "longitude": 72.0,
            "status": "active" if i < 2 else "inactive",
        })
    active = await repo.get_active_cameras()
    assert len(active) >= 2


@pytest.mark.asyncio
async def test_camera_repo_update(db_session: AsyncSession) -> None:
    repo = CameraRepository(db_session)
    cam = await repo.create({
        "id": _uid(), "name": "Old", "location": "L", "latitude": 0, "longitude": 0
    })
    updated = await repo.update(cam.id, {"name": "New Name"})
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_camera_repo_delete(db_session: AsyncSession) -> None:
    repo = CameraRepository(db_session)
    cam = await repo.create({
        "id": _uid(), "name": "Del", "location": "L", "latitude": 0, "longitude": 0
    })
    deleted = await repo.delete(cam.id)
    assert deleted is True
    assert await repo.get(cam.id) is None


# ---------------------------------------------------------------------------
# TrafficRecordRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_traffic_bulk_insert(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = TrafficRecordRepository(db_session)
    now = _now()
    rows = [
        {
            "id": _uid(),
            "camera_id": cam.id,
            "timestamp": now - timedelta(minutes=i),
            "direction": "north",
            "lane_number": 1,
            "speed_kmh": 30.0 + i,
        }
        for i in range(100)
    ]
    inserted = await repo.bulk_create(rows)
    assert inserted == 100


@pytest.mark.asyncio
async def test_traffic_density_window(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = TrafficRecordRepository(db_session)
    now = _now()
    rows = [
        {
            "id": _uid(),
            "camera_id": cam.id,
            "timestamp": now - timedelta(minutes=i),
            "direction": "north",
            "lane_number": 1,
            "speed_kmh": 40.0,
        }
        for i in range(10)
    ]
    await repo.bulk_create(rows)
    density = await repo.get_density_by_window(
        cam.id, now - timedelta(hours=1), now + timedelta(minutes=1)
    )
    assert density["count"] == 10
    assert density["avg_speed"] == 40.0


# ---------------------------------------------------------------------------
# NumberPlateRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_plate_find_by_text(db_session: AsyncSession) -> None:
    v = await _make_vehicle(db_session)
    plate = NumberPlate(
        id=_uid(),
        vehicle_id=v.id,
        plate_text="MH-12-AB-5678",
        plate_text_normalized="MH12AB5678",
        confidence=0.95,
    )
    db_session.add(plate)
    await db_session.flush()

    repo = NumberPlateRepository(db_session)
    results = await repo.find_by_plate_text("MH-12-AB-5678")
    assert len(results) >= 1
    assert results[0].plate_text == "MH-12-AB-5678"


# ---------------------------------------------------------------------------
# AnalyticsRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analytics_upsert_is_idempotent(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = AnalyticsRepository(db_session)
    bucket = datetime(2024, 3, 15, 10, 0, 0, tzinfo=timezone.utc)

    first = await repo.upsert_hourly_bucket(cam.id, bucket, {"vehicle_count": 100})
    second = await repo.upsert_hourly_bucket(cam.id, bucket, {"vehicle_count": 150})

    assert first.camera_id == cam.id
    assert second.vehicle_count == 150   # Updated, not duplicated


@pytest.mark.asyncio
async def test_analytics_get_trend(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = AnalyticsRepository(db_session)
    now = _now().replace(minute=0, second=0, microsecond=0)

    for h in range(5):
        bucket = now - timedelta(hours=h)
        await repo.upsert_hourly_bucket(cam.id, bucket, {"vehicle_count": 50 + h})

    trend = await repo.get_trend(cam.id, hours=6)
    assert len(trend) >= 5


# ---------------------------------------------------------------------------
# EmergencyEventRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_emergency_get_active_and_resolve(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = EmergencyEventRepository(db_session)

    evt = EmergencyEvent(
        id=_uid(),
        camera_id=cam.id,
        timestamp=_now(),
        emergency_type=EmergencyType.AMBULANCE.value,
        priority=1,
        status=EmergencyStatus.ACTIVE.value,
    )
    db_session.add(evt)
    await db_session.flush()

    active = await repo.get_active_emergencies()
    assert any(e.id == evt.id for e in active)

    resolved = await repo.resolve_event(evt.id)
    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None


# ---------------------------------------------------------------------------
# SignalRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_get_last_phase(db_session: AsyncSession) -> None:
    cam = await _make_camera(db_session)
    repo = SignalRepository(db_session)
    now = _now()

    for i, phase in enumerate(["red", "green", "yellow"]):
        sig = SignalRecord(
            id=_uid(),
            camera_id=cam.id,
            timestamp=now + timedelta(seconds=i * 30),
            phase=phase,
            duration_seconds=30.0,
            triggered_by=SignalTrigger.FIXED.value,
        )
        db_session.add(sig)
    await db_session.flush()

    last = await repo.get_last_phase(cam.id)
    assert last is not None
    assert last.phase == "yellow"
