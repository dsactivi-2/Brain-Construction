#!/bin/bash
# Nach Write/Edit: Pruefen ob Secrets eingefuegt wurden
INPUT=$(cat -)

python3 << PYEOF
import json, sys, re

hook_data = json.loads(r"""$INPUT""")
file_path = hook_data.get("file_path", "")
content = hook_data.get("content", "")

# Secret-Patterns pruefen
secret_patterns = [
    (r'(?:api[_-]?key|apikey)\s*[:=]\s*["\x27][A-Za-z0-9]{20,}', "API Key"),
    (r'(?:password|passwd|pwd)\s*[:=]\s*["\x27][^\s]{8,}', "Passwort"),
    (r'(?:secret|token)\s*[:=]\s*["\x27][A-Za-z0-9]{20,}', "Secret/Token"),
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "Private Key"),
    (r'sk-[A-Za-z0-9]{20,}', "OpenAI API Key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub Token"),
]

for pattern, label in secret_patterns:
    if re.search(pattern, str(content), re.IGNORECASE):
        print(f"[WARNUNG] Moegliches Secret gefunden: {label} in {file_path}")
        print("[AKTION] Bitte Secret entfernen und in .env oder Vault speichern!")
PYEOF
