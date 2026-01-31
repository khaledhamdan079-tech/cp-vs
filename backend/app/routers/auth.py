from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token, RegistrationResponse, ConfirmationStatusResponse
from ..auth import verify_password, get_password_hash, create_access_token
from ..config import settings
from ..dependencies import get_current_user
from ..codeforces_api import cf_api

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=RegistrationResponse)
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
    
    # Create new user with confirmation fields
    try:
        hashed_password = get_password_hash(user_data.password)
        now = datetime.utcnow()
        confirmation_deadline = now + timedelta(minutes=5)
        
        new_user = User(
            handle=handle,
            password_hash=hashed_password,
            is_confirmed=False,
            confirmation_deadline=confirmation_deadline
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create a token for the user so they can check confirmation status
        # This token will work even though user is not confirmed
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(new_user.id)}, expires_delta=access_token_expires
        )
        
        # Return registration response with confirmation details and token
        return RegistrationResponse(
            id=new_user.id,
            handle=new_user.handle,
            rating=new_user.rating,
            created_at=new_user.created_at,
            is_confirmed=False,
            problem_link="https://codeforces.com/problemset/problem/4/A",
            deadline=confirmation_deadline,
            access_token=access_token,
            token_type="bearer"
        )
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
    
    # Check if user is confirmed
    if not user.is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not confirmed. Please complete the confirmation process by submitting a solution to the Watermelon problem (4A) on Codeforces.",
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_confirmed_user)):
    return current_user


@router.get("/confirmation-status", response_model=ConfirmationStatusResponse)
async def get_confirmation_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get confirmation status for the current user.
    Uses get_current_user (not get_confirmed_user) to allow unconfirmed users to check status.
    """
    now = datetime.utcnow()
    time_remaining = None
    
    if current_user.confirmation_deadline:
        deadline = current_user.confirmation_deadline
        if deadline > now:
            time_remaining = int((deadline - now).total_seconds())
        else:
            time_remaining = 0
    
    return ConfirmationStatusResponse(
        is_confirmed=current_user.is_confirmed,
        deadline=current_user.confirmation_deadline,
        time_remaining=time_remaining,
        problem_link="https://codeforces.com/problemset/problem/4/A"
    )
