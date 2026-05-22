#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$ROOT/.pids"
mkdir -p "$PID_DIR"

echo "=== VocabFusion Learning System ==="

cd "$ROOT/backend"
if [[ ! -d venv ]]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi
# shellcheck source=/dev/null
source venv/bin/activate
pip install -r requirements.txt -q
python scripts/seed_data.py

python run.py &
echo $! >"$PID_DIR/backend.pid"

cd "$ROOT/frontend"
if [[ ! -d node_modules ]]; then
  echo "Installing frontend dependencies..."
  npm install
fi
npm run dev &
echo $! >"$PID_DIR/frontend.pid"

echo ""
echo "Backend:  http://localhost:8000  (docs: /docs)"
echo "Frontend: http://localhost:3000"
echo "Demo: demo / demo123"
echo ""
echo "Status: ./status.sh   Stop: ./stop.sh   (or Ctrl+C here)"
echo "Press Ctrl+C to stop both services"

cleanup() {
  "$ROOT/stop.sh" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
wait
