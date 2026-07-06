from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.trainers import Trainer
from app.schemas.trainers import TrainerResponse, TrainerCreate, TrainerUpdate
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/trainers", tags=["trainers"])

@router.get("/", response_model=list[TrainerResponse])
async def get_trainers(db: AsyncSession = Depends(get_db)):
    statement = select(Trainer).where(Trainer.is_active == True).order_by(Trainer.id)
    result = await db.execute(statement)
    trainers = result.scalars().all()
    return trainers

@router.get("/{trainer_id}", response_model=TrainerResponse)
async def get_trainer(trainer_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(Trainer).where(Trainer.id == trainer_id)
    result = await db.execute(statement)
    trainer = result.scalar_one_or_none()

    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return trainer

@router.post("/", response_model=TrainerResponse)
async def create_trainer(trainer_data: TrainerCreate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    new_trainer = Trainer(**trainer_data.model_dump())
    db.add(new_trainer)
    await db.commit()
    await db.refresh(new_trainer)
    return new_trainer

@router.patch("/{trainer_id}", response_model=TrainerResponse)
async def update_trainer(trainer_id: int, trainer_data: TrainerUpdate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Trainer).where(Trainer.id == trainer_id)
    result = await db.execute(statement)
    trainer = result.scalar_one_or_none()

    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    for key, value in trainer_data.model_dump(exclude_unset=True).items():
        setattr(trainer, key, value)

    await db.commit()
    await db.refresh(trainer)
    return trainer

@router.delete("/{trainer_id}", response_model=TrainerResponse)
async def delete_trainer(trainer_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(Trainer).where(Trainer.id == trainer_id)
    result = await db.execute(statement)
    trainer = result.scalar_one_or_none()

    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    trainer.is_active = False
    await db.commit()
    await db.refresh(trainer)
    return trainer