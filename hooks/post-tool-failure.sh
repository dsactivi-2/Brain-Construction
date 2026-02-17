#!/bin/bash
# Tool-Fehler tracken
INPUT=$(cat -)

python3 << PYEOF
import json, sys, os
from datetime import datetime

hook_data = json.loads(r"""$INPUT""")
tool_name = hook_data.get("tool_name", "unknown")
error = hook_data.get("error", "unknown")

log_dir = os.path.expanduser("~/claude-agent-team/brain/logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "tool-failures.log")

with open(log_file, "a") as f:
    f.write(f"[{datetime.now().isoformat()}] {tool_name}: {error}\n")

print(f"[FEHLER] Tool '{tool_name}' fehlgeschlagen: {str(error)[:200]}")
PYEOF
