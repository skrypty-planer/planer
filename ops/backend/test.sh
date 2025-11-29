#!/usr/bin/env bash
set -euo pipefail


SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKEND_DIR=$(cd "$SCRIPT_DIR/../../backend" && pwd)
PROJECT_ROOT=$(cd "$BACKEND_DIR/.." && pwd)
cd "$PROJECT_ROOT"

if ! command -v pip >/dev/null 2>&1; then
  echo "pip not found. Please ensure Python is installed." >&2
  exit 1
fi

pip install --upgrade pip >/dev/null
pip install -r "$BACKEND_DIR/requirements.txt"

export PYTHONPATH="$PROJECT_ROOT"
echo "PYTHONPATH set to $PYTHONPATH"
pytest $PYTHONPATH/backend/tests