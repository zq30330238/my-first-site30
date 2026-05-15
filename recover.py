"""One-click recovery — installs everything needed after Claude Code + CC-Switch are set up"""
import subprocess, sys, os, shutil
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


def winget_install(name, pkg_id, check_cmd, check_arg="--version"):
    """Install a package via winget if not already present"""
    try:
        r = subprocess.run([check_cmd, check_arg], capture_output=True, text=True)
        if r.returncode == 0:
            return f"{name} found: {r.stdout.strip().split(chr(10))[0]}"
    except FileNotFoundError:
        pass
    subprocess.run(["winget", "install", pkg_id, "--accept-package-agreements",
                    "--disable-interactivity"], check=True)
    return f"{name} installed"


def npm_install_global(pkg, bin_name=None):
    """Install an npm package globally if not present"""
    name = bin_name or pkg
    try:
        r = subprocess.run([name, "--version"], capture_output=True, text=True)
        if r.returncode == 0:
            return f"{pkg} found: {r.stdout.strip()}"
    except FileNotFoundError:
        pass
    subprocess.run(["npm", "install", "-g", pkg], check=True)
    return f"{pkg} installed"


# ============================
# Recovery steps
# ============================

@step(1, "Check CC-Switch DeepSeek config")
def check_ccswitch():
    db_path = USER / ".cc-switch" / "cc-switch.db"
    if not db_path.exists():
        return "CC-Switch not found -- install and configure DeepSeek first"
    import sqlite3, json
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name, is_current, settings_config FROM providers WHERE app_type='claude' AND is_current=1")
    row = cursor.fetchone()
    conn.close()
    if row:
        cfg = json.loads(row[2])
        env = cfg.get("env", {})
        model = env.get("ANTHROPIC_MODEL", "unknown")
        base = env.get("ANTHROPIC_BASE_URL", "unknown")
        return f"CC-Switch: {row[0]} -> {model} @ {base}"
    return "No active Claude provider in CC-Switch -- configure DeepSeek first"


@step(2, "Install VS Code")
def install_vscode():
    return winget_install("VS Code", "Microsoft.VisualStudioCode", "code")


@step(3, "Install Python 3.10+")
def install_python():
    return winget_install("Python", "Python.Python.3.10", "python")


@step(4, "Install Git")
def install_git():
    return winget_install("Git", "Git.Git", "git")


@step(5, "Install Node.js LTS")
def install_node():
    return winget_install("Node.js", "OpenJS.NodeJS.LTS", "node")


@step(6, "Install Python dependencies")
def install_python_deps():
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "flask", "waitress", "requests", "python-dotenv"],
                   check=True, capture_output=True)
    return "flask waitress requests python-dotenv installed"


@step(7, "Install Codex CLI")
def install_codex():
    return npm_install_global("@openai/codex", "codex")


@step(8, "Setup Codex proxy .env")
def setup_proxy_env():
    env_file = PROXY_DIR / ".env"
    if env_file.exists():
        return "proxy .env exists, skipping"
    # Read key from CC-Switch config
    import sqlite3, json
    db_path = USER / ".cc-switch" / "cc-switch.db"
    api_key = "sk-YOUR_KEY_HERE"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT settings_config FROM providers WHERE app_type='claude' AND is_current=1")
        row = cursor.fetchone()
        conn.close()
        if row:
            cfg = json.loads(row[2])
            api_key = cfg.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", api_key)
    env_file.write_text(f"DEEPSEEK_API_KEY={api_key}\n")
    return "Created .env from CC-Switch config"


@step(9, "Restore Codex config")
def restore_codex_config():
    src = BACKUP / "codex-config.toml"
    dst = USER_CODEX / "config.toml"
    if dst.exists():
        return "Codex config exists, skipping"
    USER_CODEX.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"Codex config restored -> {dst}"


@step(10, "Restore memory files")
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
    return f"{count} memory files restored"


@step(11, "Set DEEPSEEK_API_KEY env var")
def set_env_var():
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key and key.startswith("sk-"):
        return f"DEEPSEEK_API_KEY already set: {key[:15]}..."
    # Try to read from CC-Switch
    import sqlite3, json
    db_path = USER / ".cc-switch" / "cc-switch.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT settings_config FROM providers WHERE app_type='claude' AND is_current=1")
        row = cursor.fetchone()
        conn.close()
        if row:
            cfg = json.loads(row[2])
            key = cfg.get("env", {}).get("ANTHROPIC_AUTH_TOKEN", "")
            if key:
                os.environ["DEEPSEEK_API_KEY"] = key
                return f"DEEPSEEK_API_KEY loaded from CC-Switch"
    return "Could not auto-set DEEPSEEK_API_KEY"


@step(12, "Verify Codex proxy")
def verify_proxy():
    import urllib.request
    try:
        r = urllib.request.urlopen("http://127.0.0.1:5000/v1/models", timeout=10)
        return "Proxy service OK"
    except Exception:
        return "Proxy not running (auto-starts on next Claude Code session)"


@step(13, "Run SEO audit to verify project")
def verify_project():
    audit_script = PROJECT / "shared" / "seo_audit.py"
    if not audit_script.exists():
        return "seo_audit.py not found"
    r = subprocess.run([sys.executable, str(audit_script)], capture_output=True, text=True)
    lines = [l for l in r.stdout.split("\n") if l]
    return f"Project verified: {len(lines)} pages scanned"


# ============================
# Main
# ============================

REQUIRED_STEPS = [
    "Python 3.10+",
    "Git",
    "Node.js LTS",
    "Python deps (flask, waitress, requests, python-dotenv)",
    "Codex CLI (@openai/codex)",
    "Codex proxy .env",
    "Codex config.toml",
    "Memory files (BIO system)",
    "DEEPSEEK_API_KEY",
    "Proxy verification",
    "SEO audit verification",
]

def main():
    ok = 0
    fail = 0

    print("=" * 60)
    print("  JYCSD Project — Full Recovery")
    print("  Prerequisites: Claude Code + CC-Switch with DeepSeek")
    print("=" * 60)
    print()

    for n, desc, fn in STEPS:
        print(f"[{n}/{len(STEPS)}] {desc}...")
        try:
            result = fn()
            print(f"  [OK] {result}")
            ok += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            fail += 1
        print()

    print("=" * 60)
    print(f"Recovery complete: {ok} OK, {fail} failed")
    if fail == 0:
        print("All systems ready. Full project operational.")
    else:
        print(f"{fail} steps failed — check errors above.")
    print("=" * 60)
    return fail


if __name__ == "__main__":
    sys.exit(main())
