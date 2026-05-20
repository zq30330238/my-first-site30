"""
Daily article generator for 6 sub-sites.
Picks 2 sites per run (rotation), generates 1 article each, deploys.
Cron: 0 6 * * *
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "daily_articles_state.json"
CF_TOKEN_ENV = "CLOUDFLARE_API_TOKEN"

# All 6 sub-sites in rotation order
SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel"]

# CF Pages project names
CF_PROJECTS = {
    "sub-healthy": "healthy-jycsd",
    "sub-pets": "pets-jycsd",
    "sub-home": "home-jycsd",
    "sub-finance": "finance-jycsd",
    "sub-tech": "tech-jycsd",
    "sub-travel": "travel-jycsd",
}


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_index": 0, "last_date": None}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def pick_sites(state):
    """Pick 2 sites, rotating through the list."""
    # Reset if we've gone through all sites
    if state["last_index"] >= len(SITES):
        state["last_index"] = 0

    idx = state["last_index"]
    # Pick 2 sites starting from idx, wrapping around
    picks = []
    for i in range(2):
        picks.append(SITES[(idx + i) % len(SITES)])

    state["last_index"] = (idx + 2) % len(SITES)
    state["last_date"] = datetime.now().strftime("%Y-%m-%d")
    return picks


def generate_article(site):
    """Generate 1 article for a site using create_articles.py."""
    print(f"\n--- Generating article for {site} ---")
    result = subprocess.run(
        [sys.executable, "shared/create_articles.py", "--sites", site, "--per-site", "1"],
        cwd=str(ROOT),
        capture_output=True, text=True, timeout=600
    )
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"FAILED: {site} returned code {result.returncode}")
        return False
    return True


def deploy_site(site):
    """Deploy a modified site to CF Pages."""
    project = CF_PROJECTS[site]
    print(f"\n--- Deploying {site} → {project} ---")
    result = subprocess.run(
        ["npx", "wrangler", "pages", "deploy", site, "--project-name", project, "--commit-dirty=true"],
        cwd=str(ROOT),
        capture_output=True, text=True, timeout=120
    )
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    return result.returncode == 0


def main():
    print(f"=== Daily Articles — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")

    state = load_state()
    picks = pick_sites(state)
    print(f"Selected: {picks}")

    success_count = 0
    fail_count = 0

    for site in picks:
        ok = generate_article(site)
        if ok:
            # Deploy each successfully generated site
            dep_ok = deploy_site(site)
            if dep_ok:
                success_count += 1
            else:
                print(f"Deploy failed for {site}")
                fail_count += 1
        else:
            fail_count += 1

    # Save state regardless (to keep rotation moving)
    save_state(state)

    print(f"\n=== Done: {success_count} success, {fail_count} failed ===")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
