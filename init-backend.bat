@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%backend"

echo === VocabFusion Backend Init ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found. Install Python 3.10+ and add to PATH.
    exit /b 1
)

for /f "delims=" %%v in ('python --version 2^>^&1') do echo Python: %%v

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [FAIL] Failed to create venv.
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [FAIL] pip install failed.
    exit /b 1
)

if not exist "data" mkdir data

echo Seeding database...
python scripts\seed_data.py
if errorlevel 1 (
    echo [FAIL] seed_data.py failed.
    exit /b 1
)

echo Verifying backend import...
python -c "from app.main import app; print('[OK] Backend import')"
if errorlevel 1 (
    echo [FAIL] Backend import check failed.
    exit /b 1
)

echo.
echo [OK] Backend environment ready.
echo     venv: %ROOT%backend\venv
echo     db:   %ROOT%backend\data\vocab.db
exit /b 0
