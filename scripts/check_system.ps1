# VocabFusion system health check
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Write-Host "=== VocabFusion System Check ===" -ForegroundColor Cyan

# 1. Backend venv
if (-not (Test-Path (Join-Path $Backend "venv\Scripts\python.exe"))) {
    Write-Host "[FAIL] Backend venv missing. Run: cd backend; python -m venv venv; pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Backend venv" -ForegroundColor Green

# 2. Database
$db = Join-Path $Backend "data\vocab.db"
if (-not (Test-Path $db)) {
    Write-Host "[WARN] Database missing, seeding..." -ForegroundColor Yellow
    Push-Location $Backend
    & .\venv\Scripts\python scripts\seed_data.py
    Pop-Location
}
Write-Host "[OK] Database" -ForegroundColor Green

# 3. Backend import
Push-Location $Backend
& .\venv\Scripts\python -c "from app.main import app; print('import ok')" | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host "[FAIL] Backend import" -ForegroundColor Red; exit 1 }
Write-Host "[OK] Backend import" -ForegroundColor Green
Pop-Location

# 4. Frontend deps
if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
    Write-Host "[WARN] node_modules missing, run npm install in frontend/" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Frontend node_modules" -ForegroundColor Green
}

# 5. API (if backend running)
try {
    $h = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3
    if ($h.status -eq "healthy") {
        Write-Host "[OK] Backend API http://127.0.0.1:8000" -ForegroundColor Green
        Push-Location $Backend
        & .\venv\Scripts\python scripts\verify_api.py
        $apiOk = $LASTEXITCODE -eq 0
        Pop-Location
        if (-not $apiOk) { exit 1 }
    }
} catch {
    Write-Host "[SKIP] Backend not running (start with start.bat)" -ForegroundColor Yellow
}

# 6. Frontend (if running)
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:3000" -UseBasicParsing -TimeoutSec 3
    if ($r.StatusCode -eq 200) {
        Write-Host "[OK] Frontend http://127.0.0.1:3000" -ForegroundColor Green
    }
} catch {
    Write-Host "[SKIP] Frontend not running (start with start.bat)" -ForegroundColor Yellow
}

Write-Host "`nCheck complete. Demo: demo / demo123" -ForegroundColor Cyan
