from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    workout_sessions: list  # type: ignore

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    workout_sessions = relationship("WorkoutSession", back_populates="user")
