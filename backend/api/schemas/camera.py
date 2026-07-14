from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel
from database.models.camera import CameraStatus

class CameraBase(BaseModel):
    name: str = Field(..., max_length=120)
    location: str = Field(..., max_length=255)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    stream_url: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=45)
    status: CameraStatus = Field(default=CameraStatus.ACTIVE)
    num_lanes: int = Field(default=4, ge=1)
    description: str | None = Field(default=None, max_length=500)

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    stream_url: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=45)
    status: CameraStatus | None = None
    num_lanes: int | None = Field(default=None, ge=1)
    description: str | None = Field(default=None, max_length=500)

class CameraResponse(CameraBase, ORMBaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
