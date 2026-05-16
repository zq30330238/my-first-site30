"""Stop hook — push TTS + write session handover for next window"""
import json, sys, os, urllib.request, socket, subprocess
from datetime import datetime
from pathlib import Path

hook_input = json.loads(sys.stdin.read())
transcript_path = hook_input.get("transcript_path", "")

# --- TTS push ---
try:
    with open(transcript_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    last_text = ""
    for line in reversed(lines[-200:]):
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
        data = json.dumps({"text": last_text}).encode()
        req = urllib.request.Request("http://127.0.0.1:9876/response", data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
except Exception:
    pass

# --- Session handover ---
try:
    PROJECT = Path(r"d:\AI网站文件夹")
    MEMORY_DIR = Path(os.environ.get("USERPROFILE", "C:/Users/Administrator")) / ".claude/projects/d--AI-----/memory"
    HANDOVER_FILE = MEMORY_DIR / "session_handover.md"

    def _run(cmd, timeout=8):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=str(PROJECT))
            return r.stdout.strip() or r.stderr.strip()
        except:
            return ""

    health = {}
    hf = PROJECT / "shared" / ".health-state.json"
    if hf.exists():
        health = json.loads(hf.read_text(encoding="utf-8"))

    md = f"""# Session Handover — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## State
- SEO: {health.get('seo_score','?')} | Content: {health.get('content_score','?')}
- Dead Links: {health.get('dead_links','?')} | Orphans: {health.get('orphans','?')}
- Sitemap: {health.get('sitemap_issues','?')} issues | Compliance: {health.get('compliance_issues','?')} issues

## Recent Commits
{_run("git log --oneline -5 --format='%h %s'")}

## Uncommitted
{_run("git diff --name-only HEAD") or "none"}
"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    HANDOVER_FILE.write_text(md, encoding="utf-8")
except Exception:
    pass

print(json.dumps({"continue": True}))
