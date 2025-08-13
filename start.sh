#!/usr/bin/env bash
set -euo pipefail

# Start script for Olympedia Athlete Scraper
# - Creates/uses a local virtualenv
# - Installs dependencies
# - Runs the CLI entrypoint (scraper.py)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PY=python3
VENV_DIR=".venv"
REQ_FILE="requirements.txt"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "python3 not found on PATH" >&2
  exit 1
fi

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  "$PY" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Install dependencies (idempotent)
if [ -f "$REQ_FILE" ]; then
  pip install -r "$REQ_FILE"
fi

# If arguments are provided, forward them directly to scraper.py.
# Otherwise, use environment-backed defaults.
if [ "$#" -gt 0 ]; then
  exec "$PY" scraper.py "$@"
else
  CONCURRENCY="${CONCURRENCY:-10}"
  DELAY="${DELAY:-0.4}"
  START="${START:-1}"
  CSV="${CSV:-athletes.csv}"
  RESUME_FLAG=()
  if [ "${RESUME:-0}" = "1" ]; then
    RESUME_FLAG=(--resume)
  fi
  exec "$PY" scraper.py \
    --start "$START" \
    --concurrency "$CONCURRENCY" \
    --delay "$DELAY" \
    --csv "$CSV" \
    "${RESUME_FLAG[@]}"
fi
