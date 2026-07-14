from pydantic import BaseModel, ConfigDict, Field
from datetime import date as DateType, time as TimeType, datetime

class ScheduleBase(BaseModel):
    start_time: TimeType
    end_time: TimeType
    class_id: int
    trainer_id: int
    date: DateType
    max_places: int = Field(gt=0)
    is_active: bool = True

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    class_id: int | None = None
    trainer_id: int | None = None
    date: DateType | None = None
    start_time: TimeType | None = None
    end_time: TimeType | None = None
    max_places: int | None = Field(default=None, gt=0)
    is_active: bool | None = None

class ScheduleResponse(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# наследовать от шедулбейз
class ScheduleDetailResponse(ScheduleResponse):
    class_title: str
    trainer_name: str
    booked_places: int
    available_places: int