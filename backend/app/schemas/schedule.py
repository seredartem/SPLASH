from pydantic import BaseModel, ConfigDict
from datetime import date as DateType, time as TimeType, datetime

class ScheduleBase(BaseModel):
    start_time: TimeType
    end_time: TimeType
    class_id: int
    trainer_id: int
    date: DateType
    max_places: int
    is_active: bool = True

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    class_id: int | None = None
    trainer_id: int | None = None
    date: DateType | None = None
    start_time: TimeType | None = None
    end_time: TimeType | None = None
    max_places: int | None = None
    is_active: bool | None = None

class ScheduleResponse(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

