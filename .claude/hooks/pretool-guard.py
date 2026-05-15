"""PreToolUse hook - auto-approve safe operations, warn on risky ones"""
import json, sys, os

hook_input = json.loads(sys.stdin.read())
tool_name = hook_input.get("tool_name", "")
tool_input = hook_input.get("tool_input", {})

# Always safe in our project
ALWAYS_ALLOW = {
    "Write": True,
    "Edit": True,
    "Read": True,
    "Glob": True,
    "Grep": True,
    "TodoWrite": True,
    "TaskOutput": True,
    "TaskStop": True,
    "WebSearch": True,
    "WebFetch": True,
    "AskUserQuestion": True,
    "Skill": True,
    "CronCreate": True,
    "CronDelete": True,
    "CronList": True,
    "ScheduleWakeup": True,
}

# Bash: auto-approve safe commands
SAFE_BASH = ["git ", "curl ", "tasklist", "netstat", "dir ", "ls ", "cd ", "cat ",
             "echo ", "mkdir", "npm ", "node ", "pip", "py ", "python", "winget",
             "ffmpeg", "which ", "where ", "time ", "sleep ", "printf", "rm -",
             "cp ", "mv ", "find ", "grep ", "head ", "tail "]

if tool_name in ALWAYS_ALLOW:
    print(json.dumps({
        "continue": True,
        "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}
    }))
elif tool_name == "Bash":
    cmd = tool_input.get("command", "")
    if any(cmd.lstrip().startswith(s) for s in SAFE_BASH):
        print(json.dumps({
            "continue": True,
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}
        }))
    else:
        # Let user decide for non-safe commands
        print(json.dumps({
            "continue": True,
            "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                    "permissionDecisionReason": f"Bash: {cmd[:80]}"}
        }))
else:
    # Unknown tool - let user decide
    print(json.dumps({
        "continue": True,
        "hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask"}
    }))
