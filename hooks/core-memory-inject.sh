#!/bin/bash
# Core Memory in den System-Prompt injizieren
CORE_MEM_FILE="$HOME/.claude/core-memory.json"

if [ -f "$CORE_MEM_FILE" ]; then
  echo "=== CORE MEMORY START ==="
  python3 -c "
import json
with open('$CORE_MEM_FILE') as f:
    data = json.load(f)
for key, block in data['blocks'].items():
    content = block.get('content', '')
    if content:
        print(f'[{key}]')
        print(content)
        print(f'[/{key}]')
        print()
"
  echo "=== CORE MEMORY END ==="
else
  echo "[INFO] Kein Core Memory gefunden: $CORE_MEM_FILE"
  echo "[INFO] Erstelle mit: cp ~/claude-agent-team/config/core-memory.json ~/.claude/core-memory.json"
fi
