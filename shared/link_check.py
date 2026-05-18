"""Link checker — find dead internal links, directory links, semantic mismatches across all 17 sites"""
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
ALL_SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel", "main-site",
    "minecraft-site", "eldenring-site", "lol-site", "fortnite-site", "valorant-site",
    "games-site", "anime-site", "dragonball-site", "onepiece-site", "naruto-site"]

SITE_DOMAINS = {
    "sub-pets": "pets.jycsd.com", "sub-healthy": "healthy.jycsd.com", "sub-home": "home.jycsd.com",
    "sub-finance": "finance.jycsd.com", "sub-tech": "tech.jycsd.com", "sub-travel": "travel.jycsd.com",
    "main-site": "jycsd.com", "minecraft-site": "minecraft.jycsd.com", "eldenring-site": "eldenring.jycsd.com",
    "lol-site": "lol.jycsd.com", "fortnite-site": "fortnite.jycsd.com", "valorant-site": "valorant.jycsd.com",
    "games-site": "games.jycsd.com", "anime-site": "anime.jycsd.com", "dragonball-site": "dragonball.jycsd.com",
    "onepiece-site": "onepiece.jycsd.com", "naruto-site": "naruto.jycsd.com",
}

STOP_WORDS = {'the', 'a', 'an', 'in', 'on', 'to', 'for', 'of', 'and', 'or', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should',
    'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these', 'those', 'it', 'its'}

SKIP_LINK_TEXTS = {'about', 'contact', 'privacy', 'policy', 'home', 'terms', 'categories', 'guides',
    'read more', 'learn more', 'view all', 'back to home', 'subscribe', 'follow us',
    'share', 'tweet', 'pin', 'email', 'print', 'previous', 'next', 'see all',
    'explore more', 'discover more', 'get started', 'click here', 'here', 'more',
    'all articles', 'latest posts', 'popular posts', 'related posts', 'hot topics'}

DEAD_LINKS = []
SEMANTIC_WARNINGS = []
ORPHAN_PAGES = []


def extract_keywords(text):
    words = re.findall(r'[a-z]{3,}', text.lower())
    return {w for w in words if w not in STOP_WORDS}


def resolve_target(href, file_dir):
    """Resolve an href to an absolute Path. Returns (target, is_directory)."""
    if href.startswith('/'):
        target = file_dir / href.lstrip('/')
    else:
        target = file_dir / href
    if href.endswith('/'):
        return target / 'index.html', True
    return target, False


def check():
    all_pages = set()
    for d in ALL_SITES:
        site_dir = ROOT / d
        if not site_dir.exists():
            continue
        for f in site_dir.glob('*.html'):
            all_pages.add(f'{d}/{f.name}')

    orphan_candidates = defaultdict(int)

    for d in ALL_SITES:
        site_dir = ROOT / d
        if not site_dir.exists():
            continue

        for f in sorted(site_dir.glob('*.html')):
            try:
                html = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue

            file_dir = f.parent
            label = f'{d}/{f.name}'
            is_article = f.name.startswith('article-')

            # --- Extract all hrefs ---
            hrefs = re.findall(r'href="([^"]+)"', html)
            for href in hrefs:
                if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue

                # Cross-site links
                if href.startswith('http'):
                    for site_dir_key, domain in SITE_DOMAINS.items():
                        if domain in href:
                            rel_path = href.split(domain, 1)[1]
                            if rel_path and not rel_path.startswith('//'):
                                target = ROOT / site_dir_key / rel_path.lstrip('/')
                                if not target.exists():
                                    if rel_path.endswith('/') and (target / 'index.html').exists():
                                        pass
                                    else:
                                        DEAD_LINKS.append(f'  {label} -> {href} (cross-site, missing: {target.relative_to(ROOT)})')
                            break
                    continue

                # Internal links
                target, is_dir = resolve_target(href, file_dir)
                if not target.exists():
                    if is_dir:
                        DEAD_LINKS.append(f'  {label} -> {href} (directory, index.html not found)')
                    elif '.' in target.name:
                        DEAD_LINKS.append(f'  {label} -> {href} (file not found: {target.relative_to(ROOT)})')

                # Track orphan candidates
                if target.suffix == '.html' and not href.startswith('http'):
                    orphan_key = str(target.relative_to(ROOT)).replace('\\', '/')
                    orphan_candidates[orphan_key] += 1

            # --- Semantic matching (article pages only) ---
            if is_article:
                a_tags = re.findall(r'<a\s[^>]*?href="([^"]+)"[^>]*?>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
                for href, raw_text in a_tags:
                    link_text = re.sub(r'<[^>]+>', '', raw_text).strip().lower()
                    link_text = re.sub(r'[^a-z\s]', '', link_text).strip()
                    if len(link_text) < 3 or link_text in SKIP_LINK_TEXTS:
                        continue
                    if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('http'):
                        continue

                    target, _ = resolve_target(href, file_dir)
                    if not target.exists() or target.suffix != '.html':
                        continue
                    try:
                        target_html = target.read_text(encoding='utf-8', errors='ignore')
                    except Exception:
                        continue
                    title_m = re.search(r'<title>(.*?)</title>', target_html)
                    h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', target_html)
                    title_h1 = (title_m.group(1) if title_m else '') + ' ' + (h1_m.group(1) if h1_m else '')

                    link_kw = extract_keywords(link_text)
                    target_kw = extract_keywords(title_h1)
                    if not link_kw:
                        continue
                    if not (link_kw & target_kw):
                        SEMANTIC_WARNINGS.append(
                            f'  {label}: "{link_text[:60]}" -> {href} (title: "{title_h1.strip()[:80]}")')


    # --- Find orphan pages ---
    for d in ALL_SITES:
        site_dir = ROOT / d
        if not site_dir.exists():
            continue
        for f in site_dir.glob('*.html'):
            key = f'{d}/{f.name}'
            if orphan_candidates[key] == 0:
                ORPHAN_PAGES.append(f'  {key} (no other page links to it)')

    return all_pages


if __name__ == '__main__':
    all_pages = check()

    total_errors = len(DEAD_LINKS)
    total_warnings = len(SEMANTIC_WARNINGS)
    total_orphans = len(ORPHAN_PAGES)

    if DEAD_LINKS:
        print(f'=== DEAD LINKS ({total_errors}) ===')
        for dl in DEAD_LINKS:
            print(dl)
    else:
        print('No dead links found.')

    if SEMANTIC_WARNINGS:
        print(f'\n=== SEMANTIC WARNINGS ({total_warnings}) ===')
        for sw in SEMANTIC_WARNINGS:
            print(sw)

    if ORPHAN_PAGES:
        print(f'\n=== ORPHAN PAGES ({total_orphans}) ===')
        for op in ORPHAN_PAGES:
            print(op)

    print(f'\nScanned {len(all_pages)} pages across {len([s for s in ALL_SITES if (ROOT/s).exists()])} sites.')
    print(f'Dead links: {total_errors}  Semantic warnings: {total_warnings}  Orphans: {total_orphans}')

    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)
