from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TrainerBase(BaseModel):
    name: str
    bio: str | None = None
    specialization: str | None = None
    photo_url: str | None = None
    is_active: bool = True

class TrainerCreate(TrainerBase):
    pass

class TrainerUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    specialization: str | None = None
    photo_url: str | None = None
    is_active: bool | None = None

class TrainerResponse(TrainerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime