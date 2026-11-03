#!/usr/bin/env bash
# Open a built single-file presentation in your browser for a human eyeball
# (the manual check that complements the automated verify.py gate).
#
#   ./preview.sh <build.html>
#
# The output is one self-contained .html — file:// works in a real browser, so
# it just opens directly. Set PREVIEW_NO_OPEN=1 to skip launching (used by tests).
set -euo pipefail
T="${1:-site.html}"

opener() {
  if [ -n "${PREVIEW_NO_OPEN:-}" ]; then echo "(would open: $1)"; return; fi
  if command -v open >/dev/null 2>&1; then open "$1"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1"
  else echo "Open this in your browser: $1"; fi
}

if [ -f "$T" ]; then
  echo ">> opening single file: $T"
  opener "$T"
else
  echo "ERROR: not found: $T  (pass the built .html file)"; exit 1
fi
