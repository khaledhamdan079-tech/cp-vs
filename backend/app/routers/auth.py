from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token
from ..auth import verify_password, get_password_hash, create_access_token
from ..config import settings
from ..dependencies import get_current_user
from ..codeforces_api import cf_api

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Validate handle
    if not user_data.handle or not user_data.handle.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Handle cannot be empty"
        )
    
    handle = user_data.handle.strip()
    
    # Validate password
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.handle == handle).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Handle already registered"
        )
    
    # Validate Codeforces handle
    is_valid = await cf_api.validate_handle(handle)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Codeforces handle. Please check the handle and try again."
        )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            handle=handle,
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.handle == user_data.handle).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect handle or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
