#!/usr/bin/env bash
set -euo pipefail

DIR=reports
COUNT=${COUNT:-2}

if [ ! -d "$DIR" ]; then
	echo "Reports directory not found: $DIR" >&2
	exit 1
fi

mapfile -t FILES < <(ls -1t "$DIR"/bid_*.md 2>/dev/null | head -n "$COUNT")
if [ "${#FILES[@]}" -lt 2 ]; then
	echo "Need at least two versioned reports to diff." >&2
	exit 1
fi

LEFT=${FILES[1]}
RIGHT=${FILES[0]}
echo -e "Diffing:\nLEFT:  $LEFT\nRIGHT: $RIGHT"

diff -u "$LEFT" "$RIGHT" || true
