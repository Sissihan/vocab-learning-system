@echo off
echo === VocabFusion Learning System ===
echo.

cd /d "%~dp0backend"
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
python scripts\seed_data.py

start "VocabFusion API" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && python run.py"

cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
start "VocabFusion Web" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend: http://localhost:8000  (API docs: /docs)
echo Frontend: http://localhost:3000
echo Demo login: demo / demo123
pause
