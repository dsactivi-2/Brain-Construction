#!/bin/bash
# Auto-Recall: Relevante Erinnerungen vor Antwort suchen (S2)
INPUT=$(cat -)
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys, os
sys.path.insert(0, "$BRAIN_DIR")

try:
    from auto_memory.recall import search_memories
except ImportError:
    # Brain-Module noch nicht implementiert — stille Degradation
    sys.exit(0)

hook_data = json.loads(r"""$INPUT""")
prompt = hook_data.get("prompt", "")

if not prompt:
    sys.exit(0)

results = search_memories(
    query=prompt,
    scopes=["session", "user", "projekt", "global"],
    top_k=10,
    min_score=0.6
)

if results:
    print("=== ERINNERUNGEN (AUTO-RECALL) ===")
    for mem in results:
        print(f"[{mem['scope']}] {mem['text']} (Score: {mem['score']:.2f})")
    print("=== ENDE ERINNERUNGEN ===")
PYEOF
