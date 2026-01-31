from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import auth, users, challenges, contests, tournaments
from .submission_checker import start_scheduler
from .migrations import run_migrations

# Run migrations first (adds new columns to existing tables)
run_migrations()

# Create tables (creates new tables if they don't exist)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    start_scheduler()
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

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(challenges.router)
app.include_router(contests.router)
app.include_router(contests.public_router)
app.include_router(tournaments.router)


@app.get("/")
async def root():
    return {"message": "CP VS API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
