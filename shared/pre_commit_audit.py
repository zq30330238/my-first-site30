"""Pre-commit audit: comprehensive quality checks before push.

Catches everything a human visitor would notice:
  - Fake/broken images (Unsplash IDs, dead domains)
  - Wrong email domains (QQ, 163, etc.)
  - Placeholder text (Article N, Lorem ipsum, etc.)
  - AI cliche phrases
  - Emoji in content
  - Ad slot integrity
  - SEO fundamentals
  - Content quality signals
  - Index page health

Usage: py shared/pre_commit_audit.py [--full] [--site X]
  --full   Scan ALL files, not just modified ones
  --site X  Scan only one site directory
"""

import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALL_SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel", "main-site",
    "minecraft-site", "eldenring-site", "lol-site", "fortnite-site", "valorant-site",
    "games-site", "anime-site", "dragonball-site", "onepiece-site", "naruto-site"]
SITES_WITH_ARTICLES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel",
    "minecraft-site", "eldenring-site", "lol-site", "fortnite-site", "valorant-site",
    "dragonball-site", "onepiece-site", "naruto-site"]
GAME_SITES = {"minecraft-site", "eldenring-site", "lol-site", "fortnite-site", "valorant-site",
    "games-site", "anime-site", "dragonball-site", "onepiece-site", "naruto-site"}

# === Image checks ===
UNSPLASH_FAKE_RE = re.compile(r'images\.unsplash\.com/photo-(\d{1,9})\?')
DEAD_IMAGE_DOMAINS = ["source.unsplash.com", "unsplash.com/source", "picsum.photos", "lorempixel.com", "placeholder.com", "via.placeholder.com"]
LOCAL_IMAGE_RE = re.compile(r'src=["\']\.\.?/[^"\']+\.(png|jpg|jpeg|gif|webp)["\']')
MISSING_ALT_RE = re.compile(r'<img(?![^>]*alt=)[^>]*>')

# === Email checks ===
BANNED_EMAIL_DOMAINS = ["qq.com", "163.com", "126.com", "sina.com", "sina.com.cn", "sohu.com", "yahoo.com.cn", "foxmail.com"]
REQUIRED_EMAIL = "zq30330238@gmail.com"
EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')

# === Placeholder text ===
PLACEHOLDER_PATTERNS = [
    (r'>Article \d{1,2}</p>', "Article N placeholder in sidebar"),
    (r'>Article \d{1,2}<', "Article N placeholder"),
    (r'>Lorem ipsum', "Lorem ipsum placeholder"),
    (r'>Sample [Tt]ext', "Sample text placeholder"),
    (r'>TODO[< ]', "TODO placeholder"),
    (r'>Test [Aa]rticle', "Test article placeholder"),
    (r'>Placeholder', "Placeholder text"),
    (r'>\[TBD\]', "TBD placeholder"),
    (r'>Coming [Ss]oon', "Coming soon placeholder"),
]

# === AI cliches (US consumer audience hates these) ===
AI_CLICHES = [
    "delve into",
    "in the ever-evolving landscape",
    "in today's digital age",
    "in today's fast-paced world",
    "unlock your potential",
    "game-changer",
    "revolutionize",
    "cutting-edge",
    "state-of-the-art",
    "unleash the power",
    "elevate your",
    "take your ___ to the next level",
    "in this comprehensive guide",
    "it's no secret that",
    "without further ado",
]

# === Emoji ===
EMOJI_RE = re.compile(
    r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251'
    r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF'
    r'\U00002600-\U000026FF\U0000FE00-\U0000FE0F]'
)

VALID_SLOTS = {
    "9112825459", "4397738132", "9739511410",
    "6968613870", "6470642127", "4688206363",
    "1349134522", "2825867721", "4302601082",
    "3024072332", "4500805691", "5977539078",
    "8480024131", "9956757497", "1433490869",
    "4107333609", "5584066966", "7060800328",
}
BAD_SLOTS = {"6452093175", "7928829977", "9405566373"}

SITE_DOMAINS = {
    "sub-pets": "pets.jycsd.com",
    "sub-healthy": "healthy.jycsd.com",
    "sub-home": "home.jycsd.com",
    "sub-finance": "finance.jycsd.com",
    "sub-tech": "tech.jycsd.com",
    "sub-travel": "travel.jycsd.com",
    "main-site": "jycsd.com",
    "minecraft-site": "minecraft.jycsd.com",
    "eldenring-site": "eldenring.jycsd.com",
    "lol-site": "lol.jycsd.com",
    "fortnite-site": "fortnite.jycsd.com",
    "valorant-site": "valorant.jycsd.com",
    "games-site": "games.jycsd.com",
    "anime-site": "anime.jycsd.com",
    "dragonball-site": "dragonball.jycsd.com",
    "onepiece-site": "onepiece.jycsd.com",
    "naruto-site": "naruto.jycsd.com",
    "anime-site": "anime.jycsd.com",
}

