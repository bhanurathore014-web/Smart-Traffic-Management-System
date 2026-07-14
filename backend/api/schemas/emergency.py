from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel
from database.models.emergency_event import EmergencyType, EmergencyStatus

class EmergencyEventBase(BaseModel):
    camera_id: str
    emergency_type: EmergencyType = Field(default=EmergencyType.UNKNOWN)
    priority: int = Field(default=1, ge=1, le=5)
    detection_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: str | None = Field(default=None, max_length=500)

class EmergencyEventCreate(EmergencyEventBase):
    timestamp: datetime | None = None
    vehicle_id: str | None = None

class EmergencyEventUpdate(BaseModel):
    status: EmergencyStatus | None = None
    resolved_at: datetime | None = None
    green_corridor_activated: bool | None = None
    notes: str | None = Field(default=None, max_length=500)

class EmergencyEventResponse(EmergencyEventBase, ORMBaseModel):
    id: str
    timestamp: datetime
    status: EmergencyStatus
    vehicle_id: str | None
    resolved_at: datetime | None
    green_corridor_activated: bool
    created_at: datetime
    updated_at: datetime
