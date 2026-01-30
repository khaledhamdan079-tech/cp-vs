# Testing Guide

This guide will help you test the CP VS project locally.

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** installed and running
3. **Node.js 18+** and npm installed
4. **Codeforces API** accessible (no API key needed, but internet required)

## Step 1: Set Up Backend

### 1.1 Navigate to backend directory
```bash
cd backend
```

### 1.2 Create virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 1.3 Install dependencies
```bash
pip install -r requirements.txt
```

### 1.4 Set up environment variables
```bash
# Run the setup script
python setup_local.py

# Or manually create .env file from .env.example
# Update DATABASE_URL with your PostgreSQL credentials
```

Example `.env` file:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cpvs_db
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CODEFORCES_API_URL=https://codeforces.com/api
```

### 1.5 Create database
```bash
# Using psql
createdb cpvs_db

# Or using PostgreSQL command line
psql -U postgres
CREATE DATABASE cpvs_db;
\q
```

### 1.6 Test the setup
```bash
python test_setup.py
```

This will verify:
- All imports work
- Configuration is correct
- Database connection works

### 1.7 Start the backend server
```bash
uvicorn app.main:app --reload
```

The backend should be running at `http://localhost:8000`

You can verify it's working by visiting:
- `http://localhost:8000` - Should show `{"message": "CP VS API"}`
- `http://localhost:8000/docs` - FastAPI automatic API documentation
- `http://localhost:8000/health` - Health check endpoint

## Step 2: Set Up Frontend

### 2.1 Navigate to frontend directory (in a new terminal)
```bash
cd frontend
```

### 2.2 Install dependencies
```bash
npm install
```

### 2.3 Start the development server
```bash
npm run dev
```

The frontend should be running at `http://localhost:3000`

## Step 3: Test the Application

### 3.1 Register a User

1. Open `http://localhost:3000` in your browser
2. Click "Register"
3. Enter:
   - **Handle**: Your Codeforces handle (or any test handle like "testuser1")
   - **Password**: Any password (min 6 characters)
4. Click "Register"

You should be automatically logged in and redirected to the dashboard.

### 3.2 Register a Second User

1. Open an incognito/private window or use a different browser
2. Register another user with a different handle (e.g., "testuser2")
3. Keep both windows open for testing challenges

### 3.3 Create a Challenge

1. In the first user's window, click "Create Challenge"
2. Search for the second user's handle
3. Select difficulty (1-4)
4. Set a start time (at least 1 hour from now for testing)
5. Click "Create Challenge"

### 3.4 Accept the Challenge

1. In the second user's window, refresh the dashboard
2. You should see a pending challenge
3. Click "Accept"

This will create a contest with 6 problems.

### 3.5 View the Contest

1. After accepting, go to the "Contests" tab
2. Click "View Contest"
3. You should see:
   - Contest details (users, difficulty, times)
   - Problems (revealed when contest starts)
   - Leaderboard

### 3.6 Test API Endpoints (Optional)

You can test the API directly using the FastAPI docs at `http://localhost:8000/docs`:

1. **Register**: POST `/api/auth/register`
   ```json
   {
     "handle": "testuser",
     "password": "testpass123"
   }
   ```

2. **Login**: POST `/api/auth/login`
   ```json
   {
     "handle": "testuser",
     "password": "testpass123"
   }
   ```
   Copy the `access_token` from the response.

3. **Get Current User**: GET `/api/auth/me`
   - Click "Authorize" button
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize" then "Try it out"

4. **Search Users**: GET `/api/users/search?q=test`
   - Requires authentication

5. **Create Challenge**: POST `/api/challenges/`
   ```json
   {
     "challenged_user_id": "<user_id_from_search>",
     "difficulty": 2,
     "suggested_start_time": "2024-01-31T10:00:00"
   }
   ```

## Troubleshooting

### Backend Issues

**Database Connection Error**
- Make sure PostgreSQL is running: `pg_isready` or check services
- Verify DATABASE_URL in .env is correct
- Check if database exists: `psql -l | grep cpvs_db`

**Import Errors**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Port Already in Use**
- Change port: `uvicorn app.main:app --reload --port 8001`
- Or kill the process using port 8000

### Frontend Issues

**Cannot Connect to Backend**
- Make sure backend is running on port 8000
- Check `vite.config.js` proxy settings
- Verify CORS is enabled in backend

**Build Errors**
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear cache: `npm cache clean --force`

**API Errors**
- Check browser console for errors
- Verify JWT token is being stored in localStorage
- Check network tab for API request/response

### Codeforces API Issues

**Problem Selection Fails**
- Codeforces API might be rate-limited (wait a few seconds)
- Check internet connection
- Verify Codeforces API is accessible: `curl https://codeforces.com/api/problemset.problems`

**Submission Checking Not Working**
- Background scheduler runs every 30 seconds
- Make sure contest status is "active"
- Check server logs for errors

## Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can register a new user
- [ ] Can login with registered user
- [ ] Can search for users
- [ ] Can create a challenge
- [ ] Can accept a challenge
- [ ] Contest is created after accepting
- [ ] Problems are selected (check database or API response)
- [ ] Contest view shows problems when started
- [ ] Leaderboard updates (when submissions are detected)

## Next Steps

Once local testing is successful:
1. Test with real Codeforces handles
2. Test submission tracking (requires actual Codeforces submissions)
3. Deploy to Railway following the README instructions
