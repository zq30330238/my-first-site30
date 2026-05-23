#!/usr/bin/env python3
"""
Continuous Learning v2 - Observation Hook (Windows-compatible)
Captures PreToolUse/PostToolUse events, detects project context,
and writes observations to ecc-homunculus data directory.
"""

import json, sys, os, re, hashlib, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization|credentials?|auth)"
    r"""(["'\s:=]+)"""
    r"([A-Za-z]+\s+)?"
    r"([A-Za-z0-9_\-/.+=]{8,})"
)
MAX_FILE_SIZE_MB = 10
SIGNAL_EVERY_N = 20
SKIP_PATHS = ["observer-sessions", ".claude-mem"]
SKIP_ENTRYPOINTS = ("cli", "sdk-ts", "claude-desktop")

def resolve_homunculus_dir() -> Path:
    """Data dir: CLV2_HOMUNCULUS_DIR > LOCALAPPDATA/ecc-homunculus > ~/.local/share/ecc-homunculus"""
    override = os.environ.get("CLV2_HOMUNCULUS_DIR")
    if override and os.path.isabs(override):
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "ecc-homunculus"
    return Path.home() / ".local" / "share" / "ecc-homunculus"

def detect_project(data_dir: Path, cwd: str) -> tuple:
    """
    Detect project via git. Returns (project_id, project_name, project_dir).
    Uses git remote URL hash (portable) or local path hash (fallback).
    """
    git_root = None
    if cwd and os.path.isdir(cwd):
        try:
            r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd,
                               capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                git_root = r.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
    if not git_root:
        return "global", "global", data_dir

    project_name = os.path.basename(git_root)
    remote_url = None
    try:
        r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=git_root,
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            remote_url = r.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    hash_input = remote_url or git_root
    project_id = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:12]
    project_dir = data_dir / "projects" / project_id
    return project_id, project_name, project_dir

def update_project_registry(data_dir: Path, pid: str, pname: str, proot: str, premote: str):
    """Update projects.json registry and per-project project.json."""
    registry_file = data_dir / "projects.json"
    project_dir = data_dir / "projects" / pid
    project_dir.mkdir(parents=True, exist_ok=True)

    registry = {}
    if registry_file.exists():
        try:
            with open(registry_file) as f:
                registry = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = registry.get(pid, {})
    metadata = {
        "id": pid, "name": pname, "root": proot, "remote": premote or "",
        "created_at": entry.get("created_at", now), "last_seen": now,
    }
    registry[pid] = metadata

    # Write project.json (per-project metadata)
    try:
        with open(project_dir / "project.json", "w") as f:
            json.dump(metadata, f, indent=2)
    except OSError:
        pass
    # Write registry
    try:
        with open(registry_file, "w") as f:
            json.dump(registry, f, indent=2)
    except OSError:
        pass

def scrub(val):
    if val is None:
        return None
    return SECRET_RE.sub(lambda m: m.group(1) + m.group(2) + (m.group(3) or "") + "[REDACTED]", str(val))

