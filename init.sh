#!/usr/bin/env bash
# Initialize backend + frontend environments (no services started)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== VocabFusion Environment Init (Backend + Frontend) ==="
echo ""

"$ROOT/init-backend.sh"
"$ROOT/init-frontend.sh"

echo ""
echo "========================================"
echo "[OK] All environments initialized."
echo "Next: ./start.sh to launch services."
echo "Check: ./scripts/check_system.sh"
echo "========================================"
