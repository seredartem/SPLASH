from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.dependencies.auth import get_current_admin, get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingResponse)
async def create_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Schedule).where(Schedule.id == booking_data.schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()
    existing_booking = await db.execute(select(Booking).where(Booking.user_id == current_user.id, Booking.schedule_id == booking_data.schedule_id, Booking.status == "booked"))

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule.is_active == False:
        raise HTTPException(status_code=400, detail="Cannot book an inactive schedule")

    if existing_booking.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already booked this schedule")
    
    statement = select(func.count(Booking.id)).where(Booking.schedule_id == booking_data.schedule_id, Booking.status == "booked")
    result = await db.execute(statement)
    booked_count = result.scalar()
    if booked_count >= schedule.max_places:
        raise HTTPException(status_code=400, detail="This schedule is fully booked")    

    new_booking = Booking(
        user_id=current_user.id,
        schedule_id=booking_data.schedule_id,
        status="booked"
    )

    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=list[BookingResponse])
async def get_user_bookings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Booking).where(Booking.user_id == current_user.id)
    result = await db.execute(statement)
    bookings = result.scalars().all()
    return bookings

@router.get("/admin/all", response_model=list[BookingResponse])
async def get_all_bookings(db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Booking).order_by(Booking.created_at)
    result = await db.execute(statement)
    bookings = result.scalars().all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id)
    result = await db.execute(statement)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id)
    result = await db.execute(statement)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)
    return booking
