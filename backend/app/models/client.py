from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func
from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id", ondelete="SET NULL"), nullable=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    phone_number = Column(String, nullable=True)
    is_child = Column(Boolean, default=False, nullable=False)
    guardian_name = Column(String, nullable=True)
    guardian_phone = Column(String, nullable=True)
    medical_notes = Column(String, nullable=True)
    personal_data_consent = Column(Boolean, default=False, nullable=False)
    marketing_consent = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)