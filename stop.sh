#!/usr/bin/env bash
# Stop VocabFusion backend and frontend (Linux / macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$ROOT/.pids"

stop_pid_file() {
  local name=$1
  local file=$2
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      # uvicorn --reload spawns child processes
      pkill -P "$pid" 2>/dev/null || true
      echo "Stopped $name (PID $pid)"
    fi
    rm -f "$file"
  fi
}

echo "=== Stopping VocabFusion ==="
echo ""

mkdir -p "$PID_DIR"
stop_pid_file "backend" "$PID_DIR/backend.pid"
stop_pid_file "frontend" "$PID_DIR/frontend.pid"

for port in 8000 3000; do
  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pids" ]]; then
      echo "$pids" | xargs kill -9 2>/dev/null || true
      echo "Stopped processes on port $port"
    fi
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" 2>/dev/null && echo "Stopped port $port" || true
  fi
done

echo ""
echo "Stopped. Run ./status.sh to verify."
