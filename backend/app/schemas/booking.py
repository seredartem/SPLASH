from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime, date as DateType, time as TimeType

class BookingCreate(BaseModel):
    schedule_id: int

class BookingResponse(BookingCreate):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    id: int
    status: str
    created_at: datetime

class BookingDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    schedule_id: int
    status: str

    class_id: int
    class_title: str

    trainer_id: int
    trainer_name: str

    date: DateType
    start_time: TimeType
    end_time: TimeType

    created_at: datetime

class AdminBookingDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    user_name: str
    user_email: EmailStr

    schedule_id: int
    status: str

    class_id: int
    class_title: str

    trainer_id: int
    trainer_name: str

    date: DateType
    start_time: TimeType
    end_time: TimeType

    created_at: datetime