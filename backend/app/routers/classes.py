from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.class_model import ClassModel
from app.schemas.class_schemas import ClassResponse, ClassCreate, ClassUpdate
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("/", response_model=list[ClassResponse])
async def get_lesson(page: int = 1,limit: int = 10,is_active: bool | None = True,db: AsyncSession = Depends(get_db),):
    offset = (page - 1) * limit
    statement = select(ClassModel)
    
    if is_active is not None:
        statement = statement.where(ClassModel.is_active == is_active)

    statement = statement.order_by(ClassModel.id).offset(offset).limit(limit)
    result = await db.execute(statement)
    classes = result.scalars().all()
    return classes

@router.post("/", response_model=ClassResponse)
async def add_lessons(class_data: ClassCreate, db: AsyncSession=Depends(get_db), current_admin: User = Depends(get_current_admin)):
    new_class = ClassModel(title=class_data.title,description=class_data.description,level=class_data.level,duration_minutes=class_data.duration_minutes)
    db.add(new_class)
    await db.commit()
    await db.refresh(new_class)
    return new_class

@router.get("/{class_id}", response_model=ClassResponse)
async def get_lesson_id(class_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(ClassModel).where(ClassModel.id == class_id)
    result = await db.execute(statement)
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Not found")
    return lesson

@router.patch("/{class_id}", response_model=ClassResponse)
async def update_lesson(class_id: int, class_data: ClassUpdate, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(ClassModel).where(ClassModel.id == class_id)
    result = await db.execute(statement)
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Not found")

    for key, value in class_data.model_dump(exclude_unset=True).items():
        setattr(lesson, key, value)

    await db.commit()
    await db.refresh(lesson)
    return lesson

@router.delete("/{class_id}", response_model=ClassResponse)
async def delete_lesson(class_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    statement = select(ClassModel).where(ClassModel.id == class_id)
    result = await db.execute(statement)
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(status_code=404, detail="Not found")

    lesson.is_active = False
    await db.commit()
    await db.refresh(lesson)
    return lesson