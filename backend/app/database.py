from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Use SQLite for local development if database_url contains sqlite
# Otherwise use the provided database_url (PostgreSQL for production)
try:
    if settings.database_url.startswith("sqlite"):
        # SQLite needs check_same_thread=False for FastAPI
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True  # Verify connections before using
        )
    else:
        # PostgreSQL - add connection pooling and retry logic
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=300,    # Recycle connections after 5 minutes
            connect_args={
                "connect_timeout": 10  # 10 second connection timeout
            }
        )
except Exception as e:
    print(f"⚠️  Database engine creation error: {e}")
    import traceback
    traceback.print_exc()
    # Re-raise to fail fast if database is completely unavailable
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
