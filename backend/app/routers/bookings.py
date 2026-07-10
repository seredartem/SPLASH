from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse, BookingDetailResponse, AdminBookingDetailResponse, BookingStatusUpdate
from app.dependencies.auth import get_current_admin, get_current_user
from app.models.user import User
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.models.trainers import Trainer
from app.models.class_model import ClassModel
from datetime import datetime
from app.constants import ALLOWED_BOOKING_STATUSES, BOOKING_STATUS_BOOKED, BOOKING_STATUS_CANCELLED

router = APIRouter(prefix="/bookings", tags=["bookings"])

def booking_details_base_query():
    return select(
        Booking.id,
        Booking.schedule_id,
        Booking.status,
        Booking.created_at,
        Schedule.class_id,
        ClassModel.title.label("class_title"),
        Schedule.trainer_id,
        Trainer.name.label("trainer_name"),
        Schedule.date,
        Schedule.start_time,
        Schedule.end_time
    ).join(Schedule, Schedule.id == Booking.schedule_id
    ).join(ClassModel, ClassModel.id == Schedule.class_id
    ).join(Trainer, Trainer.id == Schedule.trainer_id)

@router.post("/", response_model=BookingResponse)
async def create_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Schedule).where(Schedule.id == booking_data.schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()
    existing_booking = await db.execute(select(Booking).where(Booking.user_id == current_user.id, Booking.schedule_id == booking_data.schedule_id, Booking.status == BOOKING_STATUS_BOOKED))

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule_start = datetime.combine(schedule.date, schedule.start_time)

    if schedule_start <= datetime.now():
        raise HTTPException(status_code=400, detail="Cannot book a past schedule")
    
    if schedule.is_active == False:
        raise HTTPException(status_code=400, detail="Cannot book an inactive schedule")

    if existing_booking.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already booked this schedule")
    
    statement = select(func.count(Booking.id)).where(Booking.schedule_id == booking_data.schedule_id, Booking.status == BOOKING_STATUS_BOOKED)
    result = await db.execute(statement)
    booked_count = result.scalar()
    if booked_count >= schedule.max_places:
        raise HTTPException(status_code=400, detail="This schedule is fully booked")    

    new_booking = Booking(
        user_id=current_user.id,
        schedule_id=booking_data.schedule_id,
        status=BOOKING_STATUS_BOOKED
    )

    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

# пагинация (limit, page) + фильтрация (active / not active) 

@router.get("/", response_model=list[BookingResponse])
async def get_user_bookings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = select(Booking).where(Booking.user_id == current_user.id)
    result = await db.execute(statement)
    bookings = result.scalars().all()
    return bookings

# параметры лимит и пейдж
@router.get("/admin/all", response_model=list[BookingResponse])
async def get_all_bookings(db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Booking).order_by(Booking.created_at)
    result = await db.execute(statement)
    bookings = result.scalars().all()
    return bookings

@router.get("/admin/details", response_model=list[AdminBookingDetailResponse])
async def get_admin_booking_details(db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(
        Booking.id,
        Booking.user_id,
        User.name.label("user_name"),
        User.email.label("user_email"),
        Booking.schedule_id,
        Booking.status,
        Booking.created_at,
        Schedule.class_id,
        ClassModel.title.label("class_title"),
        Schedule.trainer_id,
        Trainer.name.label("trainer_name"),
        Schedule.date,
        Schedule.start_time,
        Schedule.end_time
    ).join(User, User.id == Booking.user_id
    ).join(Schedule, Schedule.id == Booking.schedule_id
    ).join(ClassModel, ClassModel.id == Schedule.class_id
    ).join(Trainer, Trainer.id == Schedule.trainer_id
    ).order_by(Schedule.date, Schedule.start_time, Booking.created_at)

    result = await db.execute(statement)
    booking_details = result.mappings().all()
    return booking_details

@router.patch("/admin/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(booking_data: BookingStatusUpdate, booking_id: int,db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Booking).where(Booking.id==booking_id)
    result = await db.execute(statement)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Not found")
    
    if booking_data.status not in ALLOWED_BOOKING_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid booking status")
    
    booking.status = booking_data.status
    await db.commit()
    await db.refresh(booking)
    return booking

@router.get("/details", response_model=list[BookingDetailResponse])
async def get_booking_details(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = booking_details_base_query().where(Booking.user_id == current_user.id).order_by(Schedule.date, Schedule.start_time)

    result = await db.execute(statement)
    booking_details = result.mappings().all()
    return booking_details

@router.get("/active", response_model=list[BookingDetailResponse])
async def get_active_bookings(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    statement = booking_details_base_query().where(Booking.user_id == current_user.id, Booking.status == BOOKING_STATUS_BOOKED).order_by(Schedule.date, Schedule.start_time)

    result = await db.execute(statement)
    booking_details = result.mappings().all()
    return booking_details

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

    if booking.status == BOOKING_STATUS_CANCELLED:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    statement = select(Schedule).where(Schedule.id == booking.schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule_start = datetime.combine(schedule.date, schedule.start_time)

    if schedule_start <= datetime.now():
        raise HTTPException(status_code=400, detail="Cannot cancel a booking after schedule has started")

    booking.status = BOOKING_STATUS_CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking