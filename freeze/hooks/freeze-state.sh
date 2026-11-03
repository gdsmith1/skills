#!/usr/bin/env bash
set -euo pipefail
state="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/freeze-dir"
case "${1:-}" in
  set) mkdir -p "$(dirname "$state")"; printf '%s\n' "$2" > "$state"; echo "frozen to $2" ;;
  clear) if [ -f "$state" ]; then echo "unfrozen (was $(cat "$state"))"; rm "$state"; else echo "nothing was frozen"; fi ;;
  *) echo "usage: freeze-state.sh set <dir> | clear" >&2; exit 2 ;;
esac
