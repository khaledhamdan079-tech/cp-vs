from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models import (
    User, Challenge, Contest, ContestProblem, ContestScore, RatingHistory,
    ChallengeStatus, ContestStatus
)
from ..schemas import ContestResponse, ContestProblemResponse, ContestScoreResponse, PublicContestResponse
from ..dependencies import get_confirmed_user
from ..problem_selector import get_unsolved_problems
from sqlalchemy import or_, func, desc

router = APIRouter(prefix="/api/contests", tags=["contests"])


# Public endpoints (no authentication required)
public_router = APIRouter(prefix="/api/contests/public", tags=["contests-public"])


@public_router.get("/latest", response_model=List[PublicContestResponse])
async def get_latest_contests(
    limit: int = Query(10, ge=1, le=50, description="Number of contests to return"),
    db: Session = Depends(get_db)
):
    """Get latest completed contests (public endpoint)"""
    contests = db.query(Contest).filter(
        Contest.status == ContestStatus.COMPLETED
    ).order_by(Contest.end_time.desc()).limit(limit).all()
    
    result = []
    for contest in contests:
        user1 = db.query(User).filter(User.id == contest.user1_id).first()
        user2 = db.query(User).filter(User.id == contest.user2_id).first()
        
        # Get final scores
        score1 = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id,
            ContestScore.user_id == contest.user1_id
        ).first()
        score2 = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id,
            ContestScore.user_id == contest.user2_id
        ).first()
        
        # Get rating changes
        history1 = db.query(RatingHistory).filter(
            RatingHistory.contest_id == contest.id,
            RatingHistory.user_id == contest.user1_id
        ).first()
        history2 = db.query(RatingHistory).filter(
            RatingHistory.contest_id == contest.id,
            RatingHistory.user_id == contest.user2_id
        ).first()
        
        result.append(PublicContestResponse(
            id=contest.id,
            user1_handle=user1.handle if user1 else "Unknown",
            user2_handle=user2.handle if user2 else "Unknown",
            difficulty=contest.difficulty,
            start_time=contest.start_time,
            end_time=contest.end_time,
            status=contest.status.value,
            user1_points=score1.total_points if score1 else 0,
            user2_points=score2.total_points if score2 else 0,
            user1_rating_change=history1.rating_change if history1 else None,
            user2_rating_change=history2.rating_change if history2 else None
        ))
    
    return result


@public_router.get("/top", response_model=List[PublicContestResponse])
async def get_top_contests(
    limit: int = Query(10, ge=1, le=50, description="Number of contests to return"),
    sort_by: str = Query("rating_change", description="Sort by: rating_change, points, competitiveness"),
    db: Session = Depends(get_db)
):
    """Get top contests by various criteria (public endpoint)"""
    contests_query = db.query(Contest).filter(
        Contest.status == ContestStatus.COMPLETED
    )
    
    if sort_by == "rating_change":
        # Sort by highest combined absolute rating change
        contests = contests_query.order_by(Contest.end_time.desc()).limit(limit * 2).all()
        # Calculate rating change for each and sort
        contest_data = []
        for contest in contests:
            history1 = db.query(RatingHistory).filter(
                RatingHistory.contest_id == contest.id,
                RatingHistory.user_id == contest.user1_id
            ).first()
            history2 = db.query(RatingHistory).filter(
                RatingHistory.contest_id == contest.id,
                RatingHistory.user_id == contest.user2_id
            ).first()
            
            total_change = abs(history1.rating_change if history1 else 0) + abs(history2.rating_change if history2 else 0)
            contest_data.append((total_change, contest))
        
        contest_data.sort(key=lambda x: x[0], reverse=True)
        contests = [c[1] for c in contest_data[:limit]]
    elif sort_by == "points":
        # Sort by highest total points scored
        contests = contests_query.order_by(Contest.end_time.desc()).limit(limit * 2).all()
        contest_data = []
        for contest in contests:
            score1 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user1_id
            ).first()
            score2 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user2_id
            ).first()
            
            total_points = (score1.total_points if score1 else 0) + (score2.total_points if score2 else 0)
            contest_data.append((total_points, contest))
        
        contest_data.sort(key=lambda x: x[0], reverse=True)
        contests = [c[1] for c in contest_data[:limit]]
    else:  # competitiveness (closest scores)
        contests = contests_query.order_by(Contest.end_time.desc()).limit(limit * 2).all()
        contest_data = []
        for contest in contests:
            score1 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user1_id
            ).first()
            score2 = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id,
                ContestScore.user_id == contest.user2_id
            ).first()
            
            point_diff = abs((score1.total_points if score1 else 0) - (score2.total_points if score2 else 0))
            contest_data.append((point_diff, contest))
        
        contest_data.sort(key=lambda x: x[0])  # Sort by smallest difference
        contests = [c[1] for c in contest_data[:limit]]
    
    result = []
    for contest in contests:
        user1 = db.query(User).filter(User.id == contest.user1_id).first()
        user2 = db.query(User).filter(User.id == contest.user2_id).first()
        
        score1 = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id,
            ContestScore.user_id == contest.user1_id
        ).first()
        score2 = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id,
            ContestScore.user_id == contest.user2_id
        ).first()
        
        history1 = db.query(RatingHistory).filter(
            RatingHistory.contest_id == contest.id,
            RatingHistory.user_id == contest.user1_id
        ).first()
        history2 = db.query(RatingHistory).filter(
            RatingHistory.contest_id == contest.id,
            RatingHistory.user_id == contest.user2_id
        ).first()
        
        result.append(PublicContestResponse(
            id=contest.id,
            user1_handle=user1.handle if user1 else "Unknown",
            user2_handle=user2.handle if user2 else "Unknown",
            difficulty=contest.difficulty,
            start_time=contest.start_time,
            end_time=contest.end_time,
            status=contest.status.value,
            user1_points=score1.total_points if score1 else 0,
            user2_points=score2.total_points if score2 else 0,
            user1_rating_change=history1.rating_change if history1 else None,
            user2_rating_change=history2.rating_change if history2 else None
        ))
    
    return result


