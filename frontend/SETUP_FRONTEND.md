# Frontend Setup Guide

## Prerequisites

Before setting up the frontend, make sure you have:
- ✅ Node.js 18+ installed (includes npm)
- ✅ Backend server running (optional, but recommended)

## Installation Steps

### 1. Install Node.js (if not installed)

See `../INSTALL_NODEJS.md` for detailed instructions.

Quick check:
```powershell
node --version
npm --version
```

### 2. Install Frontend Dependencies

Navigate to the frontend directory:
```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\frontend"
```

Install dependencies:
```powershell
npm install
```

This will install all required packages (React, Vite, Axios, etc.)

### 3. Start Development Server

```powershell
npm run dev
```

The frontend will start at: `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Configuration

The frontend is configured to proxy API requests to `http://localhost:8000` (backend).

To change the backend URL, edit `vite.config.js` or set environment variable:
```powershell
$env:VITE_API_BASE_URL="http://localhost:8000"
npm run dev
```

## Troubleshooting

**Port 3000 already in use:**
- Change port in `vite.config.js` or use:
  ```powershell
  npm run dev -- --port 3001
  ```

**npm install fails:**
- Delete `node_modules` folder and `package-lock.json`
- Run `npm install` again
- Check internet connection

**Cannot connect to backend:**
- Make sure backend is running on port 8000
- Check `vite.config.js` proxy settings
- Verify CORS is enabled in backend
