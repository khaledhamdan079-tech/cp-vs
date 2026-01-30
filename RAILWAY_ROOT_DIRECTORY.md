# How to Set Root Directory in Railway

## Method 1: Using Settings Tab (Recommended)

1. **After creating the service**, click on the service tile/box in Railway dashboard
2. Click the **"Settings"** tab (top navigation bar)
3. Scroll down to find different sections:
   - Look for **"Source"** section
   - Or **"General"** section
   - Or **"Configuration"** section
4. Find the field labeled:
   - **"Root Directory"**
   - **"Root Path"**
   - **"Working Directory"**
   - Or similar
5. Enter: `backend` (for backend) or `frontend` (for frontend)
6. Changes save automatically or click "Save"

## Method 2: Using railway.json (Already Created!)

I've already created `railway.json` files for you. Railway should detect them automatically!

**For Backend**: `backend/railway.json` exists
**For Frontend**: `frontend/railway.json` exists

If Railway detects these files, it will use them automatically. However, you may still need to set the root directory in Settings.

## Method 3: Using Railway CLI

If the UI doesn't work, you can use Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Set root directory for backend service
railway variables set RAILWAY_ROOT_DIRECTORY=backend

# Or use the service-specific command
railway run --service backend --directory backend
```

## Method 4: Check Service Settings Location

The Root Directory option might be in different places:

### Option A: Settings → Source
- Click service → Settings tab → Source section → Root Directory

### Option B: Settings → General  
- Click service → Settings tab → General section → Root Directory

### Option C: Service Configuration
- Click service → Look for "Configure" or "Edit" button
- Root Directory might be in a modal/popup

### Option D: Service Variables
- Sometimes it's set via environment variable
- Check Variables tab for `RAILWAY_ROOT_DIRECTORY`

## Method 5: Create Separate Repositories (Easiest)

If you can't find the option, the easiest solution is:

1. **Create two separate GitHub repositories**:
   - `cp-vs-backend` - Copy only the `backend/` folder contents
   - `cp-vs-frontend` - Copy only the `frontend/` folder contents

2. **Deploy each separately**:
   - Deploy `cp-vs-backend` repo → No root directory needed
   - Deploy `cp-vs-frontend` repo → No root directory needed

This is actually cleaner and easier to manage!

## Current Railway UI (2024)

Railway's UI has changed over time. Here's where to look:

1. **Service Tile** → Click it
2. **Top Tabs**: Settings | Variables | Deployments | Metrics
3. **Settings Tab** → Scroll down:
   - **Source** section (has Root Directory)
   - **Build** section (has Build Command)
   - **Deploy** section (has Start Command)

## If You Still Can't Find It

1. **Check Railway Documentation**: https://docs.railway.app/guides/services
2. **Contact Railway Support**: They're very responsive
3. **Use Separate Repos**: This is often the easiest solution
4. **Check Railway Discord**: https://discord.gg/railway

## Quick Test

Try this:
1. Create the service
2. Let Railway auto-detect (it might work!)
3. Check the build logs - if it fails looking for files, you need root directory
4. If build succeeds, you might not need to set it!

## Alternative: Use railway.toml

Create `railway.toml` in project root:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[service]
rootDirectory = "backend"
```

But this might not work for monorepos. Railway might need separate services.
