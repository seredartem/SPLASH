from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.database import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate, ScheduleDetailResponse
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.models.schedule import Schedule
from app.models.booking import Booking
from app.models.trainers import Trainer
from app.models.class_model import ClassModel
from app.constants import BOOKING_STATUS_BOOKED

router = APIRouter(prefix="/schedules", tags=["schedules"])

# pagination
@router.get("/", response_model=list[ScheduleResponse])
async def get_schedules(page: int = 1,limit: int = 10, is_active: bool | None = True, db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    statement = select(Schedule)

    if is_active is not None:
        statement = statement.where(Schedule.is_active == is_active)

    statement = statement.order_by(Schedule.date, Schedule.start_time).offset(offset).limit(limit)
    result = await db.execute(statement)
    schedules = result.scalars().all()
    return schedules

@router.post("/", response_model=ScheduleResponse)
async def add_schedule(schedule_data: ScheduleCreate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    new_schedule = Schedule(**schedule_data.model_dump())
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

@router.get("/details", response_model=list[ScheduleDetailResponse])
async def get_schedule_details(page: int = 1, limit: int = 10, is_active: bool | None = True, db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
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
    ).order_by(Schedule.date, Schedule.start_time)

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
        raise HTTPException(status_code=404, detail="Not found")

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