# ✅ Setup Complete!

Your CP VS project is now fully set up and ready to test!

## What's Installed

✅ **Backend:**
- Python virtual environment (`backend/venv/`)
- All Python dependencies installed
- SQLite database configured
- Database tables created

✅ **Frontend:**
- Node.js v24.13.0 installed
- npm v11.6.2 installed
- All frontend dependencies installed

## Quick Start

### Option 1: Use Batch Files (Easiest)

**Terminal 1 - Start Backend:**
```cmd
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"
start_server.bat
```

**Terminal 2 - Start Frontend:**
```cmd
cd "C:\Users\khaled\Desktop\projects\CP VS"
start_frontend.bat
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\frontend"
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Test the Application

1. Open http://localhost:3000 in your browser
2. Register a user (e.g., handle: "testuser1", password: "test123")
3. Open an incognito window, register another user (e.g., "testuser2")
4. In the first window: Click "Create Challenge" → Search for "testuser2" → Select difficulty → Create
5. In the second window: Dashboard → Accept the challenge
6. View the created contest!

## Important Notes

### PATH Update
If you open a **new terminal** and Node.js commands don't work:
- Close and reopen your terminal/PowerShell
- Or restart your computer
- Node.js should then be available

### Virtual Environment
Always activate the backend virtual environment before running Python commands:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### Database
- Using SQLite for local testing (no setup needed!)
- Database file: `backend/cpvs.db`
- For production, switch to PostgreSQL

## Troubleshooting

**Backend won't start:**
- Make sure virtual environment is activated
- Check if port 8000 is available
- Verify `.env` file exists in `backend/` folder

**Frontend won't start:**
- Make sure Node.js is installed: `node --version`
- Check if port 3000 is available
- Try deleting `node_modules` and running `npm install` again

**npm/node not recognized:**
- Restart your terminal/PowerShell
- Or restart your computer
- Verify Node.js installation: Check `C:\Program Files\nodejs\` exists

## Next Steps

1. Start both servers (backend and frontend)
2. Test user registration and login
3. Create challenges between users
4. Test contest creation and problem selection
5. Deploy to Railway when ready (see README.md)

Enjoy testing your CP VS platform! 🚀
