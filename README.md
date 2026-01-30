# CP VS - Codeforces Contest Challenge Platform

A full-stack web application where users can challenge each other to Codeforces contests. The system creates contests with 6 problems from appropriate divisions, tracks first-solver points, and determines winners.

## Features

- **User Registration & Authentication**: Register with Codeforces handle and password, login with JWT tokens
- **Challenge System**: Challenge other users with suggested start time and difficulty level
- **Contest Creation**: Automatically creates contests with 6 problems (A-F) when challenge is accepted
- **Problem Selection**: Selects problems from divisions matching difficulty that neither user has solved
- **Real-time Tracking**: Monitors Codeforces submissions every 30 seconds during active contests
- **First-Solver Points**: Awards points to the first user who solves each problem (100-600 points for A-F)
- **Leaderboard**: Live leaderboard showing current scores during contests

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **PostgreSQL**: Database
- **SQLAlchemy**: ORM
- **JWT**: Authentication
- **APScheduler**: Background task scheduling
- **Codeforces API**: Problem fetching and submission tracking

### Frontend
- **React**: UI library
- **Vite**: Build tool
- **React Router**: Routing
- **Axios**: HTTP client

## Project Structure

```
CP VS/
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── auth.py         # JWT utilities
│   │   ├── codeforces_api.py
│   │   ├── problem_selector.py
│   │   ├── submission_checker.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── contexts/       # Auth context
    │   ├── api/           # API client
    │   └── App.jsx
    └── package.json
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Update `.env` with your database URL and JWT secret:
```
DATABASE_URL=postgresql://user:password@localhost:5432/cpvs_db
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CODEFORCES_API_URL=https://codeforces.com/api
```

6. Create the database:
```bash
# Using PostgreSQL
createdb cpvs_db
```

7. Run migrations (tables are created automatically on first run):
```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional, defaults to localhost:8000):
```
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Deployment to Railway

### Backend Deployment

1. Create a new Railway project
2. Connect your GitHub repository
3. Set the root directory to `backend`
4. Add environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string (Railway provides this)
   - `JWT_SECRET_KEY`: A secure random string
   - `JWT_ALGORITHM`: HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 1440
   - `CODEFORCES_API_URL`: https://codeforces.com/api
5. Railway will automatically detect the Python project and install dependencies
6. The Procfile will be used to start the server

### Frontend Deployment

1. Create a new Railway project (or use a static hosting service like Vercel/Netlify)
2. Set the root directory to `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Set environment variable:
   - `VITE_API_BASE_URL`: Your backend Railway URL

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/me` - Get current user profile
- `GET /api/users/{handle}` - Get user by handle
- `GET /api/users/search?q={query}` - Search users

### Challenges
- `POST /api/challenges/` - Create challenge
- `GET /api/challenges/` - List user's challenges
- `POST /api/challenges/{id}/accept` - Accept challenge
- `POST /api/challenges/{id}/reject` - Reject challenge

### Contests
- `GET /api/contests/` - List user's contests
- `GET /api/contests/{id}` - Get contest details
- `GET /api/contests/{id}/problems` - Get contest problems

## Notes

- Codeforces API rate limits: ~5 requests per second
- Contest duration defaults to 2 hours
- Problems are selected from divisions matching difficulty (1-4 maps to Div 4-1)
- Only problems that neither user has solved are selected
- First solver gets points; second solver gets 0 for that problem
- Submissions are checked every 30 seconds during active contests

## License

MIT
