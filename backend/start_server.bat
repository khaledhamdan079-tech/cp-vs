@echo off
echo ========================================
echo   CP VS Backend Server
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting server on http://localhost:8000
echo API docs: http://localhost:8000/docs
echo Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload

pause
