from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate
from app.dependencies.auth import get_current_admin
from app.models.user import User
from app.models.schedule import Schedule

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/", response_model=list[ScheduleResponse])
async def get_schedules(db: AsyncSession = Depends(get_db)):
    statement = select(Schedule).where(Schedule.is_active == True).order_by(Schedule.date, Schedule.start_time)
    
    result = await db.execute(statement)
    schedules = result.scalars()
    return schedules.all()

@router.post("/", response_model=ScheduleResponse)
async def add_schedule(schedule_data: ScheduleCreate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    new_schedule = Schedule(**schedule_data.model_dump())
    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)
    return new_schedule

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