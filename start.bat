@echo off
echo ⚖  Veritas — Starting up...
echo.

:: Backend
echo Starting backend...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements.txt
start /B uvicorn main:app --reload --port 8000
cd ..

:: Frontend
echo Starting frontend...
cd frontend
if not exist node_modules (
    npm install
)
start /B npm run dev
cd ..

echo.
echo ✅ Veritas is running!
echo    Frontend ^→ http://localhost:3000
echo    Backend  ^→ http://localhost:8000
echo    API Docs ^→ http://localhost:8000/api/docs
echo.
pause
