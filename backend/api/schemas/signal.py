from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel
from database.models.signal_record import SignalPhase, SignalTrigger

class SignalRecordBase(BaseModel):
    camera_id: str
    phase: SignalPhase
    duration_seconds: float = Field(default=0.0, ge=0.0)
    triggered_by: SignalTrigger = Field(default=SignalTrigger.FIXED)
    lane_id: int | None = None
    vehicle_count_at_trigger: int | None = None

class SignalRecordCreate(SignalRecordBase):
    timestamp: datetime | None = None

class SignalRecordResponse(SignalRecordBase, ORMBaseModel):
    id: str
    timestamp: datetime
    actual_duration_seconds: float | None
    created_at: datetime
    updated_at: datetime
