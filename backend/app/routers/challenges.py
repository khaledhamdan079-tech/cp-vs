from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import User, Challenge, ChallengeStatus
from ..schemas import ChallengeCreate, ChallengeResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate difficulty
    if challenge_data.difficulty not in [1, 2, 3, 4]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Difficulty must be between 1 and 4"
        )
    
    # Find challenged user
    challenged_user = None
    if challenge_data.challenged_user_id:
        challenged_user = db.query(User).filter(User.id == challenge_data.challenged_user_id).first()
    elif challenge_data.challenged_handle:
        challenged_user = db.query(User).filter(User.handle == challenge_data.challenged_handle).first()
    
    if not challenged_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenged user not found"
        )
    
    if challenged_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot challenge yourself"
        )
    
    # Create challenge
    new_challenge = Challenge(
        challenger_id=current_user.id,
        challenged_id=challenged_user.id,
        difficulty=challenge_data.difficulty,
        suggested_start_time=challenge_data.suggested_start_time,
        status=ChallengeStatus.PENDING
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    
    return new_challenge


@router.get("/", response_model=List[ChallengeResponse])
async def list_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all challenges sent or received by the current user"""
    challenges = db.query(Challenge).filter(
        (Challenge.challenger_id == current_user.id) |
        (Challenge.challenged_id == current_user.id)
    ).order_by(Challenge.created_at.desc()).all()
    
    return challenges


@router.post("/{challenge_id}/accept", response_model=ChallengeResponse)
async def accept_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if challenge.challenged_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the challenged user"
        )
    
    if challenge.status != ChallengeStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge is not pending"
        )
    
    challenge.status = ChallengeStatus.ACCEPTED
    db.commit()
    db.refresh(challenge)
    
    # Create contest (will be handled by contest creation endpoint)
    from . import contests as contests_module
    await contests_module.create_contest_from_challenge(challenge, db)
    
    return challenge


@router.post("/{challenge_id}/reject", response_model=ChallengeResponse)
async def reject_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found"
        )
    
    if challenge.challenged_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the challenged user"
        )
    
    if challenge.status != ChallengeStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge is not pending"
        )
    
    challenge.status = ChallengeStatus.REJECTED
    db.commit()
    db.refresh(challenge)
    
    return challenge
