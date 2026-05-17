"""PreToolUse hook - always allow, permission control via settings.local.json"""
import json, sys

hook_input = json.loads(sys.stdin.read())

# All permission decisions are handled by settings.local.json allowlist.
# This hook is informational only — no blocking, no popups.
print(json.dumps({
    "continue": True,
    "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}
}))
