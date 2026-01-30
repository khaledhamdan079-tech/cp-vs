@echo off
echo Cleaning project before deployment...
echo.

REM Remove Python cache files
echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Removing %%d
    rd /s /q "%%d"
)
for /r . %%f in (*.pyc *.pyo) do @if exist "%%f" (
    echo Removing %%f
    del /q "%%f"
)

REM Remove local database files
echo Removing local database files...
if exist "backend\cpvs.db" (
    echo Removing backend\cpvs.db
    del /q "backend\cpvs.db"
)

REM Remove node_modules if exists
echo Checking for node_modules...
if exist "frontend\node_modules" (
    echo node_modules found - keeping (needed for build)
)

REM Remove dist folders
echo Removing build artifacts...
if exist "frontend\dist" (
    echo Removing frontend\dist
    rd /s /q "frontend\dist"
)

REM Remove .env files (keep .env.example)
echo Checking .env files...
if exist "backend\.env" (
    echo WARNING: backend\.env exists - make sure it's in .gitignore
)

echo.
echo Cleanup complete!
echo.
echo Files cleaned:
echo - Python cache files (__pycache__, *.pyc)
echo - Local database files (*.db)
echo - Build artifacts (dist/)
echo.
echo Ready to commit and deploy!
pause
