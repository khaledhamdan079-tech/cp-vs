# Railway Deployment Guide

This guide will walk you through deploying both the backend and frontend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Account**: Your code should be in a GitHub repository
3. **PostgreSQL Database**: Railway provides PostgreSQL (or use external service)

## Step 1: Prepare Your Repository

### 1.1 Create Railway Configuration Files

Make sure you have:
- `backend/Procfile` (already exists)
- `backend/runtime.txt` (already exists)
- `.gitignore` files (already exist)

### 1.2 Update .env.example

Ensure your `.env.example` has all required variables:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CODEFORCES_API_URL=https://codeforces.com/api
```

## Step 2: Deploy Backend to Railway

### 2.1 Create New Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your repository

### 2.2 Configure Backend Service

1. Railway will detect your project
2. Click "Add Service" → "GitHub Repo"
3. Select your repository again
4. **After the service is created**, click on the service tile
5. Go to **Settings** tab
6. Scroll down to find **"Source"** section
7. Set **Root Directory** to: `backend`
8. In **"Deploy"** section, set **Start Command** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
9. Build Command can be left empty (Railway auto-detects Python)

### 2.3 ⚠️ IMPORTANT: Add PostgreSQL Database FIRST

**You MUST add PostgreSQL before setting environment variables, otherwise the backend will fail to start!**

1. In your Railway project dashboard, click **"New"** button (top right)
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a PostgreSQL database service
4. **DATABASE_URL is automatically set** - you don't need to copy it manually
5. Railway automatically shares `DATABASE_URL` with all services in the project

**Why this is required:**
- The backend requires `DATABASE_URL` to connect to the database
- Without it, you'll see: `ValidationError: database_url Field required`
- Railway sets `DATABASE_URL` automatically when you add PostgreSQL

### 2.4 Set Environment Variables

Go to your backend service → "Variables" tab and add:

```
JWT_SECRET_KEY=<generate-a-strong-random-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CODEFORCES_API_URL=https://codeforces.com/api
```

**Note**: `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

**Generate JWT Secret Key**:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

Or use an online generator: https://randomkeygen.com/

### 2.5 Deploy Backend

1. Railway will automatically detect changes and deploy
2. Check the "Deployments" tab to see build logs
3. Once deployed, go to "Settings" → "Generate Domain" to get your backend URL
4. Your backend will be available at: `https://your-service-name.up.railway.app`

### 2.6 Verify Backend Deployment

Visit:
- `https://your-backend-url.up.railway.app/` - Should return `{"message": "CP VS API"}`
- `https://your-backend-url.up.railway.app/docs` - FastAPI documentation
- `https://your-backend-url.up.railway.app/health` - Health check

## Step 3: Deploy Frontend to Railway

### 3.1 Create Frontend Service

1. In the same Railway project, click "New" → "GitHub Repo"
2. Select your repository again
3. **After the service is created**, click on the frontend service tile
4. Go to **Settings** tab
5. Scroll down to find **"Source"** section
6. Set **Root Directory** to: `frontend`
7. In **"Build"** section, set **Build Command** to: `npm install && npm run build`
8. In **"Deploy"** section, set **Start Command** to: `npx serve dist -s -l $PORT`

### 3.2 Configure Frontend Environment Variables

Go to frontend service → "Variables" tab:

```
VITE_API_BASE_URL=https://your-backend-url.up.railway.app
```

**Important**: Replace `your-backend-url` with your actual backend Railway URL.

### 3.3 Alternative: Use Static File Serving

If `npm run preview` doesn't work, you can use a static file server:

1. Install `serve` package (add to `package.json`):
```json
{
  "scripts": {
    "preview": "serve -s dist -l $PORT"
  },
  "dependencies": {
    "serve": "^14.2.1"
  }
}
```

Or use Railway's static file serving:
- Set **Start Command** to: `npx serve dist -s -l $PORT`

### 3.4 Deploy Frontend

1. Railway will build and deploy automatically
2. Generate a domain in frontend service settings
3. Your frontend will be at: `https://your-frontend-url.up.railway.app`

## Step 4: Update CORS Settings

### 4.1 Update Backend CORS

Once you have your frontend URL, update backend CORS:

In `backend/app/main.py`, update:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.up.railway.app",
        "http://localhost:3000"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to trigger redeployment.

## Step 5: Database Migration

### 5.1 Run Migrations

Railway will automatically create tables on first startup (because of `Base.metadata.create_all(bind=engine)` in `main.py`).

If you need to run migrations manually:
1. Go to backend service → "Deployments"
2. Click on a deployment → "View Logs"
3. Check that tables were created successfully

## Step 6: Testing Deployment

1. **Test Backend**:
   - Visit `https://your-backend-url.up.railway.app/docs`
   - Try registering a user via the API docs
   - Verify database connection works

2. **Test Frontend**:
   - Visit `https://your-frontend-url.up.railway.app`
   - Register a new user
   - Create a challenge
   - Verify everything works

## Troubleshooting

### Backend Issues

**Build Fails**:
- Check build logs in Railway
- Ensure `requirements.txt` is in the `backend/` directory
- Verify Python version in `runtime.txt` is supported

**Database Connection Error**:
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure database exists

**Port Error**:
- Railway sets `$PORT` environment variable automatically
- Make sure your start command uses `$PORT`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Issues

**Build Fails**:
- Check Node.js version (Railway uses Node 18+ by default)
- Verify all dependencies in `package.json`
- Check build logs for specific errors

**API Connection Error**:
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS settings in backend
- Ensure backend URL doesn't have trailing slash

**404 Errors**:
- For React Router, you may need to configure Railway to serve `index.html` for all routes
- Add `_redirects` file or configure static file serving

## Railway-Specific Configuration

### Custom Domain (Optional)

1. Go to service → "Settings" → "Domains"
2. Add your custom domain
3. Configure DNS as instructed

### Environment Variables Management

- Use Railway's environment variables for secrets
- Never commit `.env` files with real secrets
- Use Railway's variable management UI

### Monitoring

- Railway provides logs for each service
- Check "Metrics" tab for resource usage
- Set up alerts if needed

## Cost Considerations

- Railway offers a free tier with usage limits
- PostgreSQL database is included
- Monitor usage in Railway dashboard
- Upgrade plan if needed

## Quick Reference

**Backend Service**:
- Root: `backend/`
- Build: Auto-detected
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Port: `$PORT` (set by Railway)

**Frontend Service**:
- Root: `frontend/`
- Build: `npm install && npm run build`
- Start: `npx serve dist -s -l $PORT` or `npm run preview`
- Port: `$PORT` (set by Railway)

**Environment Variables**:
- Backend: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CODEFORCES_API_URL`
- Frontend: `VITE_API_BASE_URL`

## Next Steps After Deployment

1. Test all functionality
2. Monitor logs for errors
3. Set up custom domains (optional)
4. Configure backups for database
5. Set up monitoring/alerts

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway status: https://status.railway.app
