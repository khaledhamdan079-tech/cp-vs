from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import UserResponse, UserSearchResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=List[UserSearchResponse])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search users by handle (for challenge creation)"""
    users = db.query(User).filter(
        User.handle.ilike(f"%{q}%"),
        User.id != current_user.id  # Exclude current user
    ).limit(limit).all()
    
    return users


@router.get("/{handle}", response_model=UserResponse)
async def get_user_by_handle(handle: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.handle == handle).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
