from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BookingCreate(BaseModel):
    schedule_id: int

class BookingResponse(BookingCreate):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    id: int
    status: str
    created_at: datetime
