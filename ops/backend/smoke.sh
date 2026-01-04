#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test: start the app and hit /health and <>
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR=$(cd "$SCRIPT_DIR/../../backend" && pwd)
PROJECT_ROOT=$(cd "$BACKEND_DIR/.." && pwd)
cd "$PROJECT_ROOT"

pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null

export PYTHONPATH="$PROJECT_ROOT"
HOST=${1:-0.0.0.0}
PORT=${2:-5000}


# Start app in background
( gunicorn -w 1 -b "$HOST:$PORT" backend.src.app:app >/tmp/backend_smoke.log 2>&1 ) &
PID=$!

cleanup() {
  kill "$PID" 2>/dev/null || true
}
trap cleanup EXIT

# Wait for health
ATTEMPTS=30
until curl -fsS "http://$HOST:$PORT/check/health" >/dev/null || [ $ATTEMPTS -eq 0 ]; do
  ATTEMPTS=$((ATTEMPTS-1))
  sleep 1
  echo "Waiting for app... attempts left: $ATTEMPTS"
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "App process exited unexpectedly:" >&2
    tail -n +1 /tmp/backend_smoke.log || true
    exit 1
  fi
done

# Health check
curl -fsS "http://$HOST:$PORT/check/health" | tee /tmp/health.json

# # <> endpoint
# curl -fsS "http://$HOST:$PORT/api/v1/" | tee /tmp/<>.json

# Basic validations
jq -e '.status_code == 200' </tmp/health.json >/dev/null || { echo "Health endpoint failed" >&2; exit 1; }


echo "Smoke test passed"