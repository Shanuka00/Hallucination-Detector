@echo off
echo Starting Enhanced Hallucination Detection System...
echo.

cd /d "%~dp0"

echo Running setup and configuration check...
cd backend
py setup.py

echo.
echo Starting FastAPI backend server...
start "Backend Server" cmd /k "py -m uvicorn app:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Backend server is starting at http://localhost:8000
echo Frontend is available at http://localhost:8000/static/index.html
echo.
echo Press any key to open the application in your browser...
pause > nul

start http://localhost:8000/static/index.html

echo.
echo Enhanced Application is now running!
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8000/static/index.html
echo Configuration: Check backend\.env file for API settings
echo.
echo Press any key to close this window...
pause > nul
