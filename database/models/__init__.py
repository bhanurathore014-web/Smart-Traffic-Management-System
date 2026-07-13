"""database/models/__init__.py — re-export all ORM models."""

from database.models.camera import Camera
from database.models.vehicle import Vehicle
from database.models.number_plate import NumberPlate
from database.models.traffic_record import TrafficRecord
from database.models.signal_record import SignalRecord
from database.models.emergency_event import EmergencyEvent
from database.models.analytics_hourly import AnalyticsHourly
from database.models.system_config import SystemConfig

__all__ = [
    "Camera",
    "Vehicle",
    "NumberPlate",
    "TrafficRecord",
    "SignalRecord",
    "EmergencyEvent",
    "AnalyticsHourly",
    "SystemConfig",
]
