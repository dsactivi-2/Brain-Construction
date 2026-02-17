#!/bin/bash
# Nach Bash-Ausfuehrung: Fehler loggen
INPUT=$(cat -)

python3 << PYEOF
import json, sys, os
from datetime import datetime

hook_data = json.loads(r"""$INPUT""")
command = hook_data.get("command", "")
exit_code = hook_data.get("exit_code", 0)

# Bei Fehler: In Fehler-Log speichern
if exit_code != 0:
    log_dir = os.path.expanduser("~/claude-agent-team/brain/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "bash-errors.log")
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] Exit {exit_code}: {command}\n")
    print(f"[FEHLER] Bash-Befehl fehlgeschlagen (Exit {exit_code}): {command[:100]}")
PYEOF
