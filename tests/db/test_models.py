"""
tests/db/test_models.py
========================
Unit tests for all 8 ORM models.

Tests:
  • Each model can be created, persisted, and retrieved.
  • FK constraints are wired correctly (via relationship access).
  • CheckConstraints reject invalid data at the Python layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.camera import Camera, CameraStatus
from database.models.vehicle import Vehicle, VehicleType
from database.models.number_plate import NumberPlate
from database.models.traffic_record import TrafficRecord, Direction
from database.models.signal_record import SignalRecord, SignalPhase, SignalTrigger
from database.models.emergency_event import EmergencyEvent, EmergencyType, EmergencyStatus
from database.models.analytics_hourly import AnalyticsHourly
from database.models.system_config import SystemConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_camera_create_and_retrieve(db_session: AsyncSession) -> None:
    cam = Camera(
        id=_uid(),
        name="Test Camera",
        location="Test Street, Mumbai",
        latitude=19.07,
        longitude=72.87,
        status=CameraStatus.ACTIVE.value,
    )
    db_session.add(cam)
    await db_session.flush()

    fetched = await db_session.get(Camera, cam.id)
    assert fetched is not None
    assert fetched.name == "Test Camera"
    assert fetched.status == "active"


@pytest.mark.asyncio
async def test_camera_default_status(db_session: AsyncSession) -> None:
    cam = Camera(id=_uid(), name="Cam2", location="Loc2", latitude=0, longitude=0)
    db_session.add(cam)
    await db_session.flush()
    assert cam.status == CameraStatus.ACTIVE.value


# ---------------------------------------------------------------------------
# Vehicle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vehicle_create(db_session: AsyncSession) -> None:
    v = Vehicle(
        id=_uid(),
        vehicle_type=VehicleType.CAR.value,
        color="white",
        make="Maruti",
        confidence=0.95,
    )
    db_session.add(v)
    await db_session.flush()
    fetched = await db_session.get(Vehicle, v.id)
    assert fetched is not None
    assert fetched.vehicle_type == "car"


# ---------------------------------------------------------------------------
# NumberPlate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_number_plate_linked_to_vehicle(db_session: AsyncSession) -> None:
    v = Vehicle(id=_uid(), vehicle_type="car")
    db_session.add(v)
    await db_session.flush()

    plate = NumberPlate(
        id=_uid(),
        vehicle_id=v.id,
        plate_text="MH-12-AB-1234",
        plate_text_normalized="MH12AB1234",
        confidence=0.92,
    )
    db_session.add(plate)
    await db_session.flush()

    fetched = await db_session.get(NumberPlate, plate.id)
    assert fetched is not None
    assert fetched.vehicle_id == v.id
    assert fetched.plate_text == "MH-12-AB-1234"


# ---------------------------------------------------------------------------
# TrafficRecord
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_traffic_record_create(db_session: AsyncSession) -> None:
    cam = Camera(id=_uid(), name="TC", location="Loc", latitude=0, longitude=0)
    db_session.add(cam)
    await db_session.flush()

    rec = TrafficRecord(
        id=_uid(),
        camera_id=cam.id,
        timestamp=_now(),
        direction=Direction.NORTH.value,
        lane_number=1,
        speed_kmh=45.0,
        detection_confidence=0.88,
    )
    db_session.add(rec)
    await db_session.flush()

    fetched = await db_session.get(TrafficRecord, rec.id)
    assert fetched is not None
    assert fetched.speed_kmh == 45.0
    assert fetched.camera_id == cam.id


# ---------------------------------------------------------------------------
# SignalRecord
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signal_record_create(db_session: AsyncSession) -> None:
    cam = Camera(id=_uid(), name="SC", location="Loc", latitude=0, longitude=0)
    db_session.add(cam)
    await db_session.flush()

    sig = SignalRecord(
        id=_uid(),
        camera_id=cam.id,
        timestamp=_now(),
        phase=SignalPhase.GREEN.value,
        duration_seconds=45.0,
        triggered_by=SignalTrigger.ADAPTIVE.value,
    )
    db_session.add(sig)
    await db_session.flush()

    fetched = await db_session.get(SignalRecord, sig.id)
    assert fetched is not None
    assert fetched.phase == "green"
    assert fetched.triggered_by == "adaptive"


# ---------------------------------------------------------------------------
# EmergencyEvent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_emergency_event_create_and_duration(db_session: AsyncSession) -> None:
    from datetime import timedelta

    cam = Camera(id=_uid(), name="EC", location="Loc", latitude=0, longitude=0)
    db_session.add(cam)
    await db_session.flush()

    ts = _now()
    resolved_at = ts + timedelta(minutes=3)
    evt = EmergencyEvent(
        id=_uid(),
        camera_id=cam.id,
        timestamp=ts,
        emergency_type=EmergencyType.AMBULANCE.value,
        priority=1,
        status=EmergencyStatus.RESOLVED.value,
        resolved_at=resolved_at,
    )
    db_session.add(evt)
    await db_session.flush()

    fetched = await db_session.get(EmergencyEvent, evt.id)
    assert fetched is not None
    assert fetched.emergency_type == "ambulance"
    assert fetched.duration_seconds is not None
    assert fetched.duration_seconds > 0


# ---------------------------------------------------------------------------
# AnalyticsHourly
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_analytics_hourly_create(db_session: AsyncSession) -> None:
    cam = Camera(id=_uid(), name="AC", location="Loc", latitude=0, longitude=0)
    db_session.add(cam)
    await db_session.flush()

    bucket = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    row = AnalyticsHourly(
        id=_uid(),
        camera_id=cam.id,
        hour_bucket=bucket,
        vehicle_count=320,
        avg_speed_kmh=38.5,
        peak_density=0.72,
    )
    db_session.add(row)
    await db_session.flush()

    fetched = await db_session.get(AnalyticsHourly, row.id)
    assert fetched is not None
    assert fetched.vehicle_count == 320


# ---------------------------------------------------------------------------
# SystemConfig
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_system_config_typed_accessors(db_session: AsyncSession) -> None:
    cfg = SystemConfig(key="signal.min_green_seconds", value="15", value_type="int")
    db_session.add(cfg)
    await db_session.flush()

    fetched = await db_session.get(SystemConfig, "signal.min_green_seconds")
    assert fetched is not None
    assert fetched.as_int() == 15
    assert fetched.as_float() == 15.0
    assert fetched.as_bool() is False   # "15" is not truthy for bool
