#!/usr/bin/env python3
import json, os, sys

event = json.load(sys.stdin)
state = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()), ".claude", "freeze-dir")
if not os.path.isfile(state):
    sys.exit(0)

allowed = os.path.realpath(open(state).read().strip())
inp = event.get("tool_input", {})
target = inp.get("file_path") or inp.get("notebook_path")
if not target:
    sys.exit(0)

target = os.path.realpath(target)
if target == allowed or target.startswith(allowed + os.sep):
    sys.exit(0)

print(f"Frozen: edits are limited to {allowed}. Run /unfreeze to lift this.", file=sys.stderr)
sys.exit(2)
