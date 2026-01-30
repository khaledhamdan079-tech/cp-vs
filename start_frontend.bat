@echo off
echo ========================================
echo   CP VS Frontend Server
echo ========================================
echo.

REM Refresh PATH to include Node.js
set PATH=%PATH%;C:\Program Files\nodejs\

REM Check if Node.js is installed
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please restart your terminal or install Node.js
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo npm version:
npm --version
echo.

cd /d "%~dp0frontend"

echo Installing/updating dependencies...
call npm install

echo.
echo Starting frontend server on http://localhost:3000
echo Backend should be running on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
