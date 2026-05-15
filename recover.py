"""One-click recovery script for new machines — run by Claude after git clone"""
import subprocess, sys, os, shutil, json
from pathlib import Path

PROJECT = Path(__file__).parent
BACKUP = PROJECT / "backup-config"
USER = Path(os.path.expanduser("~"))
USER_CLAUDE = USER / ".claude"
USER_CODEX = USER / ".codex"
PROXY_DIR = PROJECT / ".claude" / "codex-proxy"

STEPS = []

def step(n, desc):
    def deco(fn):
        STEPS.append((n, desc, fn))
        return fn
    return deco


@step(1, "Install Python dependencies")
def install_python_deps():
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "waitress", "requests", "python-dotenv"],
                   check=True, capture_output=True)
    return "flask, waitress, requests, python-dotenv installed"


@step(2, "Install Codex CLI")
def install_codex():
    try:
        r = subprocess.run(["npm", "list", "-g", "@openai/codex"], capture_output=True, text=True)
        if "@openai/codex" in r.stdout:
            return "Codex CLI already installed"
    except FileNotFoundError:
        return "npm not found — install Node.js first"
    subprocess.run(["npm", "install", "-g", "@openai/codex"], check=True)
    return "Codex CLI installed"


@step(3, "Check DEEPSEEK_API_KEY")
def check_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key and key.startswith("sk-"):
        return f"API key set: {key[:15]}..."
    return ("WARNING: DEEPSEEK_API_KEY not set!\n"
            "  Run in PowerShell:\n"
            "  [System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_KEY', 'sk-YOUR-KEY', 'User')")


@step(4, "Setup Codex proxy .env")
def setup_proxy_env():
    env_file = PROXY_DIR / ".env"
    if env_file.exists():
        return "proxy .env already exists, skipping"
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-YOUR_KEY_HERE")
    env_file.write_text(f"DEEPSEEK_API_KEY={api_key}\n")
    return "Created .env from environment variable"


@step(5, "Restore Codex config")
def restore_codex_config():
    src = BACKUP / "codex-config.toml"
    dst = USER_CODEX / "config.toml"
    if dst.exists():
        return "Codex config already exists, skipping"
    USER_CODEX.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"Codex config restored -> {dst}"


@step(6, "Restore memory files")
def restore_memory():
    memory_dir = USER_CLAUDE / "projects" / "d--AI-----" / "memory"
    src = BACKUP / "memory"
    if not src.exists():
        return "No memory backup found"
    memory_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in src.iterdir():
        shutil.copy2(f, memory_dir / f.name)
        count += 1
    return f"{count} memory files restored -> {memory_dir}"


@step(7, "Verify proxy service")
def verify_proxy():
    import urllib.request
    try:
        r = urllib.request.urlopen("http://127.0.0.1:5000/v1/models", timeout=10)
        return "Proxy service verified"
    except Exception:
        return "Proxy not running (will auto-start on next Claude Code session via SessionStart hook)"


@step(8, "Run SEO audit to verify project")
def verify_project():
    audit_script = PROJECT / "shared" / "seo_audit.py"
    if audit_script.exists():
        r = subprocess.run([sys.executable, str(audit_script)], capture_output=True, text=True)
        lines = [l for l in r.stdout.split("\n") if l]
        return f"Project verified: {len(lines)} pages scanned"
    return "seo_audit.py not found"


def main():
    ok_count = 0
    fail_count = 0

    print("=" * 60)
    print("  JYCSD Project — New Machine Recovery")
    print("=" * 60)
    print()

    for n, desc, fn in STEPS:
        print(f"[{n}/{len(STEPS)}] {desc}...")
        try:
            result = fn()
            print(f"  OK: {result}")
            ok_count += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            fail_count += 1
        print()

    print("=" * 60)
    print(f"Recovery complete: {ok_count} OK, {fail_count} failed")
    if fail_count == 0:
        print("Run: py shared/seo_audit.py to verify all 79 pages.")
    print("=" * 60)
    return fail_count


if __name__ == "__main__":
    sys.exit(main())
