#!/bin/bash
# Subagent-Start: Kontext fuer neuen Subagent vorbereiten
INPUT=$(cat -)

python3 << PYEOF
import json, sys, os

hook_data = json.loads(r"""$INPUT""")
agent_type = hook_data.get("agent_type", "unknown")

# Agent-Profil laden falls verfuegbar
profiles_dir = os.path.expanduser("~/claude-agent-team/agents")
profile_map = {
    "berater": "berater",
    "architekt": "architekt",
    "coder": "coder",
    "tester": "tester",
    "reviewer": "reviewer",
    "designer": "designer",
    "analyst": "analyst",
    "doc-scanner": "doc-scanner",
    "devops": "devops",
    "dokumentierer": "dokumentierer",
}

profile_name = profile_map.get(agent_type.lower(), "")
if profile_name:
    profile_path = os.path.join(profiles_dir, profile_name, "CLAUDE.md")
    if os.path.exists(profile_path):
        with open(profile_path) as f:
            print(f.read())

print(f"[SUBAGENT] Typ: {agent_type} gestartet")
PYEOF
