"""
Script to clear all data from the database.
WARNING: This will delete ALL data from ALL tables!
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from app.models import (
    User, Challenge, Contest, ContestProblem, ContestScore, RatingHistory
)

def clear_database():
    """Delete all data from all tables"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CLEARING DATABASE - ALL DATA WILL BE DELETED")
        print("=" * 60)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("No tables found in database.")
            return
        
        print(f"\nFound {len(tables)} tables: {', '.join(tables)}")
        print("\nDeleting data from tables (respecting foreign key constraints)...")
        
        # Delete in reverse order of dependencies
        # 1. RatingHistory (depends on users, contests)
        if 'rating_history' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM rating_history")).scalar()
            db.execute(text("DELETE FROM rating_history"))
            print(f"  ✓ Deleted {count} records from rating_history")
        
        # 2. ContestScore (depends on contests, users)
        if 'contest_scores' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM contest_scores")).scalar()
            db.execute(text("DELETE FROM contest_scores"))
            print(f"  ✓ Deleted {count} records from contest_scores")
        
        # 3. ContestProblem (depends on contests, users)
        if 'contest_problems' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM contest_problems")).scalar()
            db.execute(text("DELETE FROM contest_problems"))
            print(f"  ✓ Deleted {count} records from contest_problems")
        
        # 4. Contest (depends on challenges, users)
        if 'contests' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM contests")).scalar()
            db.execute(text("DELETE FROM contests"))
            print(f"  ✓ Deleted {count} records from contests")
        
        # 5. Challenge (depends on users)
        if 'challenges' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM challenges")).scalar()
            db.execute(text("DELETE FROM challenges"))
            print(f"  ✓ Deleted {count} records from challenges")
        
        # 6. User (no dependencies)
        if 'users' in tables:
            count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            db.execute(text("DELETE FROM users"))
            print(f"  ✓ Deleted {count} records from users")
        
        # Commit all deletions
        db.commit()
        
        print("\n" + "=" * 60)
        print("Database cleared successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Failed to clear database: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    # Safety confirmation
    print("\n" + "!" * 60)
    print("WARNING: This will DELETE ALL DATA from the database!")
    print("!" * 60)
    response = input("\nType 'DELETE ALL' to confirm: ")
    
    if response == "DELETE ALL":
        clear_database()
    else:
        print("\nOperation cancelled. Database was not modified.")
        sys.exit(0)
