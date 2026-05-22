@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%frontend"

echo === VocabFusion Frontend Init ===
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Node.js not found. Install Node.js 18+ and add to PATH.
    exit /b 1
)

for /f "delims=" %%v in ('node --version 2^>^&1') do echo Node: %%v
for /f "delims=" %%v in ('npm --version 2^>^&1') do echo npm: %%v

echo Installing npm dependencies...
call npm install
if errorlevel 1 (
    echo [FAIL] npm install failed.
    exit /b 1
)

echo.
echo [OK] Frontend environment ready.
echo     deps: %ROOT%frontend\node_modules
exit /b 0
