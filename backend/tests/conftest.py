"""
Pytest configuration and fixtures for tournament tests
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

# Set test environment variables before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")

# Mock migrations before importing main
import app.migrations as migrations_module
original_run_migrations = migrations_module.run_migrations
migrations_module.run_migrations = lambda: None

from app.database import Base, get_db
from app.models import User, Tournament, TournamentSlot, TournamentInvite, TournamentMatch, TournamentRoundSchedule
from app.auth import create_access_token, get_password_hash

# Create test app without migrations and scheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, challenges, contests, tournaments

test_app = FastAPI(title="CP VS API Test", version="1.0.0")
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
test_app.include_router(auth.router)
test_app.include_router(users.router)
test_app.include_router(challenges.router)
test_app.include_router(contests.router)
test_app.include_router(contests.public_router)
test_app.include_router(tournaments.router)

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    from app.dependencies import get_confirmed_user, get_current_user
    
    # Store current user in a list so it can be modified
    current_user_ref = [None]
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    def override_get_current_user(credentials=None, db_session=None):
        user = current_user_ref[0]
        if user is None:
            raise Exception("No test user set - use auth_headers fixture")
        return user
    
    def override_get_confirmed_user(current_user=None):
        user = current_user_ref[0]
        if user is None:
            raise Exception("No test user set - use auth_headers fixture")
        if not user.is_confirmed:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not confirmed"
            )
        return user
    
    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.dependency_overrides[get_confirmed_user] = override_get_confirmed_user
    
    # Make current_user_ref available to fixtures
    client.current_user_ref = current_user_ref
    
    try:
        with TestClient(test_app) as test_client:
            # Attach the ref to the client so fixtures can access it
            test_client.current_user_ref = current_user_ref
            yield test_client
    finally:
        test_app.dependency_overrides.clear()
        current_user_ref[0] = None


@pytest.fixture
def test_user(db):
    """Create a test user"""
    try:
        password_hash = get_password_hash("testpass123")
    except:
        password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    user = User(
        id=uuid.uuid4(),
        handle="testuser",
        password_hash=password_hash,
        rating=1500,
        is_confirmed=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db):
    """Create a second test user"""
    try:
        password_hash = get_password_hash("testpass123")
    except:
        password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    user = User(
        id=uuid.uuid4(),
        handle="testuser2",
        password_hash=password_hash,
        rating=1400,
        is_confirmed=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user3(db):
    """Create a third test user"""
    try:
        password_hash = get_password_hash("testpass123")
    except:
        password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    user = User(
        id=uuid.uuid4(),
        handle="testuser3",
        password_hash=password_hash,
        rating=1300,
        is_confirmed=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    client.current_user_ref[0] = test_user
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(client, test_user2):
    """Get authentication headers for test user 2"""
    client.current_user_ref[0] = test_user2
    token = create_access_token(data={"sub": str(test_user2.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user3(client, test_user3):
    """Get authentication headers for test user 3"""
    client.current_user_ref[0] = test_user3
    token = create_access_token(data={"sub": str(test_user3.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tournament_4_participants(db, test_user):
    """Create a tournament with 4 participants"""
    tournament = Tournament(
        id=uuid.uuid4(),
        creator_id=test_user.id,
        num_participants=4,
        difficulty=2,
        status="pending"
    )
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    
    # Create slots
    for i in range(1, 5):
        slot = TournamentSlot(
            id=uuid.uuid4(),
            tournament_id=tournament.id,
            slot_number=i,
            status="PENDING"
        )
        db.add(slot)
    db.commit()
    
    return tournament


@pytest.fixture
def tournament_8_participants(db, test_user):
    """Create a tournament with 8 participants"""
    tournament = Tournament(
        id=uuid.uuid4(),
        creator_id=test_user.id,
        num_participants=8,
        difficulty=2,
        status="pending"
    )
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    
    # Create slots
    for i in range(1, 9):
        slot = TournamentSlot(
            id=uuid.uuid4(),
            tournament_id=tournament.id,
            slot_number=i,
            status="PENDING"
        )
        db.add(slot)
    db.commit()
    
    return tournament
