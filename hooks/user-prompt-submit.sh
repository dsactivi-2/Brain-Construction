#!/bin/bash
# User-Prompt validieren — Sicherheits-Check
INPUT=$(cat -)

python3 << PYEOF
import json, sys

hook_data = json.loads(r"""$INPUT""")
prompt = hook_data.get("prompt", "")

# Sicherheits-Check: Gefaehrliche Patterns erkennen
dangerous_patterns = [
    "rm -rf /",
    "DROP TABLE",
    "DROP DATABASE",
    "DELETE FROM",
    "--no-verify",
    "force push",
    "force-push",
]

for pattern in dangerous_patterns:
    if pattern.lower() in prompt.lower():
        print(f"[WARNUNG] Gefaehrliches Pattern erkannt: '{pattern}'")
        print("[INFO] Bitte bestaetigen Sie diese Aktion explizit.")
PYEOF
