from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel
from database.models.traffic_record import Direction

class TrafficRecordBase(BaseModel):
    camera_id: str
    direction: Direction = Field(default=Direction.UNKNOWN)
    lane_number: int = Field(default=1, ge=1)
    speed_kmh: float | None = Field(default=None, ge=0)
    detection_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    bbox_x1: int | None = None
    bbox_y1: int | None = None
    bbox_x2: int | None = None
    bbox_y2: int | None = None
    tracker_id: int | None = None

class TrafficRecordCreate(TrafficRecordBase):
    timestamp: datetime | None = None
    vehicle_id: str | None = None
    number_plate_id: str | None = None

class TrafficRecordResponse(TrafficRecordBase, ORMBaseModel):
    id: str
    timestamp: datetime
    vehicle_id: str | None
    number_plate_id: str | None
    created_at: datetime
    updated_at: datetime

class DensityResponse(BaseModel):
    count: int
    avg_speed: float
