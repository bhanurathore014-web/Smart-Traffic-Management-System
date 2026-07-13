"""database/repositories/__init__.py — re-export all repositories."""

from database.repositories.base import BaseRepository
from database.repositories.camera import CameraRepository
from database.repositories.traffic_record import TrafficRecordRepository
from database.repositories.number_plate import NumberPlateRepository
from database.repositories.analytics import AnalyticsRepository
from database.repositories.emergency_event import EmergencyEventRepository
from database.repositories.signal_record import SignalRepository

__all__ = [
    "BaseRepository",
    "CameraRepository",
    "TrafficRecordRepository",
    "NumberPlateRepository",
    "AnalyticsRepository",
    "EmergencyEventRepository",
    "SignalRepository",
]
