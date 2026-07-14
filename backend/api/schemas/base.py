from pydantic import BaseModel, ConfigDict

class ORMBaseModel(BaseModel):
    """Base Pydantic model with ORM mapping enabled."""
    model_config = ConfigDict(from_attributes=True)
