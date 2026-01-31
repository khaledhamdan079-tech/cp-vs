from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Challenge, ChallengeStatus, Contest, ContestStatus
from ..schemas import ChallengeCreate, ChallengeResponse
from ..dependencies import get_confirmed_user

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


@router.post("/", response_model=ChallengeResponse)
async def create_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_confirmed_user),
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
    
    # Check for existing pending challenge between the same two users (in either direction)
    existing_pending = db.query(Challenge).filter(
        Challenge.status == ChallengeStatus.PENDING,
        or_(
            (Challenge.challenger_id == current_user.id) & (Challenge.challenged_id == challenged_user.id),
            (Challenge.challenger_id == challenged_user.id) & (Challenge.challenged_id == current_user.id)
        )
    ).first()
    
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is already a pending challenge between you and this user. Please wait for it to be accepted or rejected."
        )
    
    # Check for overlapping contests for both users
    # Contest duration is 2 hours
    proposed_start_time = challenge_data.suggested_start_time
    proposed_end_time = proposed_start_time + timedelta(hours=2)
    
    # Check for overlapping contests
    # A contest overlaps if: proposed_start < existing_end AND proposed_end > existing_start
    overlapping_contest = db.query(Contest).filter(
        Contest.status.in_([ContestStatus.SCHEDULED, ContestStatus.ACTIVE]),
        Contest.start_time < proposed_end_time,
        Contest.end_time > proposed_start_time,
        or_(
            Contest.user1_id == current_user.id,
            Contest.user2_id == current_user.id,
            Contest.user1_id == challenged_user.id,
            Contest.user2_id == challenged_user.id
        )
    ).first()
    
    if overlapping_contest:
        # Get user handles for the overlapping contest
        overlapping_user1 = db.query(User).filter(User.id == overlapping_contest.user1_id).first()
        overlapping_user2 = db.query(User).filter(User.id == overlapping_contest.user2_id).first()
        
        # Determine which user has the conflict
        conflicting_user = None
        if overlapping_contest.user1_id == current_user.id or overlapping_contest.user2_id == current_user.id:
            conflicting_user = current_user.handle
        elif overlapping_contest.user1_id == challenged_user.id or overlapping_contest.user2_id == challenged_user.id:
            conflicting_user = challenged_user.handle
        
        # Format the error message
        contest_info = f"{overlapping_user1.handle if overlapping_user1 else 'User1'} vs {overlapping_user2.handle if overlapping_user2 else 'User2'}"
        time_info = f"{overlapping_contest.start_time.strftime('%Y-%m-%d %H:%M')} - {overlapping_contest.end_time.strftime('%Y-%m-%d %H:%M')}"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{conflicting_user if conflicting_user else 'One of the users'} already has a contest scheduled/active during this time ({contest_info}, {time_info}). Please choose a different time."
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
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Get all challenges sent or received by the current user"""
    challenges = db.query(Challenge).filter(
        (Challenge.challenger_id == current_user.id) |
        (Challenge.challenged_id == current_user.id)
    ).order_by(Challenge.created_at.desc()).all()
    
    return challenges


@router.get("/pending-count")
async def get_pending_challenges_count(
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Get count of pending challenges received by the current user"""
    count = db.query(Challenge).filter(
        Challenge.challenged_id == current_user.id,
        Challenge.status == ChallengeStatus.PENDING
    ).count()
    
    return {"count": count}


@router.post("/{challenge_id}/accept", response_model=ChallengeResponse)
async def accept_challenge(
    challenge_id: str,
    current_user: User = Depends(get_confirmed_user),
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
    current_user: User = Depends(get_confirmed_user),
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
