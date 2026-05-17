#!/usr/bin/env bash
# Validate a DESIGN.md against the canonical Google spec linter.
#
# Usage:
#   ./lint.sh path/to/DESIGN.md
#
# Exit codes:
#   0  — file passes (errors == 0). Warnings may still be present.
#   1  — lint failures present.
#   2  — npx unavailable or runtime error.
#
# The linter is installed on demand via `npx @google/design.md`. First
# run downloads ~5 MB; subsequent runs are cached.

set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" ]]; then
  echo "Usage: $0 <DESIGN.md>" >&2
  exit 2
fi

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 2
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found. Install Node.js (https://nodejs.org) to run the linter." >&2
  exit 2
fi

# Default registry diagnostic — print only on failure so the happy path stays quiet.
run_lint() {
  npx --yes "@google/design.md" lint "$FILE"
}

if ! OUTPUT="$(run_lint 2>&1)"; then
  echo "$OUTPUT"
  if grep -qi "ENOVERSIONS" <<<"$OUTPUT"; then
    echo "" >&2
    echo "Hint: npm couldn't find @google/design.md. Check your registry:" >&2
    echo "      npm config get registry   # expect https://registry.npmjs.org/" >&2
  fi
  exit 1
fi

echo "$OUTPUT"
