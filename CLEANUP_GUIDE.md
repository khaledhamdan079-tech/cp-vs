# Project Cleanup Guide

This guide helps you clean the project before deploying to Railway.

## What Gets Cleaned

### Files to Remove:
1. **Python cache files**: `__pycache__/`, `*.pyc`, `*.pyo`
2. **Local database files**: `*.db`, `*.sqlite`, `*.sqlite3` (like `cpvs.db`)
3. **Build artifacts**: `frontend/dist/`, `frontend/dist-ssr/`
4. **Environment files**: `.env` (local only, `.env.example` is kept)

### Files Kept:
- All source code files
- Configuration files (`.gitignore`, `package.json`, `requirements.txt`, etc.)
- Documentation files
- Test files (optional - can be removed if desired)
- Helper scripts (optional - can be removed if desired)

## Quick Cleanup (Windows)

### Option 1: Use the cleanup script
```bash
# Run the cleanup batch file
cleanup.bat
```

### Option 2: Manual cleanup
```bash
# Remove Python cache
cd backend
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
for /r . %f in (*.pyc *.pyo) do @if exist "%f" del /q "%f"

# Remove local database
del cpvs.db

# Remove frontend build artifacts
cd ..\frontend
if exist dist rd /s /q dist
```

## Files That Should NOT Be Committed

These are already in `.gitignore`:
- `backend/.env` - Local environment variables
- `backend/cpvs.db` - Local SQLite database
- `backend/__pycache__/` - Python cache
- `frontend/node_modules/` - Dependencies (installed on Railway)
- `frontend/dist/` - Build output (built on Railway)

## Pre-Deployment Checklist

Before committing and pushing:

- [ ] Run cleanup script or manual cleanup
- [ ] Verify `.env` files are not committed (check `git status`)
- [ ] Verify database files are not committed
- [ ] Verify no sensitive data in code
- [ ] Check that `.gitignore` is properly configured
- [ ] Test locally that everything still works

## What Railway Needs

Railway will:
- Install dependencies from `requirements.txt` and `package.json`
- Build the frontend from source (`npm run build`)
- Create database tables automatically
- Use environment variables from Railway dashboard

## Files Safe to Keep in Repository

These are fine to commit:
- `backend/.env.example` - Example environment file
- Test files (`test_*.py`) - Optional, but useful
- Helper scripts (`setup_local.py`, etc.) - Optional, but useful
- Documentation files (`.md` files)
- Configuration files (`railway.json`, `Procfile`, etc.)

## After Cleanup

1. **Check what will be committed**:
   ```bash
   git status
   ```

2. **Review changes**:
   ```bash
   git diff
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Clean project before deployment"
   git push origin main
   ```

## Troubleshooting

### Issue: Still seeing cache files in git status

**Solution**: They might already be tracked. Remove them:
```bash
git rm -r --cached backend/__pycache__
git rm --cached backend/*.pyc
```

### Issue: Database file still showing

**Solution**: Remove it from git tracking:
```bash
git rm --cached backend/cpvs.db
```

### Issue: .env file showing

**Solution**: Make sure it's in `.gitignore`, then:
```bash
git rm --cached backend/.env
```
