# Railway Quick Start Guide

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository

### Step 3: Deploy Backend

1. Railway will create a service automatically
2. **Click on the service** (the tile/box)
3. Go to **"Settings"** tab (top right)
4. Scroll down to **"Source"** section
5. Find **"Root Directory"** field
6. Enter: `backend`
7. Scroll to **"Deploy"** section
8. Set **"Start Command"** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
9. Click **"Save"** or changes auto-save

### Step 4: Add PostgreSQL Database

1. In your Railway project, click **"New"** button
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway creates the database
5. **DATABASE_URL is automatically set** - you don't need to copy it!

### Step 5: Set Backend Environment Variables

1. Still in backend service → **"Variables"** tab
2. Click **"New Variable"** for each:

```
JWT_SECRET_KEY = <generate-random-key>
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
CODEFORCES_API_URL = https://codeforces.com/api
```

**Generate JWT Secret Key**:
- Visit: https://randomkeygen.com/
- Copy a "CodeIgniter Encryption Keys" (32+ characters)
- Or use PowerShell: `-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})`

### Step 6: Get Backend URL

1. In backend service → **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://your-backend.up.railway.app`)

### Step 7: Deploy Frontend

1. In same Railway project, click **"New"** button
2. Select **"GitHub Repo"**
3. Choose your repository again
4. **Click on the new frontend service**
5. Go to **"Settings"** tab
6. **"Source"** section → Set **Root Directory** to: `frontend`
7. **"Build"** section → Set **Build Command** to: `npm install && npm run build`
8. **"Deploy"** section → Set **Start Command** to: `npx serve dist -s -l $PORT`

### Step 8: Set Frontend Environment Variable

1. In frontend service → **"Variables"** tab
2. Click **"New Variable"**
3. Add:
   ```
   VITE_API_BASE_URL = https://your-backend.up.railway.app
   ```
   (Use your actual backend URL from Step 6)

### Step 9: Get Frontend URL

1. In frontend service → **"Settings"** tab
2. **"Domains"** section → **"Generate Domain"**
3. Copy frontend URL

### Step 10: Update Backend CORS

1. Go back to backend service → **"Variables"** tab
2. Add new variable:
   ```
   FRONTEND_URL = https://your-frontend.up.railway.app
   ```
   (Use your actual frontend URL)
3. Railway will automatically redeploy

### Step 11: Test

1. Visit your frontend URL
2. Register a user
3. Test the application!

## Where to Find Settings

**Root Directory Location**:
1. Click on your service (the tile/box in Railway dashboard)
2. Click **"Settings"** tab (top navigation)
3. Scroll down to **"Source"** section
4. **Root Directory** is there

**If you still can't find it**:
- Look for **"Configure"** button on the service tile
- Or check **"Settings"** → **"General"** section
- Railway UI may vary - look for any field that says "Root", "Directory", or "Path"

## Alternative: Use Separate Repositories

If Railway doesn't support root directory well, you can:

1. **Create separate GitHub repos**:
   - One for backend (only backend folder)
   - One for frontend (only frontend folder)

2. **Deploy each separately**:
   - Backend repo → Railway backend service
   - Frontend repo → Railway frontend service

## Troubleshooting

**Can't find Root Directory**:
- Make sure you're in the **Settings** tab of the service
- Try refreshing the page
- Check if Railway UI has changed - look for "Source" or "Configuration" sections

**Service won't start**:
- Check **"Deployments"** tab → **"View Logs"**
- Verify Root Directory is set correctly
- Check Start Command uses `$PORT`

**Build fails**:
- Check build logs in **"Deployments"** tab
- Verify Root Directory points to correct folder
- Ensure all files are in the repository

## Visual Guide

```
Railway Dashboard
├── Your Project
    ├── Backend Service (click this)
    │   ├── Settings Tab
    │   │   ├── Source Section
    │   │   │   └── Root Directory: "backend"
    │   │   ├── Deploy Section
    │   │   │   └── Start Command: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    │   │   └── Domains Section
    │   │       └── Generate Domain
    │   └── Variables Tab
    │       └── Add environment variables
    │
    ├── Frontend Service (click this)
    │   ├── Settings Tab
    │   │   ├── Source Section
    │   │   │   └── Root Directory: "frontend"
    │   │   ├── Build Section
    │   │   │   └── Build Command: "npm install && npm run build"
    │   │   ├── Deploy Section
    │   │   │   └── Start Command: "npx serve dist -s -l $PORT"
    │   │   └── Domains Section
    │   │       └── Generate Domain
    │   └── Variables Tab
    │       └── VITE_API_BASE_URL
    │
    └── PostgreSQL Database
        └── DATABASE_URL (auto-set)
```

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway status: https://status.railway.app
