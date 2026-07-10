from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# сделать бзербейз под почту и пароль
class UserCreate(BaseModel):
    name: str   
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 