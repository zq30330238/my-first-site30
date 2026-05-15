"""SessionStart hook - auto-start daemon services if not already running"""
import subprocess, socket, sys, json, os

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

# Output context for Claude
print(json.dumps({
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "Daemon services checked. TTS bridge:9876, Vosk:9877, Codex proxy:5000."
    }
}))
