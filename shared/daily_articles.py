"""Daily article generator — ALL 22 sites every run.

Three-phase pipeline per run:
  Phase 1: 3 priority sites (rightsdaily, dailymedadvice, fortnite) — must pass
  Phase 2: Remaining 10 content sites (batch of 4, 10s sleep between batches)
  Phase 3: Remaining 9 game/anime sites (batch of 3, 10s sleep between batches)
"""
import json
import random
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "daily_articles_state.json"
CF_TOKEN_ENV = "CLOUDFLARE_API_TOKEN"

# ── 13 content sites (article-based, use create_articles.py) ──
SITES = [
    "main-site",
    "sub-healthy", "sub-pets", "sub-home", "sub-finance",
    "sub-tech", "sub-travel", "sub-auto", "sub-moto",
    "sub-food", "rightsdaily", "dailymedadvice", "entertainment",
]

# ── 10 game/anime wiki sites (blog-based, use create_game_blog.py) ──
GAME_SITES = [
    "naruto-site", "onepiece-site", "dragonball-site",
    "lol-site", "fortnite-site", "valorant-site",
    "eldenring-site", "minecraft-site", "anime-site", "games-site",
]

# ── 4 priority sites submitted to Google — must pass every run ──
PRIORITY_SITES = ["rightsdaily", "dailymedadvice", "fortnite-site", "main-site"]

# CF Pages project name mappings
CF_PROJECTS = {
    # Content sites
    "main-site": "main-site",
    "sub-healthy": "healthy-jycsd",
    "sub-pets": "pets-jycsd",
    "sub-home": "home-jycsd",
    "sub-finance": "finance-jycsd",
    "sub-tech": "tech-jycsd",
    "sub-travel": "travel-jycsd",
    "sub-auto": "auto-jycsd",
    "sub-moto": "moto-jycsd",
    "sub-food": "food-jycsd",
    "rightsdaily": "rightsdaily",
    "dailymedadvice": "dailymedadvice",
    "entertainment": "entertainment-jycsd",
    # Game/anime sites
    "naruto-site": "naruto-jycsd",
    "onepiece-site": "onepiece-jycsd",
    "dragonball-site": "dragonball-jycsd",
    "lol-site": "lol-jycsd",
    "fortnite-site": "fortnite-jycsd",
    "valorant-site": "valorant-jycsd",
    "eldenring-site": "eldenring-jycsd",
    "minecraft-site": "minecraft-jycsd",
    "anime-site": "anime-jycsd",
    "games-site": "games-jycsd",
}

CONTENT_BATCH_SIZE = 4
GAME_BATCH_SIZE = 3
BATCH_SLEEP_SEC = 10


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run": None, "total_generated": 0}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def generate_content_article(site, template=None):
    """Generate 1 article for a content site via create_articles.py."""
    print(f"\n--- Generating article for {site} ---")
    cmd = [sys.executable, "shared/create_articles.py", "--sites", site, "--per-site", "1", "--skip-audit"]
    if template:
        cmd.extend(["--template", template])
    proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1, encoding='utf-8', errors='replace')
    for line in proc.stdout:
        print(line, end='', flush=True)
    proc.wait()
    if proc.returncode != 0:
        print(f"FAILED: {site} returned code {proc.returncode}")
        return False
    return True


def generate_game_blog(site):
    """Generate 1 blog post for a game/anime site via create_game_blog.py."""
    print(f"\n--- Generating blog for {site} ---")
    cmd = [sys.executable, "shared/create_game_blog.py", "--sites", site, "--per-site", "1"]
    proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1, encoding='utf-8', errors='replace')
    for line in proc.stdout:
        print(line, end='', flush=True)
    proc.wait()
    if proc.returncode != 0:
        print(f"FAILED: {site} returned code {proc.returncode}")
        return False
    return True


def deploy_site(site):
    """Deploy a modified site to CF Pages."""
    project = CF_PROJECTS.get(site)
    if not project:
        print(f"  No CF project mapping for {site}, skipping deploy")
        return False
    print(f"\n--- Deploying {site} -> {project} ---")
    result = subprocess.run(
        f'npx.cmd wrangler pages deploy {site} --project-name {project} --commit-dirty=true',
        cwd=str(ROOT), capture_output=True, timeout=120, shell=True,
    )
    stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
    stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
    # Strip non-ASCII for Windows GBK console
    ascii_out = stdout.encode('ascii', errors='replace').decode('ascii')
    print(ascii_out)
    if stderr:
        print(f"STDERR: {stderr.encode('ascii', errors='replace').decode('ascii')}")
    return result.returncode == 0


def _generate(site, template):
    """Route site to correct generator (content article or game blog)."""
    if site in GAME_SITES:
        return generate_game_blog(site)
    return generate_content_article(site, template)


