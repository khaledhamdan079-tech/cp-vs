# Deploying New Features to Railway

This guide covers deploying the new features (rating system, homepage, leaderboard, user profiles) to Railway.

## Step 1: Commit and Push Changes

### 1.1 Stage All Changes

```bash
# Navigate to project root
cd "C:\Users\khaled\Desktop\projects\CP VS"

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Add rating system, homepage, leaderboard, and user profiles"

# Push to GitHub
git push origin main
```

**Note**: If you haven't initialized git yet:
```bash
git init
git add .
git commit -m "Initial commit with new features"
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Step 2: Database Migration

### Important: New Database Fields

The new features add:
- `rating` field to `users` table (default: 1000)
- `rating_history` table

**Railway will automatically create these tables** when the backend starts because we use `Base.metadata.create_all(bind=engine)` in `main.py`.

However, if you have existing users, you may need to:

### Option A: Let Railway Auto-Create (Recommended)
- Railway will create new tables automatically
- Existing users will get `rating = 1000` (default value)
- No manual migration needed

### Option B: Manual Migration (If Needed)
If you encounter issues, you can run a migration script locally first, then push:

```python
# Create a migration script: backend/migrate_ratings.py
from app.database import SessionLocal, engine, Base
from app.models import User, RatingHistory
from sqlalchemy import text

# Create tables
Base.metadata.create_all(bind=engine)

# Update existing users with default rating
db = SessionLocal()
try:
    db.execute(text("UPDATE users SET rating = 1000 WHERE rating IS NULL"))
    db.commit()
    print("Migration completed!")
finally:
    db.close()
```

## Step 3: Railway Automatic Deployment

Railway will automatically detect the push and redeploy:

1. **Backend Service**:
   - Railway will rebuild and redeploy automatically
   - Check the "Deployments" tab to see progress
   - Wait for deployment to complete (usually 2-5 minutes)

2. **Frontend Service**:
   - Railway will rebuild and redeploy automatically
   - Check the "Deployments" tab to see progress

## Step 4: Verify Deployment

### 4.1 Check Backend Logs

1. Go to Railway dashboard → Backend service
2. Click "Deployments" → Latest deployment → "View Logs"
3. Look for:
   - ✅ "Application startup complete"
   - ✅ No database errors
   - ✅ Tables created successfully

### 4.2 Test Backend Endpoints

Visit your backend URL:
- `https://your-backend.up.railway.app/docs` - Should show FastAPI docs
- `https://your-backend.up.railway.app/api/users/leaderboard` - Should return leaderboard (may be empty initially)
- `https://your-backend.up.railway.app/api/contests/public/latest` - Should return latest contests

### 4.3 Test Frontend

Visit your frontend URL:
- `https://your-frontend.up.railway.app` - Should show new homepage
- `https://your-frontend.up.railway.app/leaderboard` - Should show leaderboard page
- Try registering a new user (with valid Codeforces handle)
- Try viewing a user profile: `https://your-frontend.up.railway.app/users/<handle>`

## Step 5: Troubleshooting

### Issue: Database Migration Errors

**Error**: `column "rating" does not exist`

**Solution**: 
1. Check backend logs for the exact error
2. The tables should auto-create, but if not:
   - Go to Railway → Backend service → "Variables"
   - Temporarily add: `FORCE_MIGRATE=true`
   - Redeploy
   - Remove the variable after successful deployment

### Issue: Frontend Not Loading

**Error**: Blank page or errors

**Solution**:
1. Check frontend deployment logs
2. Verify `VITE_API_BASE_URL` is set correctly
3. Check browser console for errors
4. Verify backend CORS settings include your frontend URL

### Issue: Rating Not Updating

**Error**: Ratings stay at 1000

**Solution**:
1. Verify contests are completing successfully
2. Check backend logs for rating update errors
3. Ensure `RatingHistory` table exists
4. Test with a completed contest

### Issue: Codeforces Handle Validation Failing

**Error**: "Invalid Codeforces handle" for valid handles

**Solution**:
1. Check backend logs for Codeforces API errors
2. Verify Codeforces API is accessible
3. Check rate limiting (Codeforces has rate limits)

## Step 6: Post-Deployment Checklist

- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Database tables created (check logs)
- [ ] Homepage loads correctly
- [ ] Leaderboard page loads
- [ ] User registration works with Codeforces handle validation
- [ ] User profiles display correctly
- [ ] Rating system updates after contest completion
- [ ] Public endpoints work without authentication

## Quick Commands Reference

```bash
# Check git status
git status

# See what files changed
git diff

# Commit changes
git add .
git commit -m "Your commit message"
git push origin main

# Check Railway deployment status (via Railway CLI if installed)
railway status
```

## Notes

- **Database**: Railway uses PostgreSQL, and tables are created automatically on startup
- **Environment Variables**: Make sure all required variables are set in Railway
- **CORS**: Frontend URL should be in backend's `FRONTEND_URL` variable
- **Build Time**: Backend typically takes 2-3 minutes, frontend 3-5 minutes
- **First Deploy**: May take longer as dependencies are installed

## Need Help?

If deployment fails:
1. Check Railway deployment logs
2. Verify all environment variables are set
3. Check that GitHub repository is connected
4. Ensure root directories are set correctly (backend: `backend`, frontend: `frontend`)
