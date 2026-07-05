from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ClassBase(BaseModel):
    title: str
    description: str | None = None
    level: str
    duration_minutes: int
    is_active: bool = True

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    level: str | None = None
    duration_minutes: int | None = None
    is_active: bool | None = None

class ClassResponse(ClassBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
