from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.booking import Booking
from app.constants import BOOKING_STATUS_BOOKED
from app.models.class_model import ClassModel


async def count_active_bookings(db: AsyncSession, schedule_id: int) -> int:
    count = func.count(Booking.id)
    statement = select(count).where(Booking.schedule_id == schedule_id, Booking.status == BOOKING_STATUS_BOOKED)
    result = await db.execute(statement)
    booked_count = result.scalar_one()
    return booked_count

async def get_active_class(db: AsyncSession, class_id: int) -> ClassModel:
    statement = select(ClassModel).where(ClassModel.id == class_id)
    result = await db.execute(statement)
    active_class = result.scalar_one_or_none()

    if active_class is None:
        raise HTTPException(status_code=404, detail=("Class not found"))
    
    if not active_class.is_active:
        raise HTTPException(status_code=400, detail="Cannot schedule an inactive class")
    
    return active_class