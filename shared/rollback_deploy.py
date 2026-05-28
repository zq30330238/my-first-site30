#!/usr/bin/env python3
import sys, json, subprocess, time, os, re
from pathlib import Path
from datetime import datetime

ROOT = Path("d:/AI网站文件夹")
CONFIG = ROOT / "shared" / "site_config.json"
HISTORY = ROOT / ".claude" / "deploy_history.json"
ACCOUNT_ID = "4e8cd083c07627f679dd86dc5b488fb0"


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def get_site(site_dir):
    config = load_config()
    for s in config["sites"]:
        if s["dir"] == site_dir:
            return s
    return None


def get_token():
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print("ERROR: CLOUDFLARE_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


def load_history():
    if HISTORY.exists():
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    return {}


def save_history(data):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def wrangler_list(project):
    result = subprocess.run(
        ["npx.cmd", "wrangler", "pages", "deployment", "list",
         "--project-name", project, "--environment", "production", "--json"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"ERROR: wrangler failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def get_local_commit():
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%H"],
            capture_output=True, text=True, timeout=10
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def fetch_live_html(url):
    r = subprocess.run(
        ["curl", "-s", "--max-time", "15", url],
        capture_output=True, text=True, timeout=20
    )
    return r.stdout


def cmd_list():
    site_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not site_dir:
        print("Usage: py rollback_deploy.py list <site_dir>", file=sys.stderr)
        sys.exit(1)

    site = get_site(site_dir)
    if not site:
        print(f"ERROR: {site_dir} not in site_config.json", file=sys.stderr)
        sys.exit(1)

    deployments = wrangler_list(site["cf_project"])
    history = load_history()
    last_good = history.get(site_dir, {}).get("last_good", "")

    print(f"\n  Deployments for {site_dir} ({site['cf_project']}):\n")
    print(f"  {'ID':<24} {'Branch':<12} {'Commit':<10} {'Status'}")
    print(f"  {'-'*22:<24} {'-'*10:<12} {'-'*8:<10} {'-'*30}")

    for d in deployments[:5]:
        marker = "  <-- last_good" if d["Id"] == last_good else ""
        print(f"  {d['Id'][:22]:<24} {d['Branch']:<12} {d['Source'][:8]:<10} {d['Status']}{marker}")

    print()


def cmd_save():
    site_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not site_dir:
        print("Usage: py rollback_deploy.py save <site_dir>", file=sys.stderr)
        sys.exit(1)

    site = get_site(site_dir)
    if not site:
        print(f"ERROR: {site_dir} not in site_config.json", file=sys.stderr)
        sys.exit(1)

    deployments = wrangler_list(site["cf_project"])
    if not deployments:
        print(f"ERROR: no deployments found for {site['cf_project']}", file=sys.stderr)
        sys.exit(1)

    current = deployments[0]
    deploy_id = current["Id"]
    commit = current["Source"]
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    history = load_history()
    if site_dir not in history:
        history[site_dir] = {}

    history[site_dir]["last_good"] = deploy_id
    history[site_dir]["cf_commit"] = commit
    history[site_dir]["local_commit"] = get_local_commit()
    history[site_dir]["timestamp"] = now
    history[site_dir]["status"] = "confirmed"
    save_history(history)

    print(f"Saved {site_dir}: last_good={deploy_id[:18]}.. commit={commit} time={now}")


def cmd_rollback():
    site_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not site_dir:
        print("Usage: py rollback_deploy.py rollback <site_dir>", file=sys.stderr)
        sys.exit(1)

    site = get_site(site_dir)
    if not site:
        print(f"ERROR: {site_dir} not in site_config.json", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    history = load_history()

    if site_dir not in history or "last_good" not in history[site_dir]:
        print(f"ERROR: no saved deployment for {site_dir}. Run 'save' first.", file=sys.stderr)
        sys.exit(1)

    deploy_id = history[site_dir]["last_good"]
    url = (f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}"
           f"/pages/projects/{site['cf_project']}/deployments/{deploy_id}/rollback")

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url,
         "-H", f"Authorization: Bearer {token}"],
        capture_output=True, text=True, timeout=30
    )

    try:
        resp = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: invalid JSON from CF API:\n{result.stdout}", file=sys.stderr)
        sys.exit(1)

    if resp.get("success"):
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        history[site_dir]["last_rollback"] = now
        save_history(history)
        print(f"Rolled back {site_dir} -> deployment {deploy_id[:18]}..")
    elif resp.get("errors"):
        print(f"ERROR: {json.dumps(resp['errors'], indent=2)}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"ERROR: unexpected CF response:\n{result.stdout}", file=sys.stderr)
        sys.exit(1)


def cmd_deploy():
    if len(sys.argv) < 3:
        print("Usage: py rollback_deploy.py deploy <site_dir>", file=sys.stderr)
        sys.exit(1)

    site_dir = sys.argv[2]
    site = get_site(site_dir)
    if not site:
        print(f"ERROR: {site_dir} not in site_config.json", file=sys.stderr)
        sys.exit(1)

    get_token()
    branch = site["production_branch"]

    # Step 1: save current deployment as last_good
    print(f"[1/5] Saving current deployment (pre-deploy) for {site_dir}...")
    cmd_save()

    # Step 2: run wrangler deploy
    print(f"[2/5] Deploying {ROOT / site_dir} -> {site['cf_project']} ({branch})...")
    deploy_result = subprocess.run(
        ["npx.cmd", "wrangler", "pages", "deploy", str(ROOT / site_dir),
         "--project-name", site["cf_project"], "--branch", branch],
        capture_output=True, text=True, timeout=120
    )
    print(deploy_result.stdout)
    if deploy_result.returncode != 0:
        print(f"ERROR: deploy failed:\n{deploy_result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Step 3: wait for CDN propagation
    print(f"[3/5] Waiting 30s for CDN propagation...")
    time.sleep(30)

    # Step 4: verify sync
    print(f"[4/5] Verifying deployment against live site...")
    live_html = fetch_live_html(f"https://{site['domain']}")
    if not live_html or len(live_html) < 100:
        print(f"ERROR: live fetch returned {len(live_html) if live_html else 0} bytes, rolling back...", file=sys.stderr)
        cmd_rollback()
        sys.exit(1)

    local_index = ROOT / site_dir / "index.html"
    local_html = local_index.read_text(encoding="utf-8", errors="ignore")

    local_cards = len(re.findall(r'class="[^"]*article-card[^"]*"', local_html))
    local_selects = len(re.findall(r'<select onchange=', local_html))
    local_ads = 'pagead2.googlesyndication.com' in local_html
    live_cards = len(re.findall(r'class="[^"]*article-card[^"]*"', live_html))
    live_selects = len(re.findall(r'<select onchange=', live_html))
    live_ads = 'pagead2.googlesyndication.com' in live_html

    problems = []
    if local_cards != live_cards:
        problems.append(f"article-cards local={local_cards} live={live_cards}")
    if local_selects != live_selects:
        problems.append(f"footer-selects local={local_selects} live={live_selects}")
    if local_ads != live_ads:
        problems.append(f"AdSense script local={local_ads} live={live_ads}")

    if problems:
        print(f"ERROR: sync mismatch:\n  " + "\n  ".join(problems), file=sys.stderr)
        print(f"[5/5] Rolling back...")
        cmd_rollback()
        sys.exit(1)

    print(f"[5/5] Deployment verified OK for {site_dir}")

    # record deploy state via existing tool
    try:
        subprocess.run(
            ["python", str(ROOT / "shared" / "record_deploy.py"), site_dir],
            capture_output=True, text=True, timeout=10
        )
    except Exception:
        pass


def cmd_help():
    print("CF Pages deployment rollback tool.\n")
    print("Usage:  python rollback_deploy.py <command> [site_dir]\n")
    print("Commands:")
    print("  list <site_dir>       Show recent production deployments (last 5)")
    print("  save <site_dir>       Save current production deployment as last_good")
    print("  rollback <site_dir>   Rollback to last saved good deployment (CF API)")
    print("  deploy <site_dir>     save -> wrangler deploy -> verify -> rollback on fail\n")
    print("Env required:  CLOUDFLARE_API_TOKEN (for rollback and deploy)")
    print("Config source: shared/site_config.json")
    print("State file:    .claude/deploy_history.json")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h", "help"):
        cmd_help()
        sys.exit(0)

    command = sys.argv[1]
    handlers = {
        "list": cmd_list,
        "save": cmd_save,
        "rollback": cmd_rollback,
        "deploy": cmd_deploy,
    }

    if command not in handlers:
        print(f"Unknown command: {command}\n", file=sys.stderr)
        cmd_help()
        sys.exit(1)

    handlers[command]()
