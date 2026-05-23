#!/usr/bin/env python3
"""部署后更新 deploy_state.json 记录"""
import json, sys, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path("d:/AI网站文件夹")
STATE_FILE = ROOT / ".claude" / "deploy_state.json"

def get_latest_commit():
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%H"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"

def record_deploy(site_dir):
    if not STATE_FILE.exists():
        print(f"ERROR: {STATE_FILE} not found")
        return False

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    commit = get_latest_commit()
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if site_dir in state["sites"]:
        state["sites"][site_dir]["last_deploy"] = now
        state["sites"][site_dir]["last_commit"] = commit
        state["last_updated"] = now
        STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Recorded: {site_dir} deployed at {now} (commit {commit[:8]})")
        return True
    else:
        print(f"ERROR: {site_dir} not in deploy_state.json")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py shared/record_deploy.py <site_dir>")
        sys.exit(1)
    record_deploy(sys.argv[1])
