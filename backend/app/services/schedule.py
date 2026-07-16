from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.booking import Booking
from app.constants import BOOKING_STATUS_BOOKED


async def count_active_bookings(db: AsyncSession, schedule_id: int) -> int:
    count = func.count(Booking.id)
    statement = select(count).where(Booking.schedule_id == schedule_id, Booking.status == BOOKING_STATUS_BOOKED)
    result = await db.execute(statement)
    booked_count = result.scalar_one()
    return booked_count