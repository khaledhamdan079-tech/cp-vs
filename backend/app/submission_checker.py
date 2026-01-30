from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .database import SessionLocal
from .models import Contest, ContestProblem, ContestScore, ContestStatus, User
from .codeforces_api import cf_api


scheduler = AsyncIOScheduler()


def recalculate_contest_scores(contest_id, db: Session):
    """Recalculate contest scores from solved problems to ensure accuracy"""
    from uuid import UUID
    # Convert contest_id to UUID if it's a string
    if isinstance(contest_id, str):
        try:
            contest_id = UUID(contest_id)
        except ValueError:
            pass
    
    # Get all solved problems for this contest
    solved_problems = db.query(ContestProblem).filter(
        ContestProblem.contest_id == contest_id,
        ContestProblem.solved_by.isnot(None)
    ).all()
    
    # Calculate scores for each user
    user_scores = {}
    for problem in solved_problems:
        user_id = problem.solved_by
        if user_id not in user_scores:
            user_scores[user_id] = 0
        user_scores[user_id] += problem.points
    
    # Update contest scores
    for user_id, total_points in user_scores.items():
        score = db.query(ContestScore).filter(
            ContestScore.contest_id == contest_id,
            ContestScore.user_id == user_id
        ).first()
        if score:
            score.total_points = total_points
    
    # Set scores to 0 for users with no solved problems
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if contest:
        for user_id in [contest.user1_id, contest.user2_id]:
            if user_id not in user_scores:
                score = db.query(ContestScore).filter(
                    ContestScore.contest_id == contest_id,
                    ContestScore.user_id == user_id
                ).first()
                if score:
                    score.total_points = 0
    
    db.commit()


async def check_contest_submissions(contest_id):
    """Check submissions for a specific contest"""
    from uuid import UUID
    db = SessionLocal()
    try:
        # Convert contest_id to UUID if it's a string
        if isinstance(contest_id, str):
            try:
                contest_id = UUID(contest_id)
            except ValueError:
                pass
        
        contest = db.query(Contest).filter(Contest.id == contest_id).first()
        if not contest or contest.status != ContestStatus.ACTIVE:
            return
        
        # Get contest problems
        problems = db.query(ContestProblem).filter(
            ContestProblem.contest_id == contest.id,
            ContestProblem.solved_by.is_(None)  # Only check unsolved problems
        ).all()
        
        if not problems:
            return
        
        # Get user handles
        user1 = db.query(User).filter(User.id == contest.user1_id).first()
        user2 = db.query(User).filter(User.id == contest.user2_id).first()
        
        # Check start time for submissions
        start_timestamp = int(contest.start_time.timestamp())
        
        # Check submissions for each problem
        for problem in problems:
            # Check user1
            if not problem.solved_by:
                submission = await cf_api.check_submission(
                    user1.handle,
                    problem.problem_code,
                    start_timestamp
                )
                if submission:
                    problem.solved_by = user1.id
                    problem.solved_at = datetime.utcnow()
                    db.commit()
                    # Recalculate scores to ensure accuracy
                    recalculate_contest_scores(contest.id, db)
                    continue
            
            # Check user2
            if not problem.solved_by:
                submission = await cf_api.check_submission(
                    user2.handle,
                    problem.problem_code,
                    start_timestamp
                )
                if submission:
                    problem.solved_by = user2.id
                    problem.solved_at = datetime.utcnow()
                    db.commit()
                    # Recalculate scores to ensure accuracy
                    recalculate_contest_scores(contest.id, db)
        
        # Check if contest should be completed
        if datetime.utcnow() >= contest.end_time:
            contest.status = ContestStatus.COMPLETED
            db.commit()
            # Remove from scheduler
            scheduler.remove_job(f"check_contest_{contest.id}")
    
    except Exception as e:
        print(f"Error checking submissions for contest {contest_id}: {e}")
    finally:
        db.close()


async def check_all_active_contests():
    """Check all active contests"""
    db = SessionLocal()
    try:
        active_contests = db.query(Contest).filter(
            Contest.status == ContestStatus.ACTIVE
        ).all()
        
        for contest in active_contests:
            await check_contest_submissions(str(contest.id))
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Check all active contests every 10 seconds
    scheduler.add_job(
        check_all_active_contests,
        'interval',
        seconds=10,
        id='check_active_contests'
    )
    
    # Also check for contests that need to be activated
    scheduler.add_job(
        activate_scheduled_contests,
        'interval',
        seconds=60,
        id='activate_contests'
    )
    
    scheduler.start()


async def activate_scheduled_contests():
    """Activate contests that have reached their start time"""
    db = SessionLocal()
    try:
        scheduled_contests = db.query(Contest).filter(
            Contest.status == ContestStatus.SCHEDULED,
            Contest.start_time <= datetime.utcnow()
        ).all()
        
        for contest in scheduled_contests:
            contest.status = ContestStatus.ACTIVE
            db.commit()
            
            # Schedule individual check for this contest
            scheduler.add_job(
                check_contest_submissions,
                'interval',
                seconds=10,
                args=[str(contest.id)],
                id=f"check_contest_{contest.id}"
            )
    finally:
        db.close()
