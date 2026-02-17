#!/bin/bash
# Benachrichtigung senden (Slack/WhatsApp/Linear)
INPUT=$(cat -)

python3 << PYEOF
import json, sys, os

hook_data = json.loads(r"""$INPUT""")
message = hook_data.get("message", "")
level = hook_data.get("level", "info")

config_file = os.path.expanduser("~/claude-agent-team/config/communication.json")
if not os.path.exists(config_file):
    sys.exit(0)

with open(config_file) as f:
    config = json.load(f)

# Slack Webhook
slack_config = config.get("slack", {})
webhook_url = slack_config.get("webhook_url", "")
if webhook_url and webhook_url.startswith("https://hooks.slack.com/") and "XXX" not in webhook_url:
    import urllib.request
    data = json.dumps({"text": f"[{level.upper()}] {message}"}).encode()
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
        print(f"[NOTIFICATION] Slack: gesendet")
    except Exception as e:
        print(f"[NOTIFICATION] Slack fehlgeschlagen: {e}")

print(f"[NOTIFICATION] {level}: {message[:200]}")
PYEOF
