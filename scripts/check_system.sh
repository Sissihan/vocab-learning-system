#!/usr/bin/env bash
# VocabFusion system health check (Linux / macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PY="$BACKEND/venv/bin/python"

echo "=== VocabFusion System Check ==="

if [[ ! -x "$PY" ]]; then
  echo "[FAIL] Backend venv missing. Run: cd backend && python3 -m venv venv && pip install -r requirements.txt"
  exit 1
fi
echo "[OK] Backend venv"

DB="$BACKEND/data/vocab.db"
if [[ ! -f "$DB" ]]; then
  echo "[WARN] Database missing, seeding..."
  (cd "$BACKEND" && "$PY" scripts/seed_data.py)
fi
echo "[OK] Database"

(cd "$BACKEND" && "$PY" -c "from app.main import app; print('import ok')") >/dev/null
echo "[OK] Backend import"

if [[ -d "$FRONTEND/node_modules" ]]; then
  echo "[OK] Frontend node_modules"
else
  echo "[WARN] node_modules missing, run: cd frontend && npm install"
fi

if curl -sf --max-time 3 "http://127.0.0.1:8000/health" | grep -q '"healthy"'; then
  echo "[OK] Backend API http://127.0.0.1:8000"
  (cd "$BACKEND" && "$PY" scripts/verify_api.py) || exit 1
else
  echo "[SKIP] Backend not running (start with ./start.sh)"
fi

if curl -sf --max-time 3 -o /dev/null "http://127.0.0.1:3000"; then
  echo "[OK] Frontend http://127.0.0.1:3000"
else
  echo "[SKIP] Frontend not running (start with ./start.sh)"
fi

echo ""
echo "Check complete. Demo: demo / demo123"
