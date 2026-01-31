from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_, func
from ..database import get_db
from ..models import User, Contest, ContestScore, ContestStatus, RatingHistory
from ..schemas import UserResponse, UserSearchResponse, LeaderboardEntryResponse, UserProfileResponse
from ..dependencies import get_confirmed_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_confirmed_user)):
    return current_user


@router.get("/search", response_model=List[UserSearchResponse])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Search users by handle (for challenge creation)"""
    users = db.query(User).filter(
        User.handle.ilike(f"%{q}%"),
        User.id != current_user.id  # Exclude current user
    ).limit(limit).all()
    
    return users


@router.get("/leaderboard", response_model=List[LeaderboardEntryResponse])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    offset: int = Query(0, ge=0, description="Number of users to skip"),
    db: Session = Depends(get_db)
):
    """Get leaderboard of users ordered by rating (public endpoint)"""
    users = db.query(User).order_by(User.rating.desc()).offset(offset).limit(limit).all()
    
    # Calculate rank (1-indexed)
    rank = offset + 1
    result = []
    for user in users:
        result.append(LeaderboardEntryResponse(
            rank=rank,
            handle=user.handle,
            rating=user.rating,
            id=user.id
        ))
        rank += 1
    
    return result


@router.get("/{handle}/profile", response_model=UserProfileResponse)
async def get_user_profile(handle: str, db: Session = Depends(get_db)):
    """Get detailed user profile (public endpoint)"""
    try:
        user = db.query(User).filter(User.handle == handle).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ensure user has rating (default to 1000 if missing due to migration)
        if not hasattr(user, 'rating') or user.rating is None:
            user.rating = 1000
            db.commit()
        
        # Get contest statistics
        user_contests = db.query(Contest).filter(
            or_(
                Contest.user1_id == user.id,
                Contest.user2_id == user.id
            ),
            Contest.status == ContestStatus.COMPLETED
        ).all()
        
        total_contests = len(user_contests)
        wins = 0
        losses = 0
        draws = 0
        
        for contest in user_contests:
            score1 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user1_id
            ).first()
            score2 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user2_id
            ).first()
            
            if score1 and score2:
                user_points = score1.total_points if contest.user1_id == user.id else score2.total_points
                opponent_points = score2.total_points if contest.user1_id == user.id else score1.total_points
                
                if user_points > opponent_points:
                    wins += 1
                elif opponent_points > user_points:
                    losses += 1
                else:
                    draws += 1
        
        win_rate = (wins / total_contests * 100) if total_contests > 0 else 0.0
        
        return UserProfileResponse(
            id=user.id,
            handle=user.handle,
            rating=getattr(user, 'rating', 1000),  # Fallback to 1000 if rating missing
            created_at=user.created_at,
            total_contests=total_contests,
            wins=wins,
            losses=losses,
            draws=draws,
            win_rate=round(win_rate, 2)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_profile: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )


@router.get("/{handle}", response_model=UserResponse)
async def get_user_by_handle(handle: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.handle == handle).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
