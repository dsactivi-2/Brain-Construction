#!/bin/bash
# Session-Start: System-Init + Warm-Up Bundle laden
# Wird bei jedem neuen Session-Start ausgefuehrt

BRAIN_DIR="$HOME/claude-agent-team/brain"

# Pruefen ob Brain-System verfuegbar ist
if [ ! -d "$BRAIN_DIR" ]; then
  echo "[WARNUNG] Brain-Verzeichnis nicht gefunden: $BRAIN_DIR"
  echo "[INFO] System startet im Degraded Mode — nur Core Memory verfuegbar"
  exit 0
fi

# Warm-Up Bundle laden (letzte Entscheidungen, offene Tasks, aktiver Kontext)
python3 << 'PYEOF'
import json, os

brain_dir = os.path.expanduser("~/claude-agent-team/brain")

warmup_file = os.path.join(brain_dir, "warmup_bundle.json")
if os.path.exists(warmup_file):
    with open(warmup_file) as f:
        bundle = json.load(f)
    print("=== WARM-UP BUNDLE ===")
    if bundle.get("last_decisions"):
        print("Letzte Entscheidungen:")
        for d in bundle["last_decisions"][-5:]:
            print(f"  - {d}")
    if bundle.get("open_tasks"):
        print("Offene Tasks:")
        for t in bundle["open_tasks"]:
            print(f"  - [{t.get('status', '?')}] {t.get('title', '?')}")
    if bundle.get("active_context"):
        print(f"Aktiver Kontext: {bundle['active_context']}")
    print("=== ENDE WARM-UP ===")
PYEOF
