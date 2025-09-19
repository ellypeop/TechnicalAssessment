#!/usr/bin/env bash
set -euo pipefail

QUERY=${1:-"From Samsic UK's context, what are key bid management requirements and how do they align with current UK FM market expectations?"}
MAX_RESULTS=${MAX_RESULTS:-8}
LOCAL_MAX_CHUNKS=${LOCAL_MAX_CHUNKS:-3}
OUT=${OUT:-report_samsic_hybrid.md}
shift || true

DOC_ARGS=()
SAMSIC_PATH="data/raw/RFP - Bid Management Systems - Samsic UK.docx"
if [ -f "$SAMSIC_PATH" ]; then
	DOC_ARGS+=("--include-samsic")
else
	DOC_ARGS+=("--no-include-samsic")
fi
# Additional docs via DOCS env var (comma-separated paths)
if [ -n "${DOCS:-}" ]; then
	IFS=',' read -ra ADDOCS <<< "$DOCS"
	for p in "${ADDOCS[@]}"; do
		DOC_ARGS+=("--doc" "$p")
	done
fi

echo "== Research Agent: Hybrid Test (Local DOCX + Web) =="

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
python -m research_agent.cli "${DOC_ARGS[@]}" --max-results "$MAX_RESULTS" --local-max-chunks "$LOCAL_MAX_CHUNKS" --out "$OUT" "$QUERY"

echo "Saved report to $OUT"
