from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.class_model import ClassModel
from app.schemas.class_schemas import ClassResponse, ClassCreate
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("/", response_model=list[ClassResponse])
async def get_lesson(db: AsyncSession = Depends(get_db)):
    statement = select(ClassModel)
    result = await db.execute(statement)
    lessons = result.scalars()
    return lessons.all()

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