# Quick Start Guide

Follow these steps to test the project locally.

## Prerequisites Check

1. **Python 3.11+**: `python --version`
2. **Node.js 18+**: `node --version`
3. **npm**: `npm --version`

**Note**: For local testing, we use **SQLite** (no installation needed!). PostgreSQL is only needed for production/Railway deployment.

## Backend Setup (Terminal 1)

```powershell
# Navigate to backend
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up .env file (if not exists)
python setup_local.py

# .env is already configured to use SQLite (no database setup needed!)
# Database file will be created automatically at: cpvs.db

# Test the setup
python test_setup.py

# Start the backend server
uvicorn app.main:app --reload
```

Backend will run at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## Frontend Setup (Terminal 2)

```powershell
# Navigate to frontend
cd "C:\Users\khaled\Desktop\projects\CP VS\frontend"

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:3000`

## Quick Test

1. Open `http://localhost:3000` in your browser
2. Register a user (e.g., handle: "testuser1", password: "test123")
3. Open incognito window, register another user (e.g., "testuser2")
4. In first window: Create Challenge → Search for "testuser2" → Select difficulty → Create
5. In second window: Dashboard → Accept the challenge
6. View the created contest!

## Troubleshooting

### Backend won't start
- Verify DATABASE_URL in `.env` is set to `sqlite:///./cpvs.db`
- Check if you have write permissions in the backend directory (for SQLite database file)
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't start
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### Database connection errors
- For SQLite: Check file permissions in backend directory
- Database file `cpvs.db` will be created automatically on first run
- If switching to PostgreSQL: Make sure PostgreSQL is running and DATABASE_URL is correct

For detailed testing instructions, see `TESTING.md`