def _run_batch(sites, template, results):
    """Run generate + deploy for a list of sites, populating results dict."""
    for site in sites:
        ok = _generate(site, template)
        if ok:
            if deploy_site(site):
                results[site] = True
            else:
                print(f"  Deploy FAILED for {site}")
                results[site] = False
        else:
            results[site] = False


def main():
    print(f"=== Daily Articles — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    print(f"Content sites: {len(SITES)}, Game/anime sites: {len(GAME_SITES)}")
    print(f"Priority (must-pass): {PRIORITY_SITES}")

    state = load_state()
    today = datetime.now().strftime("%Y-%m-%d")

    force_template = random.choice(["A", "B", "C", "D", "E"])
    print(f"Template for this round: {force_template}")

    results = {}  # site -> bool

    # ── Phase 1: Priority sites (must pass, run first) ──
    print(f"\n{'='*60}")
    print(f"PHASE 1 [PRIORITY]: {' / '.join(PRIORITY_SITES)}")
    print(f"{'='*60}")
    for site in PRIORITY_SITES:
        print(f"\n[PRIORITY] {site}")
        _run_batch([site], force_template, results)

    # ── Phase 2: Remaining content sites (batches of 4) ──
    remaining_content = [s for s in SITES if s not in PRIORITY_SITES]
    content_batches = [remaining_content[i:i + CONTENT_BATCH_SIZE]
                       for i in range(0, len(remaining_content), CONTENT_BATCH_SIZE)]
    print(f"\n{'='*60}")
    print(f"PHASE 2: Content sites — {len(remaining_content)} remaining, "
          f"{len(content_batches)} batches")
    print(f"{'='*60}")
    for batch_idx, batch in enumerate(content_batches):
        print(f"\n--- Content batch {batch_idx + 1}/{len(content_batches)}: {batch} ---")
        _run_batch(batch, force_template, results)
        if batch_idx < len(content_batches) - 1:
            print(f"\nSleeping {BATCH_SLEEP_SEC}s before next batch...")
            time.sleep(BATCH_SLEEP_SEC)

    # ── Phase 3: Remaining game sites (batches of 3) ──
    remaining_game = [s for s in GAME_SITES if s not in PRIORITY_SITES]
    game_batches = [remaining_game[i:i + GAME_BATCH_SIZE]
                    for i in range(0, len(remaining_game), GAME_BATCH_SIZE)]
    print(f"\n{'='*60}")
    print(f"PHASE 3: Game/anime sites — {len(remaining_game)} remaining, "
          f"{len(game_batches)} batches")
    print(f"{'='*60}")
    for batch_idx, batch in enumerate(game_batches):
        print(f"\n--- Game batch {batch_idx + 1}/{len(game_batches)}: {batch} ---")
        _run_batch(batch, force_template, results)
        if batch_idx < len(game_batches) - 1:
            print(f"\nSleeping {BATCH_SLEEP_SEC}s before next batch...")
            time.sleep(BATCH_SLEEP_SEC)

    # ── Summary Report ──
    total = len(SITES) + len(GAME_SITES)
    content_ok = sum(1 for s in SITES if results.get(s))
    game_ok = sum(1 for s in GAME_SITES if results.get(s))

    priority_ok = all(results.get(s) for s in PRIORITY_SITES)
    priority_marks = []
    for s in PRIORITY_SITES:
        status = f"{s}={'OK' if results.get(s) else 'FAIL'}"
        if not results.get(s):
            status += " [X]"
        priority_marks.append(status)
    priority_str = ", ".join(priority_marks)

    content_fails = [s for s in SITES if not results.get(s)]
    game_fails = [s for s in GAME_SITES if not results.get(s)]
    all_fails = content_fails + game_fails

    print(f"\n{'='*60}")
    print(f"=== DAILY REPORT {today} ===")
    print(f"Priority sites: {priority_str}")
    print(f"Content sites: {content_ok}/{len(SITES)} OK"
          + (f" ({', '.join(content_fails)} FAIL)" if content_fails else ""))
    print(f"Game/Anime blogs: {game_ok}/{len(GAME_SITES)} OK"
          + (f" ({', '.join(game_fails)} FAIL)" if game_fails else ""))
    if all_fails:
        print(f"Total: {content_ok + game_ok}/{total} — {len(all_fails)} FAILED")
    else:
        print(f"Total: {content_ok + game_ok}/{total} — ALL CLEAR")
    print(f"{'='*60}")

    # Save state
    state["last_run"] = today
    state["total_generated"] = state.get("total_generated", 0) + content_ok + game_ok
    save_state(state)

    # Return code 1 if any priority site failed, otherwise reflect all failures
    if not priority_ok:
        return 1
    return 0 if len(all_fails) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
