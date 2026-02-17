#!/bin/bash
# Auto-Capture: Neue Fakten aus Konversation extrahieren + speichern (S2)
INPUT=$(cat -)
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys
sys.path.insert(0, "$BRAIN_DIR")

try:
    from auto_memory.capture import extract_and_store
except ImportError:
    # Brain-Module noch nicht implementiert — stille Degradation
    sys.exit(0)

hook_data = json.loads(r"""$INPUT""")
conversation = hook_data.get("conversation", "")

if not conversation:
    sys.exit(0)

new_memories = extract_and_store(
    conversation=conversation,
    extract_types=["fakt", "entscheidung", "praeferenz", "fehler", "todo"],
    dedup=True
)

if new_memories:
    for mem in new_memories:
        print(f"[GESPEICHERT] [{mem['scope']}] {mem['type']}: {mem['text']}")
PYEOF
