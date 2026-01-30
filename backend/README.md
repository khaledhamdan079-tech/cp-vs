# CP VS Backend

FastAPI backend for the Codeforces Contest Challenge Platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy `.env.example` to `.env`):
```
DATABASE_URL=postgresql://user:password@localhost:5432/cpvs_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CODEFORCES_API_URL=https://codeforces.com/api
```

3. Create database tables (automatically created on first run)

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## Railway Deployment

Railway will automatically:
- Detect Python project
- Install dependencies from `requirements.txt`
- Use `Procfile` to start the server
- Set `PORT` environment variable

Make sure to set all required environment variables in Railway dashboard.
