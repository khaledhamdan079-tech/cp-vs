# Railway Environment Variables Setup

## Required Environment Variables

When deploying to Railway, you **MUST** set these environment variables in your backend service:

### Step-by-Step: Setting Environment Variables

1. **Go to your backend service** in Railway dashboard
2. Click on **"Variables"** tab
3. Click **"New Variable"** for each one:

#### Required Variables:

```
DATABASE_URL
```
- **Value**: Automatically set by Railway when you add PostgreSQL
- **You don't need to set this manually!**
- Railway sets it automatically when you add a PostgreSQL database

```
JWT_SECRET_KEY
```
- **Value**: Generate a strong random key (32+ characters)
- **How to generate**:
  - Visit: https://randomkeygen.com/
  - Copy a "CodeIgniter Encryption Keys" (32+ characters)
  - Or use: `openssl rand -hex 32` (Linux/Mac)
  - Or PowerShell: `-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})`

```
JWT_ALGORITHM
```
- **Value**: `HS256`

```
ACCESS_TOKEN_EXPIRE_MINUTES
```
- **Value**: `1440` (24 hours)

```
CODEFORCES_API_URL
```
- **Value**: `https://codeforces.com/api`

```
FRONTEND_URL
```
- **Value**: Your frontend Railway URL (set this after deploying frontend)
- Example: `https://your-frontend.up.railway.app`

## Important Notes

1. **Variable Names**: Railway uses **UPPERCASE** for environment variables
   - Railway provides: `DATABASE_URL`
   - Our code reads: `database_url` (automatically mapped)

2. **DATABASE_URL**: 
   - Railway automatically sets this when you add PostgreSQL
   - You'll see it in the Variables tab
   - **Don't change it!**

3. **After Adding Variables**:
   - Railway automatically redeploys
   - Check the "Deployments" tab to see the new deployment
   - Check logs to verify it's working

## Verification

After setting variables, check the deployment logs:

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Click **"View Logs"**
4. Look for:
   - ✅ "Application startup complete"
   - ✅ No "Field required" errors
   - ✅ Database connection successful

## Troubleshooting

**Error: "Field required"**:
- You haven't set all required environment variables
- Go to Variables tab and add missing ones
- Make sure variable names match exactly (case-sensitive in Railway UI)

**Error: "Database connection failed"**:
- Verify PostgreSQL service is running
- Check DATABASE_URL is set (should be automatic)
- Verify DATABASE_URL format is correct

**Error: "JWT_SECRET_KEY required"**:
- Add JWT_SECRET_KEY variable
- Make sure it's a strong random string
- Redeploy after adding

## Quick Setup Script

You can also set variables via Railway CLI:

```bash
railway variables set JWT_SECRET_KEY=your-secret-key
railway variables set JWT_ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=1440
railway variables set CODEFORCES_API_URL=https://codeforces.com/api
```

But the easiest way is through the Railway web UI!
