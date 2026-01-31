from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import asyncio
from uuid import UUID
from .database import SessionLocal
from .models import Contest, ContestProblem, ContestScore, ContestStatus, User, RatingHistory
from .codeforces_api import cf_api
from .rating import calculate_elo_rating, determine_contest_scores
from .problem_selector import get_unsolved_problems


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


def update_ratings_after_contest(contest_id, db: Session):
    """Update user ratings after a contest is completed"""
    # Convert contest_id to UUID if it's a string
    if isinstance(contest_id, str):
        try:
            contest_id = UUID(contest_id)
        except ValueError:
            pass
    
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest or contest.status != ContestStatus.COMPLETED:
        return
    
    # Get final scores for both users
    score1 = db.query(ContestScore).filter(
        ContestScore.contest_id == contest.id,
        ContestScore.user_id == contest.user1_id
    ).first()
    score2 = db.query(ContestScore).filter(
        ContestScore.contest_id == contest.id,
        ContestScore.user_id == contest.user2_id
    ).first()
    
    if not score1 or not score2:
        return
    
    # Get users
    user1 = db.query(User).filter(User.id == contest.user1_id).first()
    user2 = db.query(User).filter(User.id == contest.user2_id).first()
    
    if not user1 or not user2:
        return
    
    # Check if ratings have already been updated for this contest
    existing_history = db.query(RatingHistory).filter(
        RatingHistory.contest_id == contest.id
    ).first()
    
    if existing_history:
        # Ratings already updated for this contest
        return
    
    # Get current ratings
    rating1_before = user1.rating
    rating2_before = user2.rating
    
    # Determine Elo scores based on points
    elo_score1, elo_score2 = determine_contest_scores(score1.total_points, score2.total_points)
    
    # Calculate new ratings
    new_rating1, new_rating2, rating_change1, rating_change2 = calculate_elo_rating(
        rating1_before, rating2_before, elo_score1, elo_score2
    )
    
    # Update user ratings
    user1.rating = new_rating1
    user2.rating = new_rating2
    
    # Create rating history entries
    history1 = RatingHistory(
        user_id=user1.id,
        contest_id=contest.id,
        rating_before=rating1_before,
        rating_after=new_rating1,
        rating_change=rating_change1
    )
    history2 = RatingHistory(
        user_id=user2.id,
        contest_id=contest.id,
        rating_before=rating2_before,
        rating_after=new_rating2,
        rating_change=rating_change2
    )
    
    db.add(history1)
    db.add(history2)
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
        
        # Check if problems exist - if not, return early (problems may not be selected yet)
        all_problems = db.query(ContestProblem).filter(
            ContestProblem.contest_id == contest.id
        ).all()
        
        if not all_problems:
            # Problems haven't been selected yet, skip checking submissions
            return
        
        # Get contest problems that haven't been solved yet
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
            if not problem.solved_by:
                # Check both users simultaneously
                submission1_task = cf_api.check_submission(
                    user1.handle,
                    problem.problem_code,
                    start_timestamp
                )
                submission2_task = cf_api.check_submission(
                    user2.handle,
                    problem.problem_code,
                    start_timestamp
                )
                
                # Wait for both checks to complete
                submission1, submission2 = await asyncio.gather(submission1_task, submission2_task)
                
                # Determine who solved first based on timestamps
                if submission1 and submission2:
                    # Both solved - compare timestamps
                    time1 = submission1.get("creationTimeSeconds", 0)
                    time2 = submission2.get("creationTimeSeconds", 0)
                    if time1 <= time2:
                        # User1 solved first (or at same time, tie goes to user1)
                        problem.solved_by = user1.id
                        problem.solved_at = datetime.fromtimestamp(time1)
                    else:
                        # User2 solved first
                        problem.solved_by = user2.id
                        problem.solved_at = datetime.fromtimestamp(time2)
                    db.commit()
                    recalculate_contest_scores(contest.id, db)
                elif submission1:
                    # Only user1 solved
                    problem.solved_by = user1.id
                    problem.solved_at = datetime.fromtimestamp(submission1.get("creationTimeSeconds", datetime.utcnow().timestamp()))
                    db.commit()
                    recalculate_contest_scores(contest.id, db)
                elif submission2:
                    # Only user2 solved
                    problem.solved_by = user2.id
                    problem.solved_at = datetime.fromtimestamp(submission2.get("creationTimeSeconds", datetime.utcnow().timestamp()))
                    db.commit()
                    recalculate_contest_scores(contest.id, db)
        
        # Check if contest should be completed
        if datetime.utcnow() >= contest.end_time:
            contest.status = ContestStatus.COMPLETED
            db.commit()
            # Update ratings after contest completion
            update_ratings_after_contest(contest.id, db)
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


async def select_contest_problems():
    """Select problems for contests that are less than 1 minute away from start time"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Find contests that are scheduled, less than 1 minute from start, and don't have problems yet
        contests_needing_problems = db.query(Contest).filter(
            Contest.status == ContestStatus.SCHEDULED,
            Contest.start_time - now <= timedelta(minutes=1),
            Contest.start_time > now  # Still haven't started
        ).all()
        
        for contest in contests_needing_problems:
            # Check if problems already exist
            existing_problems = db.query(ContestProblem).filter(
                ContestProblem.contest_id == contest.id
            ).first()
            
            if existing_problems:
                # Problems already selected, skip
                continue
            
            # Get user handles for problem selection
            user1 = db.query(User).filter(User.id == contest.user1_id).first()
            user2 = db.query(User).filter(User.id == contest.user2_id).first()
            
            if not user1 or not user2:
                print(f"Error: Users not found for contest {contest.id}")
                continue
            
            try:
                # Select problems
                problems = await get_unsolved_problems(
                    user1.handle,
                    user2.handle,
                    contest.difficulty
                )
                
                # Create contest problems
                for prob_data in problems:
                    contest_problem = ContestProblem(
                        contest_id=contest.id,
                        problem_index=prob_data["problem_index"],
                        problem_code=prob_data["problem_code"],
                        problem_url=prob_data["problem_url"],
                        points=prob_data["points"],
                        division=prob_data["division"]
                    )
                    db.add(contest_problem)
                
                # Ensure scores exist (they should already exist, but check to be safe)
                score1 = db.query(ContestScore).filter(
                    ContestScore.contest_id == contest.id,
                    ContestScore.user_id == user1.id
                ).first()
                score2 = db.query(ContestScore).filter(
                    ContestScore.contest_id == contest.id,
                    ContestScore.user_id == user2.id
                ).first()
                
                if not score1:
                    score1 = ContestScore(contest_id=contest.id, user_id=user1.id, total_points=0)
                    db.add(score1)
                
                if not score2:
                    score2 = ContestScore(contest_id=contest.id, user_id=user2.id, total_points=0)
                    db.add(score2)
                
                db.commit()
                print(f"Successfully selected {len(problems)} problems for contest {contest.id}")
            except Exception as e:
                db.rollback()
                print(f"Error selecting problems for contest {contest.id}: {e}")
    except Exception as e:
        print(f"Error in select_contest_problems: {e}")
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
    
    # Check for contests that need problems selected (less than 1 minute before start)
    scheduler.add_job(
        select_contest_problems,
        'interval',
        seconds=10,
        id='select_contest_problems'
    )
    
    # Check pending user confirmations every 30 seconds
    from .confirmation_checker import check_pending_confirmations
    scheduler.add_job(
        check_pending_confirmations,
        'interval',
        seconds=30,
        id='check_pending_confirmations'
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
