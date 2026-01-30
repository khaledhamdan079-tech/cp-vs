"""
Script to delete all contests from the database.
Run this to clean up and test with new problem selection logic.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import Contest, ContestProblem, ContestScore

def delete_all_contests():
    """Delete all contests and related data"""
    db = SessionLocal()
    try:
        # Count before deletion
        contest_count = db.query(Contest).count()
        
        print("=" * 80)
        print("Deleting Contests")
        print("=" * 80)
        print(f"Found {contest_count} contest(s)")
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
    delete_all_contests()
