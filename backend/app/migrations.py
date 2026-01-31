"""
Database migration utilities for adding new columns and tables.
"""
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from .database import engine
from .models import Base, RatingHistory
import os


def clear_all_data(conn):
    """Clear all data from all tables"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        return
    
    print("\n" + "!" * 60)
    print("CLEARING ALL DATA FROM DATABASE")
    print("!" * 60)
    
    # Delete in reverse order of dependencies
    if 'rating_history' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM rating_history")).scalar()
        conn.execute(text("DELETE FROM rating_history"))
        print(f"  ✓ Deleted {count} records from rating_history")
    
    if 'contest_scores' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contest_scores")).scalar()
        conn.execute(text("DELETE FROM contest_scores"))
        print(f"  ✓ Deleted {count} records from contest_scores")
    
    if 'contest_problems' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contest_problems")).scalar()
        conn.execute(text("DELETE FROM contest_problems"))
        print(f"  ✓ Deleted {count} records from contest_problems")
    
    if 'contests' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contests")).scalar()
        conn.execute(text("DELETE FROM contests"))
        print(f"  ✓ Deleted {count} records from contests")
    
    if 'challenges' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM challenges")).scalar()
        conn.execute(text("DELETE FROM challenges"))
        print(f"  ✓ Deleted {count} records from challenges")
    
    if 'users' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        conn.execute(text("DELETE FROM users"))
        print(f"  ✓ Deleted {count} records from users")
    
    print("✓ Database cleared successfully\n")


def run_migrations():
    """Run database migrations to add new columns and tables"""
    try:
        with engine.begin() as conn:  # Use begin() for transaction management
            inspector = inspect(engine)
            
            # Check if we should clear all data (set CLEAR_DB=true environment variable)
            # WARNING: This will delete ALL data! Use with caution.
            should_clear = os.getenv('CLEAR_DB', 'false').lower() in ('true', '1', 'yes')
            if should_clear:
                clear_all_data(conn)
            
            # Check if users table exists and add missing columns
            if 'users' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('users')]
                
                # Add rating column if it doesn't exist
                if 'rating' not in columns:
                    print("Adding 'rating' column to users table...")
                    if engine.dialect.name == 'postgresql':
                        conn.execute(text("""
                            DO $$ 
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 FROM information_schema.columns 
                                    WHERE table_name = 'users' AND column_name = 'rating'
                                ) THEN
                                    ALTER TABLE users ADD COLUMN rating INTEGER NOT NULL DEFAULT 1000;
                                END IF;
                            END $$;
                        """))
                    else:
                        # SQLite
                        conn.execute(text("ALTER TABLE users ADD COLUMN rating INTEGER NOT NULL DEFAULT 1000"))
                    print("✓ Added 'rating' column with default value 1000")
                else:
                    print("✓ 'rating' column already exists")
                
                # Add is_confirmed column if it doesn't exist
                if 'is_confirmed' not in columns:
                    print("Adding 'is_confirmed' column to users table...")
                    if engine.dialect.name == 'postgresql':
                        conn.execute(text("""
                            DO $$ 
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 FROM information_schema.columns 
                                    WHERE table_name = 'users' AND column_name = 'is_confirmed'
                                ) THEN
                                    ALTER TABLE users ADD COLUMN is_confirmed BOOLEAN NOT NULL DEFAULT FALSE;
                                    CREATE INDEX IF NOT EXISTS ix_users_is_confirmed ON users(is_confirmed);
                                END IF;
                            END $$;
                        """))
                    else:
                        # SQLite
                        conn.execute(text("ALTER TABLE users ADD COLUMN is_confirmed BOOLEAN NOT NULL DEFAULT 0"))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_is_confirmed ON users(is_confirmed)"))
                    print("✓ Added 'is_confirmed' column with default value FALSE")
                else:
                    print("✓ 'is_confirmed' column already exists")
                
                # Add confirmation_deadline column if it doesn't exist
                if 'confirmation_deadline' not in columns:
                    print("Adding 'confirmation_deadline' column to users table...")
                    if engine.dialect.name == 'postgresql':
                        conn.execute(text("""
                            DO $$ 
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 FROM information_schema.columns 
                                    WHERE table_name = 'users' AND column_name = 'confirmation_deadline'
                                ) THEN
                                    ALTER TABLE users ADD COLUMN confirmation_deadline TIMESTAMP;
                                END IF;
                            END $$;
                        """))
                    else:
                        # SQLite
                        conn.execute(text("ALTER TABLE users ADD COLUMN confirmation_deadline DATETIME"))
                    print("✓ Added 'confirmation_deadline' column")
                else:
                    print("✓ 'confirmation_deadline' column already exists")
                
                # Set existing users as confirmed (they registered before this feature)
                if 'is_confirmed' in columns:
                    print("Setting existing users as confirmed...")
                    if engine.dialect.name == 'postgresql':
                        conn.execute(text("""
                            UPDATE users 
                            SET is_confirmed = TRUE 
                            WHERE is_confirmed = FALSE AND confirmation_deadline IS NULL
                        """))
                    else:
                        # SQLite
                        conn.execute(text("""
                            UPDATE users 
                            SET is_confirmed = 1 
                            WHERE is_confirmed = 0 AND confirmation_deadline IS NULL
                        """))
                    print("✓ Existing users marked as confirmed")
            else:
                print("⚠ 'users' table does not exist yet - will be created by create_all()")
            
            # Create rating_history table if it doesn't exist
            if 'rating_history' not in inspector.get_table_names():
                print("Creating 'rating_history' table...")
                Base.metadata.create_all(bind=engine, tables=[RatingHistory.__table__])
                print("✓ Created 'rating_history' table")
            else:
                print("✓ 'rating_history' table already exists")
        
        # Ensure all other tables exist (outside transaction for create_all)
        print("Ensuring all tables exist...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables verified")
        
    except Exception as e:
        print(f"⚠ Migration error: {e}")
        print("Attempting to continue - tables will be created by create_all()")
        # Fallback: just create all tables
        Base.metadata.create_all(bind=engine)
