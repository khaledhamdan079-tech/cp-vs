"""
Database migration utilities for adding new columns and tables.
"""
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from .database import engine
from .models import Base, RatingHistory


def run_migrations():
    """Run database migrations to add new columns and tables"""
    try:
        with engine.begin() as conn:  # Use begin() for transaction management
            inspector = inspect(engine)
            
            # Check if users table exists and if rating column exists
            if 'users' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('users')]
                
                # Add rating column if it doesn't exist
                if 'rating' not in columns:
                    print("Adding 'rating' column to users table...")
                    # Use DO block for PostgreSQL to check before adding
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
                    print("✓ Added 'rating' column with default value 1000")
                else:
                    print("✓ 'rating' column already exists")
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
