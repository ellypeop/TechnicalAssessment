#!/usr/bin/env bash
set -euo pipefail

QUERY=${1:-"What services does Samsic UK provide and what are key considerations in bid management for UK FM providers?"}
MAX_RESULTS=${MAX_RESULTS:-8}
LOCAL_MAX_CHUNKS=${LOCAL_MAX_CHUNKS:-0}
OUT=${OUT:-report_samsic_web.md}

echo "== Research Agent: Web Lookup Test (Samsic UK) =="

if ! command -v python >/dev/null 2>&1; then
	echo "Python is required but not found in PATH." >&2
	exit 1
fi

if [ ! -d .venv ]; then
	echo "Creating virtual environment..."
	python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt >/dev/null

if [ ! -f .env ]; then
	echo ".env not found. Create a .env with OPENAI_API_KEY before running." >&2
fi

echo "Running research for query: $QUERY"
python -m research_agent.cli --no-include-samsic --max-results "$MAX_RESULTS" --local-max-chunks "$LOCAL_MAX_CHUNKS" --out "$OUT" "$QUERY"

echo "Saved report to $OUT"
