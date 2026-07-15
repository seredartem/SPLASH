from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.database import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate, ScheduleDetailResponse
from app.dependencies.auth import get_current_admin
from app.dependencies.pagination import get_offset
from app.models.user import User
from app.models.schedule import Schedule
from app.models.booking import Booking
from app.models.trainers import Trainer
from app.models.class_model import ClassModel
from app.constants import BOOKING_STATUS_BOOKED
from datetime import datetime

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/", response_model=list[ScheduleResponse])
async def get_schedules(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), is_active: bool | None = True, db: AsyncSession = Depends(get_db)):
    offset = get_offset(page, limit)
    statement = select(Schedule)

    if is_active is not None:
        statement = statement.where(Schedule.is_active == is_active)

    statement = statement.order_by(Schedule.date, Schedule.start_time, Schedule.id).offset(offset).limit(limit)
    result = await db.execute(statement)
    schedules = result.scalars().all()
    return schedules

@router.post("/", response_model=ScheduleResponse)
async def add_schedule(schedule_data: ScheduleCreate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    if schedule_data.start_time >= schedule_data.end_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be later than start time"
        )
    schedule_start = datetime.combine(
        schedule_data.date,
        schedule_data.start_time
    )

    if schedule_start <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Cannot create a schedule in the past"
        )        

    statement = select(ClassModel).where(
    ClassModel.id == schedule_data.class_id
    )
    result = await db.execute(statement)
    class_item = result.scalar_one_or_none()

    if class_item is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    if not class_item.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot schedule an inactive class"
        )
    
    statement = select(Trainer).where(
    Trainer.id == schedule_data.trainer_id
    )
    result = await db.execute(statement)
    trainer = result.scalar_one_or_none()
    if trainer is None:
        raise HTTPException(
            status_code=404,
            detail="Trainer not found"
        )

    if not trainer.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot schedule an inactive trainer"
        )
    
    new_schedule = Schedule(**schedule_data.model_dump())
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

@router.get("/details", response_model=list[ScheduleDetailResponse])
async def get_schedule_details(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), is_active: bool | None = True, db: AsyncSession = Depends(get_db)):
    offset = get_offset(page, limit)
    statement = select(
        Schedule.id,
        Schedule.class_id,
        ClassModel.title.label("class_title"),
        Schedule.trainer_id,
        Trainer.name.label("trainer_name"),
        Schedule.date,
        Schedule.start_time,
        Schedule.end_time,
        Schedule.max_places,
        (Schedule.max_places - func.count(Booking.id)).label("available_places"),
        func.count(Booking.id).label("booked_places"),
        Schedule.is_active,
        Schedule.created_at
    ).join(ClassModel, ClassModel.id == Schedule.class_id
    ).join(Trainer, Trainer.id == Schedule.trainer_id
    ).outerjoin(Booking, and_(Booking.schedule_id == Schedule.id, Booking.status == BOOKING_STATUS_BOOKED))

    if is_active is not None:
        statement = statement.where(Schedule.is_active == is_active)

    statement = statement.group_by(Schedule.id, Schedule.class_id, ClassModel.title, Schedule.trainer_id, Trainer.name, Schedule.date, Schedule.start_time, Schedule.end_time, Schedule.max_places, Schedule.is_active, Schedule.created_at
    ).order_by(Schedule.date, Schedule.start_time, Schedule.id)

    statement = statement.offset(offset).limit(limit)
    result = await db.execute(statement)
    schedule_details = result.mappings().all()
    return schedule_details

@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: int, schedule_data: ScheduleUpdate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found"
        )

    updated_start_time = (
        schedule_data.start_time
        if schedule_data.start_time is not None
        else schedule.start_time
    )

    updated_end_time = (
        schedule_data.end_time
        if schedule_data.end_time is not None
        else schedule.end_time
    )

    if updated_start_time >= updated_end_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be later than start time"
        )
    
    updated_date = (
        schedule_data.date
        if schedule_data.date is not None
        else schedule.date
    )
    updated_schedule_start = datetime.combine(
        updated_date,
        updated_start_time
    )

    if (
        schedule_data.date is not None
        or schedule_data.start_time is not None
    ):
        if updated_schedule_start <= datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Cannot move a schedule to the past"
            )
    
    if schedule_data.class_id is not None:
        statement = select(ClassModel).where(
            ClassModel.id == schedule_data.class_id
        )
        result = await db.execute(statement)
        class_item = result.scalar_one_or_none()

        if class_item is None:
            raise HTTPException(status_code=404, detail="Class not found")

        if not class_item.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot schedule an inactive class"
            )
    
    if schedule_data.trainer_id is not None:
        statement = select(Trainer).where(
            Trainer.id == schedule_data.trainer_id
        )
        result = await db.execute(statement)
        trainer = result.scalar_one_or_none()

        if trainer is None:
            raise HTTPException(status_code=404, detail="Trainer not found")

        if not trainer.is_active:
            raise HTTPException(
                status_code=400,
                detail="Cannot schedule an inactive trainer"
            )
        
    should_check_bookings = (
        schedule_data.max_places is not None
        or schedule_data.is_active is False
    )

    booked_count = 0

    if should_check_bookings:
        statement = select(func.count(Booking.id)).where(
            Booking.schedule_id == schedule.id,
            Booking.status == BOOKING_STATUS_BOOKED
        )
        result = await db.execute(statement)
        booked_count = result.scalar()

    if (
        schedule_data.max_places is not None
        and schedule_data.max_places < booked_count
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Max places cannot be lower than "
                "the number of active bookings"
            )
        )

    if schedule_data.is_active is False and booked_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate schedule with active bookings"
        )

    for key, value in schedule_data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", response_model=ScheduleResponse)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Not found")
    
    statement = select(func.count(Booking.id)).where(
    Booking.schedule_id == schedule.id,
    Booking.status == BOOKING_STATUS_BOOKED
    )
    result = await db.execute(statement)
    booked_count = result.scalar()

    if booked_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate schedule with active bookings"
        )

    schedule.is_active = False
    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(Schedule).where(Schedule.id == schedule_id)
    result = await db.execute(statement)
    schedule = result.scalar_one_or_none()

    if not schedule:
        raise HTTPException(status_code=404, detail="Not found")
    return schedule