STOP_WORDS = {'the', 'a', 'an', 'in', 'on', 'to', 'for', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these', 'those', 'it', 'its'}
UTILITY_PAGES = {'about', 'contact', 'cookie-policy', 'privacy-policy', 'terms', 'category-meal-plans', 'category-nutrition', 'category-recipes', 'category-cats', 'category-dogs', 'category-small-pets', 'category-gardening', 'category-interior', 'category-diy', 'category-budgeting', 'category-investing', 'category-credit', 'category-ai', 'category-guides', 'category-reviews', 'category-security', 'category-budget-travel', 'category-destinations', 'category-digital-nomad', 'category-tips', 'category-home', 'category-tech'}
SKIP_LINK_TEXTS = {'about', 'contact', 'privacy', 'policy', 'home', 'terms', 'categories', 'guides',
    'read more', 'learn more', 'view all', 'back to home', 'subscribe', 'follow us',
    'share', 'tweet', 'pin', 'email', 'print', 'previous', 'next', 'see all',
    'explore more', 'discover more', 'get started', 'click here', 'here', 'more',
    'all articles', 'latest posts', 'popular posts', 'related posts', 'hot topics'}

def extract_keywords(text):
    words = re.findall(r'[a-z]{3,}', text.lower())
    return {w for w in words if w not in STOP_WORDS}

errors = []
warnings = []


def label(filepath):
    return f"{filepath.parent.name}/{filepath.name}"


def is_utility_page(filepath):
    """Utility pages don't need ad slots or blockquotes."""
    stem = filepath.stem
    if stem in UTILITY_PAGES:
        return True
    if stem.startswith('category-'):
        return True
    if '-site/' in str(filepath) and stem in ('about', 'contact', 'cookie-policy', 'privacy-policy', 'terms'):
        return True
    return False


def check_article(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    utility = is_utility_page(filepath)

    # === IMAGE CHECKS ===
    # 1a. Fake Unsplash IDs (short numeric, AI-generated)
    for m in UNSPLASH_FAKE_RE.finditer(html):
        fid = m.group(1)
        if len(fid) <= 9:
            errors.append(f"{name}: fake Unsplash photo ID 'photo-{fid}' (AI hallucination, image 404s)")

    # 1b. Dead image domains
    for domain in DEAD_IMAGE_DOMAINS:
        if domain in html:
            errors.append(f"{name}: dead image domain: {domain}")

    # 1c. Local image references (won't work on CDN)
    for m in LOCAL_IMAGE_RE.finditer(html):
        errors.append(f"{name}: local image reference: {m.group(0)[:80]}")

    # 1d. Images missing alt text
    missing_alts = len(MISSING_ALT_RE.findall(html))
    if missing_alts > 0:
        warnings.append(f"{name}: {missing_alts} img tag(s) missing alt attribute")

    # === EMAIL CHECKS ===
    for m in EMAIL_RE.finditer(html):
        email = m.group(0)
        domain = email.split("@")[1]
        if domain in BANNED_EMAIL_DOMAINS:
            errors.append(f"{name}: banned email domain ({email}) — use {REQUIRED_EMAIL}")
        elif domain == "gmail.com" and email != REQUIRED_EMAIL:
            warnings.append(f"{name}: unexpected Gmail address: {email}")

    # === PLACEHOLDER TEXT ===
    for pattern, desc in PLACEHOLDER_PATTERNS:
        if re.search(pattern, html):
            errors.append(f"{name}: {desc}")

    # === AI CLICHES ===
    for cliche in AI_CLICHES:
        if cliche.lower() in html.lower():
            warnings.append(f"{name}: AI cliche — '{cliche}'")

    # === EMOJI ===
    emoji_count = len(EMOJI_RE.findall(html))
    if emoji_count > 0:
        errors.append(f"{name}: {emoji_count} emoji found (banned per project style)")

    # === FORM FUNCTIONALITY ===
    forms = re.findall(r'<form[^>]*>', html)
    for form_html in forms:
        has_onsubmit = 'onsubmit=' in form_html
        has_action = 'action=' in form_html
        has_prevent_default = 'event.preventDefault()' in form_html
        has_real_handler = has_onsubmit and not has_prevent_default

        if has_prevent_default and 'mailto:' not in form_html:
            # preventDefault with no real behavior (only flag if no mailto fallback)
            if 'alert(' not in form_html or 'This is a static' in form_html:
                errors.append(f"{name}: dead form — event.preventDefault() without real handler")

        if not has_onsubmit and not has_action:
            errors.append(f"{name}: form has no onsubmit or action — clicking submit reloads page")

    # === DEAD LINKS ===
    dead_links = re.findall(r'href="#"', html)
    if dead_links:
        errors.append(f"{name}: {len(dead_links)} dead link(s) with href=\"#\"")

    # === REAL LINK VALIDATION ===
    hrefs = re.findall(r'href="([^"]+)"', html)
    file_dir = filepath.parent
    for href in hrefs:
        if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        if href.startswith('http'):
            for site_dir_key, domain in sorted(SITE_DOMAINS.items(), key=lambda x: -len(x[1])):
                if domain in href:
                    rel_path = href.split(domain, 1)[1]
                    if rel_path and not rel_path.startswith('//'):
                        target = ROOT / site_dir_key / rel_path.lstrip('/')
                        if not target.exists():
                            if rel_path.endswith('/') and (target / 'index.html').exists():
                                pass
                            else:
                                errors.append(f"{name}: cross-site broken link: {href} (file missing: {target.relative_to(ROOT)})")
                    break
            continue
        if href.startswith('/'):
            target = site_dir / href.lstrip('/')
        else:
            target = file_dir / href
        if href.endswith('/'):
            index_target = target / 'index.html'
            if not index_target.exists():
                errors.append(f"{name}: directory link broken: {href} → {index_target.relative_to(ROOT)} (index.html not found)")
        elif not target.exists() and '.' in target.name:
            errors.append(f"{name}: broken internal link: {href} → {target.relative_to(ROOT)} (file not found)")

    # === SEMANTIC LINK MATCHING (article pages only, WARNING not ERROR) ===
    a_tags = re.findall(r'<a\s[^>]*?href="([^"]+)"[^>]*?>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
    for href, raw_text in a_tags:
        link_text = re.sub(r'<[^>]+>', '', raw_text).strip().lower()
        link_text = re.sub(r'[^a-z\s]', '', link_text).strip()
        if len(link_text) < 3:
            continue
        if link_text in SKIP_LINK_TEXTS:
            continue
        if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('http'):
            continue
        if href.startswith('/'):
            target = site_dir / href.lstrip('/')
        else:
            target = file_dir / href
        if href.endswith('/'):
            target = target / 'index.html'
        if not target.exists() or not target.suffix == '.html':
            continue
        try:
            target_html = target.read_text(encoding="utf-8", errors="ignore")
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
            warnings.append(f"{name}: semantic mismatch — \"{link_text[:60]}\" links to {href} (title: \"{title_h1.strip()[:80]}\")")

    # === AD SLOTS ===
    slots = re.findall(r'data-ad-slot="(\d+)"', html)
    bad = [s for s in slots if s in BAD_SLOTS]
    if bad:
        errors.append(f"{name}: BAD ad slots: {bad}")
    # Game/anime sites use render_game_site.py with Auto Ads only, no manual ad slots
    is_game_site = site_dir.name in GAME_SITES

    if not is_game_site:
        if not utility and len(slots) not in (3, 4):
            errors.append(f"{name}: expected 3-4 ad slots, found {len(slots)}")
    for s in slots:
        if s not in VALID_SLOTS and s not in BAD_SLOTS:
            warnings.append(f"{name}: unknown ad slot: {s}")

    # Ad block integrity
    if not is_game_site:
        ad_push = len(re.findall(r'\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\)', html))
        if not utility and ad_push != len(slots):
            errors.append(f"{name}: {len(slots)} ad units but {ad_push} push scripts (mismatch)")

    # Auto Ads script — check for ALL sites including game sites
    if not utility and 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' not in html:
        errors.append(f"{name}: missing Auto Ads script")

    # === SEO META (skip for utility pages)
    if not utility:
        meta_checks = {
            "google-adsense-account": 'google-adsense-account',
            "description": 'name="description"',
            "og:title": 'property="og:title"',
            "og:description": 'property="og:description"',
        }
        for meta_key, pattern in meta_checks.items():
            if pattern not in html:
                errors.append(f"{name}: missing meta tag: {meta_key}")

        if 'rel="canonical"' not in html:
            errors.append(f"{name}: missing canonical URL")

    # === CONTENT QUALITY ===
    # Word count
    article_div = re.search(r'class="[^"]*article-content[^"]*"[^>]*>', html)
    if article_div:
        pos = article_div.end()
        depth = 1
        while depth > 0:
            next_open = html.find('<div', pos)
            next_close = html.find('</div>', pos)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 4
            else:
                depth -= 1
                if depth == 0:
                    inner = html[article_div.end():next_close]
                    text = re.sub(r'<[^>]+>', ' ', inner)
                    text = re.sub(r'\s+', ' ', text).strip()
                    wc = len(text.split())
                    if wc < 800:
                        warnings.append(f"{name}: low word count: {wc} (min 800)")
                    elif wc > 3000:
                        warnings.append(f"{name}: very high word count: {wc}")
                pos = next_close + 6

    # Title length
    title_m = re.search(r'<title>(.*?)</title>', html)
    if title_m:
        title_text = title_m.group(1)
        if len(title_text) < 30:
            warnings.append(f"{name}: title too short: {len(title_text)} chars")
        elif len(title_text) > 70:
            warnings.append(f"{name}: title too long: {len(title_text)} chars (keep under 70)")

    # Description length
    desc_m = re.search(r'content="([^"]+)"', html)
    if desc_m:
        desc_text = desc_m.group(1)
        if len(desc_text) > 160:
            warnings.append(f"{name}: meta description too long: {len(desc_text)} chars (keep under 160)")

    # Multiple h1
    h1_count = len(re.findall(r'<h1[ >]', html))
    if h1_count > 1:
        errors.append(f"{name}: {h1_count} h1 tags (should be exactly 1)")

    # === JSON-LD VALIDATION ===
    jsonld_m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if jsonld_m:
        try:
            json.loads(jsonld_m.group(1))
        except json.JSONDecodeError:
            errors.append(f"{name}: invalid JSON-LD schema")

    # === DOMAIN CHECK (skip utility pages)
    if not utility:
        site_dir = filepath.parent.name
        expected_domain = SITE_DOMAINS.get(site_dir)
        if expected_domain and expected_domain not in html:
            errors.append(f"{name}: expected domain '{expected_domain}' not found in HTML")

    # === BLOCKQUOTE CHECK ===
    if not utility and '<blockquote' not in html:
        warnings.append(f"{name}: no blockquote found (articles should have at least one stat/tip)")


def check_index(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)

    # Index-specific: check article card images
    for m in UNSPLASH_FAKE_RE.finditer(html):
        fid = m.group(1)
        if len(fid) <= 9:
            errors.append(f"{name}: fake Unsplash photo ID 'photo-{fid}' in article card")

    for domain in DEAD_IMAGE_DOMAINS:
        if domain in html:
            errors.append(f"{name}: dead image domain in cards: {domain}")

    for m in EMAIL_RE.finditer(html):
        email = m.group(0)
        domain = email.split("@")[1]
        if domain in BANNED_EMAIL_DOMAINS:
            errors.append(f"{name}: banned email: {email}")

    for pattern, desc in PLACEHOLDER_PATTERNS:
        if re.search(pattern, html):
            errors.append(f"{name}: {desc}")

    emoji_count = len(EMOJI_RE.findall(html))
    if emoji_count > 0:
        errors.append(f"{name}: {emoji_count} emoji found")

    # Index must have GA4 + AdSense
    if 'googletagmanager.com/gtag/js' not in html:
        errors.append(f"{name}: missing GA4 tag")
    if 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' not in html:
        errors.append(f"{name}: missing AdSense script")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Scan ALL files, not just modified")
    parser.add_argument("--site", help="Scan only one site directory")
    args = parser.parse_args()

    target_sites = [args.site] if args.site else SITES_WITH_ARTICLES
    files_checked = 0

    for site in target_sites:
        site_dir = ROOT / site
        if not site_dir.exists():
            continue

        # Scan ALL HTML files recursively (catches sub-pages like guides/*/index.html)
        for f in sorted(site_dir.glob("**/*.html")):
            if f.name == "index.html":
                check_index(f, site_dir)
            else:
                check_article(f, site_dir)
            files_checked += 1

    if files_checked == 0:
        print("No files to audit.")
        return 0

    print(f"Audited {files_checked} files across {len(target_sites)} sites.\n")

    if warnings:
        print(f"=== {len(warnings)} WARNINGS ===")
        for w in warnings:
            print(f"  WARN: {w}")
        print()

    if errors:
        print(f"=== {len(errors)} ERRORS ===")
        for e in errors:
            print(f"  FAIL: {e}")
        print(f"\nCommit BLOCKED. Fix {len(errors)} error(s) before pushing.")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
