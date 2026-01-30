"""
Script to check contest data in the database.
Run this to see what contests exist and their details.
"""
import sys
import os
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Contest, ContestProblem, ContestScore, User, Challenge

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"

def check_contests():
    """Display all contests and their details"""
    db = SessionLocal()
    try:
        contests = db.query(Contest).order_by(Contest.created_at.desc()).all()
        
        if not contests:
            print("No contests found in the database.")
            return
        
        print("=" * 80)
        print(f"Found {len(contests)} contest(s)")
        print("=" * 80)
        print()
        
        for i, contest in enumerate(contests, 1):
            user1 = db.query(User).filter(User.id == contest.user1_id).first()
            user2 = db.query(User).filter(User.id == contest.user2_id).first()
            
            print(f"Contest #{i}")
            print("-" * 80)
            print(f"ID: {contest.id}")
            print(f"Users: {user1.handle if user1 else 'N/A'} vs {user2.handle if user2 else 'N/A'}")
            print(f"Difficulty: {contest.difficulty}")
            print(f"Status: {contest.status.value}")
            print(f"Start Time: {format_datetime(contest.start_time)}")
            print(f"End Time: {format_datetime(contest.end_time)}")
            print(f"Created: {format_datetime(contest.created_at)}")
            
            # Get problems
            problems = db.query(ContestProblem).filter(
                ContestProblem.contest_id == contest.id
            ).order_by(ContestProblem.problem_index).all()
            
            print(f"\nProblems ({len(problems)}):")
            if problems:
                for prob in problems:
                    solver = None
                    if prob.solved_by:
                        solver = db.query(User).filter(User.id == prob.solved_by).first()
                    print(f"  {prob.problem_index}: {prob.problem_code} - {prob.points} pts")
                    print(f"    URL: {prob.problem_url}")
                    if solver:
                        print(f"    Solved by: {solver.handle} at {format_datetime(prob.solved_at)}")
                    else:
                        print(f"    Status: Not solved yet")
            else:
                print("  No problems assigned yet")
            
            # Get scores
            scores = db.query(ContestScore).filter(
                ContestScore.contest_id == contest.id
            ).all()
            
            print(f"\nScores:")
            for score in scores:
                user = db.query(User).filter(User.id == score.user_id).first()
                print(f"  {user.handle if user else 'N/A'}: {score.total_points} points")
            
            # Get challenge info
            challenge = db.query(Challenge).filter(Challenge.id == contest.challenge_id).first()
            if challenge:
                print(f"\nChallenge Info:")
                challenger = db.query(User).filter(User.id == challenge.challenger_id).first()
                challenged = db.query(User).filter(User.id == challenge.challenged_id).first()
                print(f"  Challenger: {challenger.handle if challenger else 'N/A'}")
                print(f"  Challenged: {challenged.handle if challenged else 'N/A'}")
                print(f"  Challenge Status: {challenge.status.value}")
            
            print()
            print("=" * 80)
            print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_users():
    """Display all users"""
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        print("=" * 80)
        print(f"Users in database: {len(users)}")
        print("=" * 80)
        for user in users:
            print(f"  {user.handle} (ID: {user.id}) - Created: {format_datetime(user.created_at)}")
        print()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CP VS Database Checker")
    print("=" * 80 + "\n")
    
    print("USERS:")
    check_users()
    
    print("\nCONTESTS:")
    check_contests()
    
    print("\nDone!")
