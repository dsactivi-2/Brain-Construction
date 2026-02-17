#!/bin/bash
# Vor Kontext-Kompaktierung: Wichtige Informationen sichern
INPUT=$(cat -)

python3 << PYEOF
import json, sys, os
from datetime import datetime

hook_data = json.loads(r"""$INPUT""")

core_mem_file = os.path.expanduser("~/.claude/core-memory.json")
if os.path.exists(core_mem_file):
    with open(core_mem_file) as f:
        core_mem = json.load(f)

    # Kompaktierungs-Timestamp in AKTUELLE-ARBEIT speichern
    aktuelle_arbeit = core_mem["blocks"].get("AKTUELLE-ARBEIT", {})
    content = aktuelle_arbeit.get("content", "")
    marker = f"\n[Kompaktiert: {datetime.now().strftime('%Y-%m-%d %H:%M')}]"

    if marker not in content:
        aktuelle_arbeit["content"] = (content + marker)[:4000]
        core_mem["blocks"]["AKTUELLE-ARBEIT"] = aktuelle_arbeit
        with open(core_mem_file, "w") as f:
            json.dump(core_mem, f, indent=2, ensure_ascii=False)
        print("[PRE-COMPACT] Aktuelle Arbeit gesichert in Core Memory")

print("[PRE-COMPACT] Kontext wird kompaktiert — Core Memory bleibt erhalten")
PYEOF