async def create_contest_from_challenge(challenge: Challenge, db: Session):
    """Create a contest when a challenge is accepted"""
    # Check if contest already exists
    existing_contest = db.query(Contest).filter(Contest.challenge_id == challenge.id).first()
    if existing_contest:
        return existing_contest
    
    # Check for overlapping contests for both users
    start_time = challenge.suggested_start_time
    end_time = start_time + timedelta(hours=2)  # Default 2 hours duration
    
    # Check for overlapping contests for both users
    # A contest overlaps if: start_time < other_end_time AND end_time > other_start_time
    overlapping = db.query(Contest).filter(
        Contest.status.in_([ContestStatus.SCHEDULED, ContestStatus.ACTIVE]),
        Contest.start_time < end_time,
        Contest.end_time > start_time,
        or_(
            Contest.user1_id == challenge.challenger_id,
            Contest.user2_id == challenge.challenger_id,
            Contest.user1_id == challenge.challenged_id,
            Contest.user2_id == challenge.challenged_id
        )
    ).first()
    
    if overlapping:
        user1 = db.query(User).filter(User.id == overlapping.user1_id).first()
        user2 = db.query(User).filter(User.id == overlapping.user2_id).first()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"One of the users already has a contest scheduled/active during this time ({user1.handle if user1 else 'User1'} vs {user2.handle if user2 else 'User2'}, {overlapping.start_time} - {overlapping.end_time})"
        )
    
    # Create contest
    contest = Contest(
        challenge_id=challenge.id,
        user1_id=challenge.challenger_id,
        user2_id=challenge.challenged_id,
        difficulty=challenge.difficulty,
        start_time=start_time,
        end_time=end_time,
        status=ContestStatus.SCHEDULED
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    
    # Create initial scores (problems will be selected later by scheduled task)
    user1 = db.query(User).filter(User.id == challenge.challenger_id).first()
    user2 = db.query(User).filter(User.id == challenge.challenged_id).first()
    
    score1 = ContestScore(contest_id=contest.id, user_id=user1.id, total_points=0)
    score2 = ContestScore(contest_id=contest.id, user_id=user2.id, total_points=0)
    db.add(score1)
    db.add(score2)
    db.commit()
    
    return contest


@router.get("/upcoming", response_model=List[ContestResponse])
async def get_upcoming_contests(
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of contests to return")
):
    """Get upcoming scheduled contests for the current user"""
    now = datetime.utcnow()
    contests = db.query(Contest).filter(
        (Contest.user1_id == current_user.id) |
        (Contest.user2_id == current_user.id),
        Contest.status.in_([ContestStatus.SCHEDULED, ContestStatus.ACTIVE]),
        Contest.start_time >= now
    ).order_by(Contest.start_time.asc()).limit(limit).all()
    
    result = []
    for contest in contests:
        user1 = db.query(User).filter(User.id == contest.user1_id).first()
        user2 = db.query(User).filter(User.id == contest.user2_id).first()
        
        # Get problems (only reveal if contest has started)
        problems_data = []
        if contest.status == ContestStatus.ACTIVE or datetime.utcnow() >= contest.start_time:
            problems = db.query(ContestProblem).filter(
                ContestProblem.contest_id == contest.id
            ).all()
            problems_data = [ContestProblemResponse.model_validate(p) for p in problems]
        
        # Get scores
        scores = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id
        ).all()
        scores_data = []
        for score in scores:
            user = db.query(User).filter(User.id == score.user_id).first()
            scores_data.append(ContestScoreResponse(
                user_id=score.user_id,
                user_handle=user.handle,
                total_points=score.total_points
            ))
        
        result.append(ContestResponse(
            id=contest.id,
            user1_id=contest.user1_id,
            user2_id=contest.user2_id,
            user1_handle=user1.handle,
            user2_handle=user2.handle,
            difficulty=contest.difficulty,
            start_time=contest.start_time,
            end_time=contest.end_time,
            status=contest.status.value,
            problems=problems_data,
            scores=scores_data
        ))
    
    return result


