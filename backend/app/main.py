from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os
from sqlalchemy import text

# Import database components - these might fail, so handle gracefully
try:
    from .database import engine, Base
    database_available = True
except Exception as e:
    print(f"[ERROR] Failed to initialize database: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    database_available = False
    engine = None
    Base = None

# Import routers and other components
try:
    from .routers import auth, users, challenges, contests, tournaments
    from .submission_checker import start_scheduler, scheduler
    from .migrations import run_migrations
except Exception as e:
    print(f"[ERROR] Failed to import modules: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    # Set defaults to prevent crashes
    scheduler = None
    start_scheduler = lambda: None
    run_migrations = lambda: None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup - run migrations and initialize database
    if database_available and engine and Base:
        try:
            print("[INFO] Running database migrations...", file=sys.stderr)
            run_migrations()
        except Exception as e:
            error_msg = f"[WARNING] Migration error (non-fatal): {e}"
            print(error_msg, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        # Create tables (creates new tables if they don't exist)
        try:
            print("[INFO] Ensuring all tables exist...", file=sys.stderr)
            Base.metadata.create_all(bind=engine)
            print("[INFO] Database initialization complete", file=sys.stderr)
        except Exception as e:
            error_msg = f"[WARNING] Table creation error: {e}"
            print(error_msg, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    # Start scheduler
    try:
        if scheduler:
            start_scheduler()
    except Exception as e:
        error_msg = f"[WARNING] Scheduler startup error (non-fatal): {e}"
        print(error_msg, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Continue even if scheduler fails to start
    
    yield
    # Shutdown (if needed)


app = FastAPI(title="CP VS API", version="1.0.0", lifespan=lifespan)

# CORS middleware
# In production, update allow_origins with your frontend URL
import os

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]

# Add Railway frontend URL from environment variable if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    # Remove trailing slash if present
    frontend_url = frontend_url.rstrip('/')
    allowed_origins.append(frontend_url)
    # Also add with trailing slash (some browsers send it)
    allowed_origins.append(frontend_url + '/')

# Log allowed origins for debugging (remove in production if needed)
print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers (only if they imported successfully)
try:
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(challenges.router)
    app.include_router(contests.router)
    app.include_router(contests.public_router)
    app.include_router(tournaments.router)
except NameError:
    print("[ERROR] Failed to include routers - some modules may not have loaded", file=sys.stderr)


@app.get("/")
async def root():
    return {"message": "CP VS API"}


@app.get("/health")
async def health():
    """Health check endpoint for Railway and load balancers"""
    if not database_available or not engine:
        return {
            "status": "unhealthy",
            "database": "not_available",
            "message": "Database not initialized"
        }
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "scheduler": "running" if scheduler and scheduler.running else "stopped"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }
