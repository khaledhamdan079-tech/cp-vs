from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import auth, users, challenges, contests
from .submission_checker import start_scheduler

# Create tables
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
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]

# Add Railway frontend URL from environment variable if set
import os
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(challenges.router)
app.include_router(contests.router)


@app.get("/")
async def root():
    return {"message": "CP VS API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
