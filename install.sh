#!/usr/bin/env bash
set -eu

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "RoadRunner developer install"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .

echo "Install complete. Run: source .venv/bin/activate"
echo "Then test: vehicleagent --simulator --samples 5 --print-json"
