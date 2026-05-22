#!/usr/bin/env bash
# VocabFusion service status check (Linux / macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$ROOT/.pids"

port_status() {
  local port=$1
  if command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "LISTENING"
      return
    fi
  elif command -v ss >/dev/null 2>&1; then
    if ss -ltn 2>/dev/null | grep -q ":${port} "; then
      echo "LISTENING"
      return
    fi
  fi
  echo "DOWN"
}

http_ok() {
  local url=$1
  local label=$2
  if command -v curl >/dev/null 2>&1; then
    if curl -sf --max-time 3 "$url" >/dev/null 2>&1; then
      echo "[OK] $label"
      return 0
    fi
  elif command -v wget >/dev/null 2>&1; then
    if wget -q --spider --timeout=3 "$url" 2>/dev/null; then
      echo "[OK] $label"
      return 0
    fi
  fi
  echo "[--] $label not reachable"
  return 1
}

echo "=== VocabFusion Service Status ==="
echo ""
echo "Backend  (port 8000): $(port_status 8000)"
echo "Frontend (port 3000): $(port_status 3000)"
echo ""

if [[ -f "$PID_DIR/backend.pid" ]]; then
  echo "Backend PID file: $(cat "$PID_DIR/backend.pid")"
fi
if [[ -f "$PID_DIR/frontend.pid" ]]; then
  echo "Frontend PID file: $(cat "$PID_DIR/frontend.pid")"
fi
echo ""

if command -v curl >/dev/null 2>&1; then
  if curl -sf --max-time 3 "http://127.0.0.1:8000/health" | grep -q '"healthy"'; then
    echo "[OK] Backend API /health"
  else
    echo "[--] Backend API /health"
  fi
else
  http_ok "http://127.0.0.1:8000/health" "Backend API /health" || true
fi

http_ok "http://127.0.0.1:3000" "Frontend http://127.0.0.1:3000" || true

echo ""
echo "URLs: Backend http://localhost:8000/docs  Frontend http://localhost:3000"
echo "Demo: demo / demo123"
