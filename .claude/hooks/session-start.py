"""SessionStart hook — start daemons + load session handover if available"""
import subprocess, socket, sys, json, os
from pathlib import Path

PROJECT = r"d:\AI网站文件夹\skills\voice-chat"
CODEX_PROXY_DIR = r"d:\AI网站文件夹\.claude\codex-proxy"
SERVICES = {
    "server.py": ("9876", f'cd "{PROJECT}" && py server.py'),
    "vosk_server.py": ("9877", f'cd "{PROJECT}" && py vosk_server.py'),
    "codex_proxy.py": ("5000", f'cd "{CODEX_PROXY_DIR}" && py codex_proxy.py'),
}


def port_alive(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("127.0.0.1", int(port)))
        s.close()
        return True
    except Exception:
        return False


for name, (port, cmd) in SERVICES.items():
    if not port_alive(port):
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# Load session handover from previous window
extra_context = "Daemon services checked. TTS bridge:9876, Vosk:9877, Codex proxy:5000."
handover_file = Path(os.environ.get("USERPROFILE", "C:/Users/Administrator")) / ".claude/projects/d--AI-----/memory/session_handover.md"
if handover_file.exists():
    try:
        content = handover_file.read_text(encoding="utf-8")
        # Truncate to avoid flooding context (keep first 60 lines)
        lines = content.strip().split("\n")
        if len(lines) > 60:
            lines = lines[:60]
            lines.append("... (truncated, full file in memory/session_handover.md)")
        handover = "\n".join(lines)
        extra_context += f"\n\n=== PREVIOUS SESSION HANDOVER ===\n{handover}\n=== END HANDOVER ==="
    except:
        pass

print(json.dumps({
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": extra_context
    }
}))
