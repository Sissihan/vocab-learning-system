@echo off
setlocal EnableExtensions
echo === VocabFusion Environment Init (Backend + Frontend) ===
echo.

call "%~dp0init-backend.bat"
if errorlevel 1 (
    echo.
    echo [FAIL] Backend init failed.
    pause
    exit /b 1
)

call "%~dp0init-frontend.bat"
if errorlevel 1 (
    echo.
    echo [FAIL] Frontend init failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] All environments initialized.
echo Next: run start.bat to launch services.
echo Check: scripts\check_system.ps1
echo ========================================
pause
exit /b 0
