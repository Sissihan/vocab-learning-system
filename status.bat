@echo off
setlocal EnableExtensions
echo === VocabFusion Service Status ===
echo.

set "BACKEND_PORT=DOWN"
set "FRONTEND_PORT=DOWN"

netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 set "BACKEND_PORT=LISTENING"

netstat -ano | findstr ":3000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 set "FRONTEND_PORT=LISTENING"

echo Backend  (port 8000): %BACKEND_PORT%
echo Frontend (port 3000): %FRONTEND_PORT%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $h = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3; if ($h.status -eq 'healthy') { Write-Host '[OK] Backend API /health' -ForegroundColor Green } else { Write-Host '[WARN] Backend /health not healthy' -ForegroundColor Yellow } } catch { Write-Host '[--] Backend API not reachable' -ForegroundColor DarkYellow }"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:3000' -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -eq 200) { Write-Host '[OK] Frontend http://127.0.0.1:3000' -ForegroundColor Green } } catch { Write-Host '[--] Frontend not reachable' -ForegroundColor DarkYellow }"

echo.
echo URLs: Backend http://localhost:8000/docs  Frontend http://localhost:3000
echo Demo: demo / demo123
exit /b 0
