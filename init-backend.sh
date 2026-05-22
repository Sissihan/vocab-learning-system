#!/usr/bin/env bash
# Initialize backend: venv, pip deps, database seed
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
PY="$BACKEND/venv/bin/python"
PIP="$BACKEND/venv/bin/pip"

echo "=== VocabFusion Backend Init ==="
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "[FAIL] python3 not found. Install Python 3.10+."
  exit 1
fi
echo "Python: $(python3 --version)"

cd "$BACKEND"

if [[ ! -d venv ]]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Installing Python dependencies..."
"$PIP" install -r requirements.txt

mkdir -p data

echo "Seeding database..."
"$PY" scripts/seed_data.py

echo "Verifying backend import..."
"$PY" -c "from app.main import app; print('[OK] Backend import')"

echo ""
echo "[OK] Backend environment ready."
echo "    venv: $BACKEND/venv"
echo "    db:   $BACKEND/data/vocab.db"
