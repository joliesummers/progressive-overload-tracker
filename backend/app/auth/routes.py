from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .models import Token, UserCreate, User
from .security import (
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: Implement actual user authentication against database
    # For now, accept any username/password combination for testing
    user = User(
        id=1,
        email=form_data.username,
        full_name="Test User",
        is_active=True
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    # TODO: Implement actual user registration
    # For now, return mock user
    return User(
        id=1,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True
    )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
