@echo off
setlocal EnableExtensions EnableDelayedExpansion
echo === Stopping VocabFusion ===
echo.

set "FOUND=0"
for %%P in (8000 3000) do (
  for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
    if not defined PID_%%a (
      set "PID_%%a=1"
      set /a FOUND+=1
      echo Stopping process on port %%P ^(PID %%a^)
      taskkill /PID %%a /T /F >nul 2>&1
      if errorlevel 1 (
        echo   [WARN] Could not stop PID %%a - try running as Administrator
      )
    )
  )
)

taskkill /FI "WINDOWTITLE eq VocabFusion API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq VocabFusion Web*" /F >nul 2>&1

if %FOUND%==0 (
  echo No listening process found on ports 8000 or 3000.
) else (
  echo.
  echo Stopped. Run status.bat to verify.
)
exit /b 0
