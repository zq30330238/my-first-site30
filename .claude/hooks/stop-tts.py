"""Stop hook - ensure TTS is pushed and services are alive"""
import json, sys, os, urllib.request, socket

# Read hook input
hook_input = json.loads(sys.stdin.read())
transcript_path = hook_input.get("transcript_path", "")

# Read last Claude response from transcript and push to TTS
try:
    with open(transcript_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the last assistant message
    last_text = ""
    for line in reversed(lines[-200:]):  # Check last 200 lines
        try:
            entry = json.loads(line)
            if entry.get("role") == "assistant" and entry.get("content"):
                text = entry["content"]
                if isinstance(text, list):
                    for block in text:
                        if isinstance(block, dict) and block.get("type") == "text":
                            last_text = block.get("text", "")
                elif isinstance(text, str):
                    last_text = text
                if last_text:
                    break
        except (json.JSONDecodeError, KeyError):
            continue

    if last_text:
        # Push to TTS bridge
        data = json.dumps({"text": last_text}).encode()
        req = urllib.request.Request("http://127.0.0.1:9876/response", data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
except Exception:
    pass  # Don't block on TTS failure

print(json.dumps({"continue": True}))