@router.get("/", response_model=List[ContestResponse])
async def list_contests(
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Get all contests for the current user"""
    contests = db.query(Contest).filter(
        (Contest.user1_id == current_user.id) |
        (Contest.user2_id == current_user.id)
    ).order_by(Contest.created_at.desc()).all()
    
    result = []
    for contest in contests:
        user1 = db.query(User).filter(User.id == contest.user1_id).first()
        user2 = db.query(User).filter(User.id == contest.user2_id).first()
        
        # Get problems (only reveal if contest has started)
        problems_data = []
        if contest.status in [ContestStatus.ACTIVE, ContestStatus.COMPLETED] or datetime.utcnow() >= contest.start_time:
            problems = db.query(ContestProblem).filter(
                ContestProblem.contest_id == contest.id
            ).all()
            problems_data = [ContestProblemResponse.model_validate(p) for p in problems]
        
        # Get scores - recalculate from solved problems to ensure accuracy
        solved_problems = db.query(ContestProblem).filter(
            ContestProblem.contest_id == contest.id,
            ContestProblem.solved_by.isnot(None)
        ).all()
        
        # Calculate scores from solved problems
        user_scores = {}
        for problem in solved_problems:
            user_id = problem.solved_by
            if user_id not in user_scores:
                user_scores[user_id] = 0
            user_scores[user_id] += problem.points
        
        # Get scores from database and update if needed
        scores = db.query(ContestScore).filter(
            ContestScore.contest_id == contest.id
        ).all()
        scores_data = []
        for score in scores:
            user = db.query(User).filter(User.id == score.user_id).first()
            # Use calculated score if available, otherwise use stored score
            calculated_points = user_scores.get(score.user_id, 0)
            # Update stored score if different
            if score.total_points != calculated_points:
                score.total_points = calculated_points
                db.commit()
            scores_data.append(ContestScoreResponse(
                user_id=score.user_id,
                user_handle=user.handle,
                total_points=calculated_points
            ))
        
        result.append(ContestResponse(
            id=contest.id,
            user1_id=contest.user1_id,
            user2_id=contest.user2_id,
            user1_handle=user1.handle,
            user2_handle=user2.handle,
            difficulty=contest.difficulty,
            start_time=contest.start_time,
            end_time=contest.end_time,
            status=contest.status.value,
            problems=problems_data,
            scores=scores_data
        ))
    
    return result


@router.get("/{contest_id}", response_model=ContestResponse)
async def get_contest(
    contest_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    if contest.user1_id != current_user.id and contest.user2_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this contest"
        )
    
    user1 = db.query(User).filter(User.id == contest.user1_id).first()
    user2 = db.query(User).filter(User.id == contest.user2_id).first()
    
    # Get problems (only reveal if contest has started)
    problems_data = []
    if contest.status in [ContestStatus.ACTIVE, ContestStatus.COMPLETED] or datetime.utcnow() >= contest.start_time:
        problems = db.query(ContestProblem).filter(
            ContestProblem.contest_id == contest.id
        ).all()
        problems_data = [ContestProblemResponse.model_validate(p) for p in problems]
    
    # Get scores - recalculate from solved problems to ensure accuracy
    solved_problems = db.query(ContestProblem).filter(
        ContestProblem.contest_id == contest.id,
        ContestProblem.solved_by.isnot(None)
    ).all()
    
    # Calculate scores from solved problems
    user_scores = {}
    for problem in solved_problems:
        user_id = problem.solved_by
        if user_id not in user_scores:
            user_scores[user_id] = 0
        user_scores[user_id] += problem.points
    
    # Get scores from database and update if needed
    scores = db.query(ContestScore).filter(
        ContestScore.contest_id == contest.id
    ).all()
    scores_data = []
    for score in scores:
        user = db.query(User).filter(User.id == score.user_id).first()
        # Use calculated score if available, otherwise use stored score
        calculated_points = user_scores.get(score.user_id, 0)
        # Update stored score if different
        if score.total_points != calculated_points:
            score.total_points = calculated_points
            db.commit()
        scores_data.append(ContestScoreResponse(
            user_id=score.user_id,
            user_handle=user.handle,
            total_points=calculated_points
        ))
    
    return ContestResponse(
        id=contest.id,
        user1_id=contest.user1_id,
        user2_id=contest.user2_id,
        user1_handle=user1.handle,
        user2_handle=user2.handle,
        difficulty=contest.difficulty,
        start_time=contest.start_time,
        end_time=contest.end_time,
        status=contest.status.value,
        problems=problems_data,
        scores=scores_data
    )


@router.get("/{contest_id}/problems", response_model=List[ContestProblemResponse])
async def get_contest_problems(
    contest_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )
    
    if contest.user1_id != current_user.id and contest.user2_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this contest"
        )
    
    # Only reveal problems if contest has started
    if contest.status not in [ContestStatus.ACTIVE, ContestStatus.COMPLETED] and datetime.utcnow() < contest.start_time:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contest has not started yet"
        )
    
    problems = db.query(ContestProblem).filter(
        ContestProblem.contest_id == contest.id
    ).all()
    
    return [ContestProblemResponse.model_validate(p) for p in problems]
