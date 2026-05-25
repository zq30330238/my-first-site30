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

import html as html_mod
import re
import sys
import json
from pathlib import Path

# Force UTF-8 on stdout to prevent GBK crashes on non-ASCII chars
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
ALL_SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-food", "sub-tech", "sub-travel", "sub-auto", "sub-moto", "main-site",
    "minecraft-site", "eldenring-site", "lol-site", "fortnite-site", "valorant-site",
    "games-site", "anime-site", "dragonball-site", "onepiece-site", "naruto-site"]
SITES_WITH_ARTICLES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-food", "sub-tech", "sub-travel", "sub-auto", "sub-moto", "main-site",
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

# === Image placeholder patterns ===
IMAGE_PLACEHOLDER_PATTERNS = [
    (r"&#9670;", "Diamond image placeholder (should be real image)"),
    (r"&#128214;", "Book emoji image placeholder (should be real image)"),
    (r"&#128293;", "Fire emoji image placeholder (should be real image)"),
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
    "in conclusion",
    "let's dive",
    "let us dive",
    "fast-paced world",
    "whether you're a",
    "buckle up",
    "without any further",
    "redefining the way",
    "more than just a",
]

# === Emoji ===
EMOJI_RE = re.compile(
    r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U000025FF'
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
    "sub-food": "food.jycsd.com",
    "sub-tech": "tech.jycsd.com",
    "sub-travel": "travel.jycsd.com",
    "sub-auto": "auto.jycsd.com",
    "sub-moto": "moto.jycsd.com",
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
UTILITY_PAGES = {'about', 'contact', 'cookie-policy', 'privacy-policy', 'terms', 'articles', 'sitemap', 'category-meal-plans', 'category-nutrition', 'category-recipes', 'category-cats', 'category-dogs', 'category-small-pets', 'category-gardening', 'category-interior', 'category-diy', 'category-budgeting', 'category-investing', 'category-credit', 'category-ai', 'category-guides', 'category-reviews', 'category-security', 'category-budget-travel', 'category-destinations', 'category-digital-nomad', 'category-tips', 'category-home', 'category-tech'}
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

    # === IMAGE PLACEHOLDER CHECK ===
    for pattern, desc in IMAGE_PLACEHOLDER_PATTERNS:
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
        # Strip fragment identifiers before file existence check
        if '#' in str(target):
            target = Path(str(target).split('#')[0])
        if href.endswith('/'):
            index_target = target / 'index.html'
            if not index_target.exists():
                errors.append(f"{name}: directory link broken: {href} → {index_target.relative_to(ROOT)} (index.html not found)")
        elif not target.exists() and '.' in target.name:
            errors.append(f"{name}: broken internal link: {href} → {target.relative_to(ROOT)} (file not found)")

    # === SEMANTIC LINK MATCHING (content-area links only) ===
    # Strip nav, footer, header before link extraction — those are navigation, not semantic references
    content_html = html
    for tag in ('nav', 'footer', 'header'):
        content_html = re.sub(rf'<{tag}[\s\S]*?</{tag}>', '', content_html)
    a_tags = re.findall(r'<a\s[^>]*?href="([^"]+)"[^>]*?>(.*?)</a>', content_html, re.IGNORECASE | re.DOTALL)
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
        # Strip fragment identifiers before file existence check
        if '#' in str(target):
            target = Path(str(target).split('#')[0])
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
    # Content sites with Auto Ads script also skip manual ad slot requirement
    is_game_site = site_dir.name in GAME_SITES
    has_auto_ads = 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in html

    if not is_game_site and not has_auto_ads:
        if not utility and len(slots) not in (3, 4):
            errors.append(f"{name}: expected 3-4 ad slots, found {len(slots)}")
    for s in slots:
        if s not in VALID_SLOTS and s not in BAD_SLOTS:
            warnings.append(f"{name}: unknown ad slot: {s}")

    # Ad block integrity
    if not is_game_site and not has_auto_ads:
        ad_push = len(re.findall(r'\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\)', html))
        if not utility and ad_push != len(slots):
            errors.append(f"{name}: {len(slots)} ad units but {ad_push} push scripts (mismatch)")

    # Auto Ads script — check for ALL sites including game sites
    if not utility and 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' not in html:
        errors.append(f"{name}: missing Auto Ads script")

    # AdSense script duplicate check
    adsense_count = len(re.findall(r'adsbygoogle\.js\?client=ca-pub-', html))
    if adsense_count > 1:
        errors.append(f"{name}: {adsense_count} copies of adsbygoogle.js script (should be exactly 1)")

    # === SEO META (skip for utility pages)
    if not utility:
        meta_checks = {
            "google-adsense-account": 'google-adsense-account',
            "description": 'name="description"',
            "og:title": 'property="og:title"',
            "og:description": 'property="og:description"',
            "og:url": 'property="og:url"',
            "og:site_name": 'property="og:site_name"',
            "og:locale": 'property="og:locale"',
            "og:type": 'property="og:type"',
            "og:image": 'property="og:image"',
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

    # Title length (utility pages like about/contact/sitemap exempt)
    if not utility:
        title_m = re.search(r'<title>(.*?)</title>', html)
        if title_m:
            title_text = title_m.group(1)
            if len(title_text) < 30:
                warnings.append(f"{name}: title too short: {len(title_text)} chars")
            elif len(title_text) > 70:
                warnings.append(f"{name}: title too long: {len(title_text)} chars (keep under 70)")
            # Title should not contain duplicated segments (e.g. "Foo - Bar - Bar")
            parts = [p.strip() for p in re.split(r'\s[-|]\s', title_text)]
            seen = set()
            for p in parts:
                if len(p) > 3 and p in seen:
                    errors.append(f"{name}: duplicate segment in title — '{p}' appears twice")
                seen.add(p)

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
    else:
        # Article pages auto-generated by create_articles.py always include schema
        warnings.append(f"{name}: missing JSON-LD schema")

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

    # AdSense script duplicate check
    adsense_count = len(re.findall(r'adsbygoogle\.js\?client=ca-pub-', html))
    if adsense_count > 1:
        errors.append(f"{name}: {adsense_count} copies of adsbygoogle.js script (should be exactly 1)")

    # === OG META TAGS for index ===
    og_checks = {
        "og:title": 'property="og:title"',
        "og:description": 'property="og:description"',
        "og:url": 'property="og:url"',
        "og:site_name": 'property="og:site_name"',
        "og:locale": 'property="og:locale"',
        "og:type": 'property="og:type"',
        "og:image": 'property="og:image"',
    }
    for meta_key, pattern in og_checks.items():
        if pattern not in html:
            errors.append(f"{name}: missing meta tag: {meta_key}")

    # === SCHEMA JSON-LD for index ===
    if '<script type="application/ld+json">' not in html:
        errors.append(f"{name}: missing JSON-LD Schema on index page")


def check_ads_txt(site_dir):
    """Check ads.txt exists and has correct pub ID."""
    ads_txt_path = site_dir / "ads.txt"
    if not ads_txt_path.exists():
        errors.append(f"{site_dir.name}/ads.txt: missing ads.txt file")
        return
    content = ads_txt_path.read_text(encoding="utf-8", errors="ignore")
    # ads.txt 标准格式是 pub-xxxxxxxx，不是 ca-pub-xxxxxxxx
    expected_pub = "pub-2595917642864488"
    if expected_pub not in content:
        errors.append(f"{site_dir.name}/ads.txt: missing correct pub ID '{expected_pub}'")


def self_check():
    """验证审计规则自身的正确性——防止检查逻辑写错导致误报/漏报."""
    issues = []
    # 从实际 ads.txt 文件验证 expected_pub 格式
    all_ads = list(ROOT.glob("*/ads.txt"))
    if all_ads:
        sample = all_ads[0].read_text(encoding="utf-8", errors="ignore")
        # pub- 格式必须在 ads.txt 中
        if "pub-2595917642864488" not in sample:
            issues.append("expected_pub 'pub-2595917642864488' 未在实际ads.txt中找到，检查常量是否正确")
        # ca-pub- 格式绝不应在 ads.txt 中（那是 script 标签格式）
        if "ca-pub-2595917642864488" in sample:
            issues.append("ads.txt 中不应出现 'ca-pub-' 前缀，这是 AdSense script 标签格式")
    if issues:
        print("AUDIT SELF-CHECK FAILED:")
        for i in issues:
            print(f"  {i}")
        sys.exit(1)


def check_footer_dropdowns(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    footer_m = re.search(r'<footer[\s\S]*?</footer>', html)
    if not footer_m:
        return
    footer_html = footer_m.group(0)
    selects = re.findall(r'<select[\s\S]*?</select>', footer_html, re.DOTALL)
    if not selects:
        # Old footer format (ul + details/summary) — must upgrade to select dropdowns
        if re.search(r'<details|<summary|>More Sites<|>Our Sites<', footer_html):
            errors.append(f"{name}: footer uses old ul+details format — replace with select dropdowns")
        return

    DROPDOWN_EXPECTED = {
        "Network": {"any": [["Myers Media", "Main Site"], ["Game Guides"], ["Anime & Manga"]]},
        "Content Sites": {"all": ["HealthyEats", "PetCare Hub", "HomeJoy", "MoneyWise", "TechNest", "TripRoute", "AutoPulse", "MotoPulse", "FlavorFusion", "RightsDaily", "DailyMedAdvice", "PopCulture HQ"]},
        "Game & Anime Wikis": {"all": ["Dragon Ball Wiki", "Naruto Wiki", "One Piece Wiki", "Valorant Wiki", "Fortnite Wiki", "LoL Wiki", "Elden Ring Wiki", "Minecraft Wiki"]},
    }

    for sel in selects:
        options = re.findall(r'<option[^>]*>(.*?)</option>', sel, re.DOTALL)
        opt_texts = [html_mod.unescape(re.sub(r'<[^>]+>', '', o).strip()) for o in options]
        for key, rule in DROPDOWN_EXPECTED.items():
            if not any(key in t for t in opt_texts):
                continue
            if "all" in rule:
                existing = {t for t in opt_texts if t in rule["all"]}
                missing = [e for e in rule["all"] if e not in existing]
                if missing:
                    errors.append(f"{name}: '{key}' dropdown missing: {', '.join(missing)}")
            elif "any" in rule:
                is_game_anime = site_dir and any(
                    d in str(site_dir).lower()
                    for d in ['naruto', 'onepiece', 'dragonball', 'valorant', 'eldenring',
                              'lol-site', 'fortnite', 'anime-site', 'minecraft']
                )
                for group in rule["any"]:
                    if not any(g in opt_texts for g in group):
                        if group == ["Game Guides"] or group == ["Anime & Manga"]:
                            if not is_game_anime:
                                continue
                        errors.append(f"{name}: '{key}' dropdown missing: {', '.join(group)}")
            break


def check_guide_page_content(filepath, site_dir):
    if 'anime-site/guides/' not in str(filepath) or filepath.name != 'index.html':
        return
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)

    # Count content cards: <a> blocks with both <img> and heading
    cards = 0
    for m in re.finditer(r'<a[^>]*>[\s\S]*?</a>', html, re.IGNORECASE):
        a_block = m.group(0)
        if re.search(r'<img', a_block, re.IGNORECASE) and re.search(r'<h\d', a_block, re.IGNORECASE):
            cards += 1
    if cards < 4:
        errors.append(f"{name}: guide page has only {cards} content cards (need at least 4)")

    # Word count in main content area
    main_m = re.search(r'<main[\s\S]*?</main>', html)
    if main_m:
        text = re.sub(r'<[^>]+>', ' ', main_m.group(0))
        text = re.sub(r'\s+', ' ', text).strip()
        wc = len(text.split())
        if wc < 100:
            errors.append(f"{name}: guide page appears to be a blank shell ({wc} words)")


def check_letter_placeholders(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    # Only flag styled spans with bg- or rounded classes inside links — indicates thumbnail placeholder
    for m in re.finditer(r'<a[^>]*>[\s\S]*?</a>', html, re.IGNORECASE):
        a_block = m.group(0)
        span_m = re.search(r'<span[^>]*class="[^"]*(?:bg-|rounded)[^"]*"[^>]*>([A-Z])</span>', a_block)
        if span_m:
            errors.append(f"{name}: letter placeholder found: '{span_m.group(1)}' used instead of image in series/character card")


def check_article_image_exists(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
    if not m:
        return
    url = m.group(1)
    if not url.startswith('/') and not url.startswith('images/'):
        return
    img_path = site_dir / url.lstrip('/')
    if not img_path.exists():
        errors.append(f"{name}: og:image file missing: {url}")
    elif img_path.stat().st_size < 5000:
        errors.append(f"{name}: og:image too small ({img_path.stat().st_size} bytes): {url}")


def check_local_img_srcs(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    for m in re.finditer(r'<img[^>]*src="([^"]+)"[^>]*>', html):
        src = m.group(1)
        if src.startswith('http') or src.startswith('data:'):
            continue
        img_path = site_dir / src.lstrip('/')
        if not img_path.exists():
            errors.append(f"{name}: <img> file missing: {src}")


def check_site_skeleton(filepath, site_dir):
    if site_dir.name not in GAME_SITES:
        return
    html_files = [f for f in site_dir.glob("**/*.html") if 'play' not in f.parts]
    if len(html_files) <= 15:
        warnings.append(f"site '{site_dir.name}' has only {len(html_files)} HTML files — may be a skeleton (needs character/guide content)")


def check_index_card_images(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = label(filepath)
    # Find article cards with empty background-image
    empty_cards = re.findall(r'background-image:url\(\)', html)
    if empty_cards:
        errors.append(f"{name}: {len(empty_cards)} article card(s) have empty background-image — run collect_content_images.py")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Scan ALL files, not just modified")
    parser.add_argument("--site", help="Scan only one site directory")
    args = parser.parse_args()

    self_check()

    target_sites = [args.site] if args.site else SITES_WITH_ARTICLES
    files_checked = 0
    _skeleton_checked = set()

    for site in target_sites:
        site_dir = ROOT / site
        if not site_dir.exists():
            continue

        # Check ads.txt for every site
        check_ads_txt(site_dir)

        # Scan ALL HTML files recursively (catches sub-pages like guides/*/index.html)
        for f in sorted(site_dir.glob("**/*.html")):
            if "\\play\\" in str(f) or "/play/" in str(f):
                continue  # standalone HTML5 games don't need SEO/ad meta
            if "\\.backup\\" in str(f) or "/.backup/" in str(f):
                continue  # skip backup files
            check_footer_dropdowns(f, site_dir)

            if 'anime-site/guides/' in str(f) and f.name == 'index.html':
                check_guide_page_content(f, site_dir)

            if f.name == 'index.html' or 'guides/' in str(f):
                check_letter_placeholders(f, site_dir)

            check_local_img_srcs(f, site_dir)

            if site_dir.name in GAME_SITES and site_dir.name not in _skeleton_checked:
                check_site_skeleton(f, site_dir)
                _skeleton_checked.add(site_dir.name)

            if f.name == "index.html":
                check_index(f, site_dir)
                check_index_card_images(f, site_dir)
            else:
                check_article(f, site_dir)
                if f.name.startswith("article-") and f.name.endswith(".html"):
                    check_article_image_exists(f, site_dir)
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
