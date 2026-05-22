#!/usr/bin/env bash
# Initialize frontend: npm dependencies
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND="$ROOT/frontend"

echo "=== VocabFusion Frontend Init ==="
echo ""

if ! command -v node >/dev/null 2>&1; then
  echo "[FAIL] node not found. Install Node.js 18+."
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "[FAIL] npm not found."
  exit 1
fi
echo "Node: $(node --version)"
echo "npm:  $(npm --version)"

cd "$FRONTEND"
echo "Installing npm dependencies..."
npm install

echo ""
echo "[OK] Frontend environment ready."
echo "    deps: $FRONTEND/node_modules"
