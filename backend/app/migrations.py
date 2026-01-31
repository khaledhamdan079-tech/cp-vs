"""
Database migration utilities for adding new columns and tables.
"""
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from .database import engine
from .models import (
    Base, RatingHistory, Tournament, TournamentSlot, TournamentInvite,
    TournamentMatch, TournamentRoundSchedule
)
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
        print(f"  [OK] Deleted {count} records from rating_history")
    
    if 'contest_scores' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contest_scores")).scalar()
        conn.execute(text("DELETE FROM contest_scores"))
        print(f"  [OK] Deleted {count} records from contest_scores")
    
    if 'contest_problems' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contest_problems")).scalar()
        conn.execute(text("DELETE FROM contest_problems"))
        print(f"  [OK] Deleted {count} records from contest_problems")
    
    if 'contests' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM contests")).scalar()
        conn.execute(text("DELETE FROM contests"))
        print(f"  [OK] Deleted {count} records from contests")
    
    if 'challenges' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM challenges")).scalar()
        conn.execute(text("DELETE FROM challenges"))
        print(f"  [OK] Deleted {count} records from challenges")
    
    if 'users' in tables:
        count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        conn.execute(text("DELETE FROM users"))
        print(f"  [OK] Deleted {count} records from users")
    
    print("[OK] Database cleared successfully\n")


def run_migrations():
    """Run database migrations to add new columns and tables"""
    try:
        # Test database connection first
        with engine.connect() as test_conn:
            test_conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"[WARNING] Database connection test failed: {e}")
        print("Skipping migrations - will retry on first request")
        raise
    
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
                    print("[OK] Added 'rating' column with default value 1000")
                else:
                    print("[OK] 'rating' column already exists")
                
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
                    print("[OK] Added 'is_confirmed' column with default value FALSE")
                else:
                    print("[OK] 'is_confirmed' column already exists")
                
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
                    print("[OK] Added 'confirmation_deadline' column")
                else:
                    print("[OK] 'confirmation_deadline' column already exists")
                
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
                    print("[OK] Existing users marked as confirmed")
            else:
                print("[WARNING] 'users' table does not exist yet - will be created by create_all()")
            
            # Create rating_history table if it doesn't exist
            if 'rating_history' not in inspector.get_table_names():
                print("Creating 'rating_history' table...")
                Base.metadata.create_all(bind=engine, tables=[RatingHistory.__table__])
                print("[OK] Created 'rating_history' table")
            else:
                print("[OK] 'rating_history' table already exists")
            
            # Add tournament_match_id to contests table if it doesn't exist
            if 'contests' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('contests')]
                if 'tournament_match_id' not in columns:
                    print("Adding 'tournament_match_id' column to contests table...")
                    if engine.dialect.name == 'postgresql':
                        conn.execute(text("""
                            DO $$ 
                            BEGIN
                                IF NOT EXISTS (
                                    SELECT 1 FROM information_schema.columns 
                                    WHERE table_name = 'contests' AND column_name = 'tournament_match_id'
                                ) THEN
                                    ALTER TABLE contests ADD COLUMN tournament_match_id VARCHAR(36);
                                    -- Make challenge_id nullable if it's not already
                                    IF EXISTS (
                                        SELECT 1 FROM information_schema.columns 
                                        WHERE table_name = 'contests' AND column_name = 'challenge_id' AND is_nullable = 'NO'
                                    ) THEN
                                        ALTER TABLE contests ALTER COLUMN challenge_id DROP NOT NULL;
                                    END IF;
                                    -- Drop unique constraint on challenge_id if it exists
                                    IF EXISTS (
                                        SELECT 1 FROM information_schema.table_constraints 
                                        WHERE table_name = 'contests' AND constraint_name = 'contests_challenge_id_key'
                                    ) THEN
                                        ALTER TABLE contests DROP CONSTRAINT contests_challenge_id_key;
                                    END IF;
                                    CREATE INDEX IF NOT EXISTS ix_contests_tournament_match_id ON contests(tournament_match_id);
                                END IF;
                            END $$;
                        """))
                    else:
                        # SQLite - just add the column (SQLite allows adding nullable columns)
                        conn.execute(text("ALTER TABLE contests ADD COLUMN tournament_match_id VARCHAR(36)"))
                        # Try to make challenge_id nullable (SQLite doesn't support ALTER COLUMN, but we can work around it)
                        # For now, just add the column - the model will handle nullable challenge_id
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_contests_tournament_match_id ON contests(tournament_match_id)"))
                    print("[OK] Added 'tournament_match_id' column to contests table")
                else:
                    print("[OK] 'tournament_match_id' column already exists in contests table")
            
            # Create tournament tables if they don't exist
            tournament_tables = [
                ('tournaments', Tournament),
                ('tournament_slots', TournamentSlot),
                ('tournament_invites', TournamentInvite),
                ('tournament_round_schedules', TournamentRoundSchedule),
                ('tournament_matches', TournamentMatch),
            ]
            
            for table_name, model_class in tournament_tables:
                if table_name not in inspector.get_table_names():
                    print(f"Creating '{table_name}' table...")
                    Base.metadata.create_all(bind=engine, tables=[model_class.__table__])
                    print(f"[OK] Created '{table_name}' table")
                else:
                    print(f"[OK] '{table_name}' table already exists")
        
        # Ensure all other tables exist (outside transaction for create_all)
        print("Ensuring all tables exist...")
        Base.metadata.create_all(bind=engine)
        print("[OK] All tables verified")
        
    except Exception as e:
        print(f"[WARNING] Migration error: {e}")
        print("Attempting to continue - tables will be created by create_all()")
        # Fallback: just create all tables
        Base.metadata.create_all(bind=engine)
