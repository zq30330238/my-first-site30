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
import re

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
    return {"last_run": None, "total_generated": 0, "failed_verifications": 0, "duplicates_skipped": 0}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def generate_content_article(site, template=None):
    """Generate 1 article for a content site via create_articles.py."""
    print(f"\n--- Generating article for {site} ---")
    cmd = [sys.executable, "shared/create_articles.py", "--sites", site, "--per-site", "1"]
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


def get_existing_titles(site):
    """Get all existing article titles for a site, excluding the latest file."""
    site_dir = ROOT / site
    titles = set()
    html_files = sorted(site_dir.glob("article-*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    for f in html_files[1:]:
        html = f.read_text(encoding='utf-8', errors='replace')
        m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        if m:
            titles.add(m.group(1).strip())
    return titles


def verify_latest_article(site):
    """Verify the latest generated article. Returns 'ok', 'duplicate', or 'fail'."""
    site_dir = ROOT / site
    html_files = sorted(site_dir.glob("article-*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not html_files:
        print(f"  [VERIFY FAIL] {site}: no article files found")
        return "fail"
    latest = html_files[0]
    html = latest.read_text(encoding='utf-8', errors='replace')

    # Check 4 essential HTML structure tags
    for tag, msg in [('</head>', 'missing </head>'), ('<body', 'missing <body'),
                     ('</body>', 'missing </body>'), ('</html>', 'missing </html>')]:
        if tag not in html:
            print(f"  [VERIFY FAIL] {latest.name}: {msg}")
            return "fail"

    # Check at least 1 img tag
    if '<img' not in html:
        print(f"  [VERIFY FAIL] {latest.name}: no image tag")
        return "fail"

    # Check no duplicate adsbygoogle
    ads_count = html.count('adsbygoogle.js')
    if ads_count > 1:
        print(f"  [VERIFY FAIL] {latest.name}: {ads_count} adsbygoogle scripts (should be 1)")
        return "fail"

    # Check for duplicate title
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if m:
        new_title = m.group(1).strip()
        existing = get_existing_titles(site)
        if new_title in existing:
            print(f"  [DUPLICATE] {latest.name}: title already exists: \"{new_title[:60]}\"")
            latest.unlink()
            print(f"  Deleted {latest.name} (duplicate)")
            return "duplicate"

    # Also scan for blog-*.html files on game sites
    blog_files = sorted(site_dir.glob("blog-*.html"), key=lambda f: f.stat().st_mtime, reverse=True)
    if blog_files:
        blog = blog_files[0]
        bhtml = blog.read_text(encoding='utf-8', errors='replace')
        for tag, _ in [('</head>',), ('<body',), ('</body>',), ('</html>',)]:
            if tag not in bhtml:
                print(f"  [VERIFY FAIL] {blog.name}: missing {tag}")
                return "fail"
        if '<img' not in bhtml:
            print(f"  [VERIFY FAIL] {blog.name}: no image tag")
            return "fail"
        ads_count = bhtml.count('adsbygoogle.js')
        if ads_count > 1:
            print(f"  [VERIFY FAIL] {blog.name}: {ads_count} adsbygoogle scripts")
            return "fail"

    return "ok"


def update_sitemap(site):
    """Regenerate sitemap.xml with all current pages."""
    site_dir = ROOT / site
    sitemap_path = site_dir / 'sitemap.xml'

    domain_map = {
        'main-site': 'https://jycsd.com',
        'sub-healthy': 'https://healthy.jycsd.com',
        'sub-pets': 'https://pets.jycsd.com',
        'sub-home': 'https://home.jycsd.com',
        'sub-finance': 'https://finance.jycsd.com',
        'sub-tech': 'https://tech.jycsd.com',
        'sub-travel': 'https://travel.jycsd.com',
        'sub-auto': 'https://auto.jycsd.com',
        'sub-moto': 'https://moto.jycsd.com',
        'sub-food': 'https://food.jycsd.com',
        'rightsdaily': 'https://rightsdaily.com',
        'dailymedadvice': 'https://dailymedadvice.com',
        'entertainment': 'https://entertainment.jycsd.com',
        'naruto-site': 'https://naruto.jycsd.com',
        'onepiece-site': 'https://onepiece.jycsd.com',
        'dragonball-site': 'https://dragonball.jycsd.com',
        'lol-site': 'https://lol.jycsd.com',
        'fortnite-site': 'https://fortnite.jycsd.com',
        'valorant-site': 'https://valorant.jycsd.com',
        'eldenring-site': 'https://eldenring.jycsd.com',
        'minecraft-site': 'https://minecraft.jycsd.com',
        'anime-site': 'https://anime.jycsd.com',
        'games-site': 'https://games.jycsd.com',
        'clothing-site': 'https://clothing.jycsd.com',
        'chinese-architecture-site': 'https://chinese-architecture.jycsd.com',
        'western-architecture-site': 'https://global-architecture.jycsd.com',
    }

    domain = domain_map.get(site)
    if not domain:
        print(f"  [SITEMAP WARN] No domain mapping for {site}")
        return False

    # Collect ALL HTML files recursively, strip .html for CF Pages clean URLs
    urls = []
    for f in sorted(site_dir.rglob("*.html")):
        rel = str(f.relative_to(site_dir)).replace('\\', '/')
        if rel == 'index.html':
            urls.append(f'{domain}/')
        elif rel.endswith('/index.html'):
            urls.append(f'{domain}/{rel[:-11]}/')
        else:
            urls.append(f'{domain}/{rel[:-5]}')

    if not urls:
        print(f"  [SITEMAP WARN] No pages found for {site}")
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in sorted(set(urls)):
        xml += f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    xml += '</urlset>\n'

    sitemap_path.write_text(xml, encoding='utf-8')
    print(f"  Sitemap updated: {len(set(urls))} URLs for {site}")
    return True


def _generate(site, template):
    """Route site to correct generator (content article or game blog)."""
    if site in GAME_SITES:
        return generate_game_blog(site)
    return generate_content_article(site, template)


def _run_batch(sites, template, results, state):
    """Run generate + verify + sitemap + deploy for a list of sites."""
    for site in sites:
        ok = _generate(site, template)
        if not ok:
            results[site] = False
            continue

        # Verify the latest generated article
        verify_result = verify_latest_article(site)
        if verify_result == "duplicate":
            state["duplicates_skipped"] = state.get("duplicates_skipped", 0) + 1
            results[site] = False
            continue
        if verify_result != "ok":
            state["failed_verifications"] = state.get("failed_verifications", 0) + 1
            results[site] = False
            continue

        # Update sitemap before deploy
        update_sitemap(site)

        # Deploy
        if deploy_site(site):
            results[site] = True
        else:
            print(f"  Deploy FAILED for {site}")
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
        _run_batch([site], force_template, results, state)

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
        _run_batch(batch, force_template, results, state)
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
        _run_batch(batch, force_template, results, state)
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
    failed_ver = state.get("failed_verifications", 0)
    dups_skip = state.get("duplicates_skipped", 0)
    if failed_ver or dups_skip:
        print(f"Verification fails: {failed_ver}, Duplicates skipped: {dups_skip}")
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
