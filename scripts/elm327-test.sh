#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-/dev/rfcomm0}"
BAUD="${2:-38400}"
DB="${3:-data/pathfinder.sqlite3}"
SAMPLES="${SAMPLES:-10}"

python3 -m vehicleagent \
  --elm327-port "$PORT" \
  --elm327-baud "$BAUD" \
  --samples "$SAMPLES" \
  --print-json \
  --db "$DB" \
  --verbose
