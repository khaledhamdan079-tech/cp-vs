"""
Script to delete all contests from the database.
Use this to clean up and test with new problem selection logic.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Contest, ContestProblem, ContestScore, Challenge

def delete_all_contests():
    """Delete all contests and related data"""
    db = SessionLocal()
    try:
        # Count before deletion
        contest_count = db.query(Contest).count()
        challenge_count = db.query(Challenge).count()
        
        print("=" * 80)
        print("Deleting Contests")
        print("=" * 80)
        print(f"Found {contest_count} contest(s)")
        print(f"Found {challenge_count} challenge(s)")
        print()
        
        if contest_count == 0:
            print("No contests to delete.")
            return
        
        # Delete contest scores
        scores_deleted = db.query(ContestScore).delete()
        print(f"Deleted {scores_deleted} contest score(s)")
        
        # Delete contest problems
        problems_deleted = db.query(ContestProblem).delete()
        print(f"Deleted {problems_deleted} contest problem(s)")
        
        # Delete contests
        contests_deleted = db.query(Contest).delete()
        print(f"Deleted {contests_deleted} contest(s)")
        
        # Optionally delete challenges too
        response = input("\nDo you want to delete all challenges as well? (y/n): ")
        if response.lower() == 'y':
            challenges_deleted = db.query(Challenge).delete()
            print(f"Deleted {challenges_deleted} challenge(s)")
        
        db.commit()
        
        print()
        print("=" * 80)
        print("Deletion completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CP VS Contest Deletion Script")
    print("=" * 80 + "\n")
    print("WARNING: This will delete all contests and related data!")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() == 'yes':
        delete_all_contests()
    else:
        print("Deletion cancelled.")