def main():
    # ── Phase detection ──
    hook_phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if not hook_phase:
        ev = os.environ.get("CLAUDE_HOOK_EVENT_NAME", "").lower()
        hook_phase = "pre" if ev in ("pretooluse", "pre") else "post"

    # ── Read stdin ──
    raw = sys.stdin.read().strip()
    if not raw:
        return

    # ── Guards ──
    ep = os.environ.get("CLAUDE_CODE_ENTRYPOINT", "cli")
    if ep not in SKIP_ENTRYPOINTS:
        return
    if os.environ.get("ECC_HOOK_PROFILE") == "minimal":
        return
    if os.environ.get("ECC_SKIP_OBSERVE") == "1":
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return

    if data.get("agent_id"):
        return

    cwd = data.get("cwd", "")
    if cwd:
        for p in SKIP_PATHS:
            if p in cwd:
                return

    # ── Resolve dirs ──
    data_dir = resolve_homunculus_dir()
    if (data_dir / "disabled").exists():
        return

    # ── Project detection ──
    pid, pname, pdir = detect_project(data_dir, cwd)
    pdir.mkdir(parents=True, exist_ok=True)
    for sub in ("instincts/personal", "instincts/inherited", "observations.archive",
                "evolved/skills", "evolved/commands", "evolved/agents"):
        (pdir / sub).mkdir(parents=True, exist_ok=True)

    # Update registry
    project_root = ""
    if pid != "global":
        try:
            project_root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                cwd=cwd, capture_output=True, text=True, timeout=5).stdout.strip()
        except:
            pass
        remote_url = ""
        try:
            remote_url = subprocess.run(["git", "remote", "get-url", "origin"],
                cwd=cwd, capture_output=True, text=True, timeout=5).stdout.strip()
        except:
            pass
        update_project_registry(data_dir, pid, pname, project_root, remote_url)

    # ── Parse event ──
    event = "tool_start" if hook_phase == "pre" else "tool_complete"
    tool_name = data.get("tool_name", data.get("tool", "unknown"))
    tool_input = data.get("tool_input", data.get("input", {}))
    tool_output = data.get("tool_response", data.get("tool_output", data.get("output", "")))
    session_id = data.get("session_id", "unknown")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    obs = {
        "timestamp": timestamp, "event": event, "tool": tool_name,
        "session": session_id, "project_id": pid, "project_name": pname,
    }

    if event == "tool_start":
        inp = json.dumps(tool_input)[:5000] if isinstance(tool_input, dict) else str(tool_input)[:5000]
        obs["input"] = scrub(inp)
    elif tool_output is not None:
        out = json.dumps(tool_output)[:5000] if isinstance(tool_output, dict) else str(tool_output)[:5000]
        obs["output"] = scrub(out)

    # ── Write observation ──
    obs_file = pdir / "observations.jsonl"

    # Rotate if >10MB
    if obs_file.exists() and obs_file.stat().st_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        archive_dir = pdir / "observations.archive"
        archive_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        obs_file.rename(archive_dir / f"observations-{ts}.jsonl")

    with open(obs_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(obs) + "\n")

    # ── Purge old archives (once daily) ──
    purge_marker = pdir / ".last-purge"
    try:
        should_purge = not purge_marker.exists()
        if not should_purge:
            mtime = datetime.fromtimestamp(purge_marker.stat().st_mtime)
            if (datetime.now() - mtime).days >= 1:
                should_purge = True
        if should_purge:
            archive_dir = pdir / "observations.archive"
            if archive_dir.exists():
                cutoff = datetime.now().timestamp() - 30 * 86400
                for f in archive_dir.glob("observations-*.jsonl"):
                    try:
                        if f.stat().st_mtime < cutoff:
                            f.unlink()
                    except OSError:
                        pass
            purge_marker.touch()
    except OSError:
        pass

    # ── Signal counter (for background observer) ──
    counter_file = pdir / ".observer-signal-counter"
    activity_file = pdir / ".observer-last-activity"
    try:
        activity_file.touch()
        counter = 0
        if counter_file.exists():
            try:
                counter = int(counter_file.read_text().strip() or "0")
            except (ValueError, OSError):
                pass
        counter += 1
        if counter >= SIGNAL_EVERY_N:
            counter = 0
            # Signal observer via pid file (if running)
            for pid_file in (pdir / ".observer.pid", data_dir / ".observer.pid"):
                if pid_file.exists():
                    try:
                        import signal
                        observer_pid = int(pid_file.read_text().strip())
                        if observer_pid > 1:
                            os.kill(observer_pid, signal.SIGUSR1)
                    except (ValueError, OSError, ImportError, ProcessLookupError):
                        try:
                            pid_file.unlink()
                        except OSError:
                            pass
        counter_file.write_text(str(counter))
    except OSError:
        pass

if __name__ == "__main__":
    main()
