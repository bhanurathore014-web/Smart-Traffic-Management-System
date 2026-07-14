from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel

class AnalyticsHourlyResponse(ORMBaseModel):
    id: str
    camera_id: str
    hour_bucket: datetime
    vehicle_count: int
    avg_speed_kmh: float | None
    peak_density: float | None
    avg_density: float | None
    car_count: int
    truck_count: int
    motorcycle_count: int
    bus_count: int
    emergency_count: int
    avg_green_duration_s: float | None
    signal_cycles: int
    is_complete: bool
    created_at: datetime
    updated_at: datetime
