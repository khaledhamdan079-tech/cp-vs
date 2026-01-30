# Frontend Deployment Steps

Now that your backend is deployed, follow these steps to deploy the frontend:

## Step 1: Get Your Backend URL

1. Go to your Railway project dashboard
2. Click on your **backend service**
3. Go to **Settings** tab
4. Scroll down to **"Networking"** section
5. Click **"Generate Domain"** (if not already generated)
6. Copy your backend URL (e.g., `https://your-backend-name.up.railway.app`)
7. Test it: Visit `https://your-backend-url.up.railway.app/docs` - you should see FastAPI docs

## Step 2: Deploy Frontend Service

1. In your Railway project dashboard, click **"New"** → **"GitHub Repo"**
2. Select your repository again
3. **After the service is created**, click on the new service tile
4. Go to **Settings** tab
5. Scroll down to **"Source"** section
6. Set **Root Directory** to: `frontend`
7. Railway should auto-detect the build settings, but verify:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve dist -s -l $PORT`

## Step 3: Set Frontend Environment Variable

1. In your **frontend service**, go to **"Variables"** tab
2. Click **"New Variable"**
3. Set:
   - **Variable Name**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-url.up.railway.app` (use your actual backend URL from Step 1)
4. Click **"Add"**

**Important**: Replace `your-backend-url` with your actual backend Railway URL (no trailing slash).

## Step 4: Generate Frontend Domain

1. In your frontend service, go to **Settings** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy your frontend URL (e.g., `https://your-frontend-name.up.railway.app`)

## Step 5: Update Backend CORS

1. Go back to your **backend service** → **"Variables"** tab
2. Click **"New Variable"**
3. Set:
   - **Variable Name**: `FRONTEND_URL`
   - **Value**: `https://your-frontend-url.up.railway.app` (use your actual frontend URL from Step 4)
4. Click **"Add"**

Railway will automatically redeploy your backend with the updated CORS settings.

## Step 6: Verify Deployment

### Test Backend:
- Visit: `https://your-backend-url.up.railway.app/docs`
- Should show FastAPI documentation
- Try the `/health` endpoint: `https://your-backend-url.up.railway.app/health`

### Test Frontend:
- Visit: `https://your-frontend-url.up.railway.app`
- Should load the React app
- Try registering a new user
- Try logging in

### Test Integration:
1. Register a user in the frontend
2. Create a challenge
3. Verify everything works end-to-end

## Troubleshooting

**Frontend shows "Network Error" or can't connect to backend:**
- Check that `VITE_API_BASE_URL` is set correctly in frontend variables
- Verify backend URL is accessible (visit `/docs` endpoint)
- Check backend logs for CORS errors

**CORS errors in browser console:**
- Verify `FRONTEND_URL` is set in backend variables
- Make sure frontend URL matches exactly (including `https://`)
- Check backend logs to see if CORS middleware is working

**Frontend shows blank page:**
- Check frontend deployment logs for build errors
- Verify `npx serve dist -s -l $PORT` command is correct
- Check that `dist` folder exists after build

**Backend returns 404 for API routes:**
- Verify backend is running (check `/health` endpoint)
- Check that routes are prefixed with `/api` in frontend calls
- Verify backend routers are included in `main.py`

## Quick Checklist

- [ ] Backend deployed and accessible
- [ ] Backend URL copied
- [ ] Frontend service created with root directory `frontend`
- [ ] `VITE_API_BASE_URL` set in frontend variables
- [ ] Frontend domain generated
- [ ] Frontend URL copied
- [ ] `FRONTEND_URL` set in backend variables
- [ ] Backend redeployed (automatic)
- [ ] Frontend accessible and working
- [ ] Can register/login through frontend
- [ ] Can create challenges and contests

## Your URLs (Fill these in):

- **Backend URL**: `https://____________________.up.railway.app`
- **Frontend URL**: `https://____________________.up.railway.app`
