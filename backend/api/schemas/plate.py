from datetime import datetime
from pydantic import BaseModel, Field

from backend.api.schemas.base import ORMBaseModel

class NumberPlateBase(BaseModel):
    plate_text: str = Field(..., max_length=20)
    plate_text_normalized: str | None = Field(default=None, max_length=20)
    region: str | None = Field(default=None, max_length=60)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    ocr_engine: str | None = Field(default=None, max_length=20)
    crop_image_path: str | None = Field(default=None, max_length=512)

class NumberPlateCreate(NumberPlateBase):
    vehicle_id: str | None = None

class NumberPlateResponse(NumberPlateBase, ORMBaseModel):
    id: str
    vehicle_id: str | None
    created_at: datetime
    updated_at: datetime
