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


class ClassUpdate(ClassBase):
    pass

class ClassResponse(ClassBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
