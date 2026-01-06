#!/usr/bin/env bash
set -euo pipefail

echo "Build and preview the frontend, then smoke test the app loads"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRONTEND_DIR=$(cd "$SCRIPT_DIR/../../frontend" && pwd)
cd "$FRONTEND_DIR"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Please install Node.js >= 18" >&2
  exit 1
fi

npm install
npm run build

# Start preview server
PORT=${PORT:-5173}
( npm run preview >/tmp/frontend_smoke.log 2>&1 ) &
PID=$!

cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT

ATTEMPTS=30
until curl -fsS "http://127.0.0.1:$PORT/" >/dev/null || [ $ATTEMPTS -eq 0 ]; do
  ATTEMPTS=$((ATTEMPTS-1))
  sleep 1
  echo "Waiting for frontend... attempts left: $ATTEMPTS"
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "Frontend preview exited unexpectedly:" >&2
    tail -n +1 /tmp/frontend_smoke.log || true
    exit 1
  fi
done

curl -fsS "http://127.0.0.1:$PORT/" >/dev/null
printf "Frontend smoke test passed\n"
