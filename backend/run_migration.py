"""
Standalone migration script to add rating column to existing database.
Run this if automatic migration doesn't work.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.migrations import run_migrations

if __name__ == "__main__":
    print("=" * 60)
    print("Running Database Migrations")
    print("=" * 60)
    try:
        run_migrations()
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
