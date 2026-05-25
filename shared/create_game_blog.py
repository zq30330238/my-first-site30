"""Generate blog posts for game/anime wiki sites.
Blog topics: character analysis, gameplay tips, version updates, weapon/item deep-dives, strategy.
500-800 words, reuses site images, creates standalone HTML under {site}/blog/.
"""
import json
import os
import re
import sys
import time
import argparse
import random
from pathlib import Path
from datetime import datetime

from reasonix_helper import reasonix_call_json

ROOT = Path(__file__).resolve().parent.parent

# Site → brand/domain mapping for blog metadata
GAME_SITE_INFO = {
    "naruto-site":    {"brand": "Naruto Wiki",       "domain": "naruto.jycsd.com"},
    "onepiece-site":  {"brand": "One Piece Wiki",    "domain": "onepiece.jycsd.com"},
    "dragonball-site":{"brand": "Dragon Ball Wiki",  "domain": "dragonball.jycsd.com"},
    "lol-site":       {"brand": "LoL Wiki",          "domain": "lol.jycsd.com"},
    "fortnite-site":  {"brand": "Fortnite Wiki",     "domain": "fortnite.jycsd.com"},
    "valorant-site":  {"brand": "Valorant Wiki",     "domain": "valorant.jycsd.com"},
    "eldenring-site": {"brand": "Elden Ring Wiki",   "domain": "eldenring.jycsd.com"},
    "minecraft-site": {"brand": "Minecraft Wiki",    "domain": "minecraft.jycsd.com"},
    "anime-site":     {"brand": "Anime Wiki Hub",    "domain": "anime.jycsd.com"},
    "games-site":     {"brand": "GameGuide",         "domain": "games.jycsd.com"},
}

# Category labels for blog subject variety
BLOG_CATEGORIES = [
    "Character Analysis", "Gameplay Guide", "Strategy", "Tips & Tricks",
    "Weapon Guide", "Update Summary", "Lore Deep Dive", "Beginner Guide",
]

SYSTEM_PROMPT = """You are a professional English game content writer for a gaming wiki site.
Output ONLY a JSON object with no markdown wrapping.

CRITICAL RULES:
1. Output ONLY valid JSON. No markdown wrapping, no ```json fence.
2. Write 500-800 words total. Be concise but informative.
3. Include exactly one <blockquote> with a pro tip or key insight.
4. article_body_html MUST NOT contain <script>, <ins>, or ad elements.
5. No emoji, no AI cliche phrases like "delve", "unlock the secrets", "your ultimate guide".
6. Use active voice. US gamer audience.

JSON STRUCTURE:
{
  "title": "SEO title (60 chars max)",
  "description": "Meta description (150-160 chars)",
  "h1_title": "Blog H1 title (no brand prefix)",
  "category": "One of: Character Analysis, Gameplay Guide, Strategy, Tips & Tricks, Weapon Guide, Update Summary, Lore Deep Dive, Beginner Guide",
  "article_body_html": "<h2>First Section</h2><p>Paragraph...</p><h2>Second Section</h2><p>More...</p>",
  "read_time": "number as string e.g. '5'",
  "date_iso": "YYYY-MM-DD",
  "date_display": "Month DD, YYYY"
}"""


def build_user_prompt(site_dir, existing_titles):
    info = GAME_SITE_INFO.get(site_dir, {"brand": site_dir, "domain": f"{site_dir}.jycsd.com"})
    brand = info["brand"]
    domain = info["domain"]

    # Determine game name from site_dir
    game_name = site_dir.replace("-site", "").replace("-", " ").title()
    if game_name == "Lol":
        game_name = "League of Legends"
    if game_name == "Onepiece":
        game_name = "One Piece"

    dedup = ""
    if existing_titles:
        dedup = "\n\nALREADY WRITTEN — DO NOT repeat any of these titles:\n" + "\n".join(f"  - {t}" for t in existing_titles)

    prompt = f"""Generate a new blog post for {brand} ({game_name} wiki).

The article must be about {game_name} — a specific character, weapon, strategy, gameplay tip, or lore topic within this game/ anime.

Blog details:
- Brand: {brand}
- Domain: {domain}
- Length: 500-800 words
- Format: h1 + 2-3 h2 sections + 1 blockquote tip
- Audience: gamers aged 16-35, US English
- Pick a random category from: Character Analysis, Gameplay Guide, Strategy, Tips & Tricks, Weapon Guide, Update Summary, Lore Deep Dive, Beginner Guide

Output the JSON object as specified.{dedup}"""
    return prompt


def extract_from_index(site_dir, section):
    """Extract <nav>, <footer>, or <head> (minus title/meta) from site index.html."""
    idx_path = ROOT / site_dir / "index.html"
    if not idx_path.exists():
        return ""
    html = idx_path.read_text(encoding="utf-8", errors="ignore")

    if section == "head":
        # Extract everything in <head> but keep it generic
        m = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
        if m:
            content = m.group(1)
            # Remove site-specific <title> and meta description (we'll add our own)
            content = re.sub(r'<title>.*?</title>', '', content)
            content = re.sub(r'<meta name="description"[^>]*>', '', content)
            content = re.sub(r'<meta property="og:title"[^>]*>', '', content)
            content = re.sub(r'<meta property="og:description"[^>]*>', '', content)
            content = re.sub(r'<link rel="canonical"[^>]*>', '', content)
            return content.strip()
    elif section == "nav":
        m = re.search(r'(<nav.*?</nav>)', html, re.DOTALL)
        if m:
            return m.group(1)
    elif section == "footer":
        m = re.search(r'(<footer.*?</footer>)', html, re.DOTALL)
        if m:
            return m.group(1)
    return ""


def pick_random_image(site_dir):
    """Pick a random image from the site's images/ directory."""
    img_dir = ROOT / site_dir / "images"
    if not img_dir.exists():
        return ""
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = [f.name for f in img_dir.iterdir() if f.suffix.lower() in valid_exts and f.is_file()]
    if not images:
        return ""
    return random.choice(images)


def get_next_blog_num(site_dir):
    blog_dir = ROOT / site_dir / "blog"
    if not blog_dir.exists():
        return 1
    nums = []
    for f in blog_dir.glob("blog-*.html"):
        m = re.search(r'blog-(\d+)', f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


def get_existing_blog_titles(site_dir):
    """Collect H1 titles from existing blog posts for dedup."""
    titles = []
    blog_dir = ROOT / site_dir / "blog"
    if not blog_dir.exists():
        return titles
    for f in sorted(blog_dir.glob("blog-*.html")):
        html = f.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<h1[^>]*class="[^"]*"[^>]*>([^<]+)</h1>', html)
        if m:
            titles.append(m.group(1).strip())
    return titles


def generate_blog_html(site_dir, content, image_file):
    """Assemble complete blog HTML from content JSON and site components."""
    info = GAME_SITE_INFO.get(site_dir, {"brand": site_dir, "domain": f"{site_dir}.jycsd.com"})
    brand = info["brand"]
    domain = info["domain"]

    head_section = extract_from_index(site_dir, "head")
    nav_html = extract_from_index(site_dir, "nav")
    footer_html = extract_from_index(site_dir, "footer")

    h1 = content.get("h1_title", "Untitled")
    title = content.get("title", h1)
    desc = content.get("description", "")
    category = content.get("category", "Game Guide")
    body_html = content.get("article_body_html", "<p>Content coming soon.</p>")
    read_time = content.get("read_time", "5")
    date_display = content.get("date_display", datetime.now().strftime("%B %d, %Y"))
    date_iso = content.get("date_iso", datetime.now().strftime("%Y-%m-%d"))

    # Build <head> content
    if head_section:
        full_head = f"""<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
<meta name="google-adsense-account" content="ca-pub-2595917642864488">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://{domain}/blog/blog-{get_next_blog_num(site_dir) - 1}.html">
<meta property="og:site_name" content="{brand}">
<meta property="og:locale" content="en_US">
<link rel="canonical" href="https://{domain}/blog/blog-{get_next_blog_num(site_dir) - 1}.html">
{head_section}
</head>"""
    else:
        full_head = f"""<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
<meta name="google-adsense-account" content="ca-pub-2595917642864488">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://{domain}/blog/blog-{get_next_blog_num(site_dir) - 1}.html">
<meta property="og:site_name" content="{brand}">
<meta property="og:locale" content="en_US">
<link rel="canonical" href="https://{domain}/blog/blog-{get_next_blog_num(site_dir) - 1}.html">
<meta name="robots" content="index, follow">
<script src="https://cdn.tailwindcss.com"></script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
</head>"""

    img_tag = ""
    if image_file:
        img_tag = f'<img src="../images/{image_file}" alt="{h1}" class="w-full h-64 object-cover rounded-xl mb-8">'

    html = f"""<!DOCTYPE html>
<html lang="en">
{full_head}
<body class="flex flex-col min-h-screen" style="background:var(--bg,#0d1117);color:var(--text,#e6edf3)">

{nav_html}

<main class="max-w-4xl mx-auto px-4 py-24">
    <article>
        <span class="text-sm font-bold uppercase tracking-wide" style="color:var(--accent,#f97316)">{category}</span>
        <h1 class="text-3xl md:text-4xl font-black mt-2 mb-4">{h1}</h1>
        <div class="flex gap-4 text-sm" style="color:var(--textSecondary,#8b949e);margin-bottom:2rem">
            <time datetime="{date_iso}">{date_display}</time>
            <span>&middot;</span>
            <span>{read_time} min read</span>
        </div>
        {img_tag}
        <div class="prose max-w-none article-content">{body_html}</div>
    </article>
</main>

{footer_html}

</body>
</html>"""
    return html


def generate_blog(site_dir, dry_run=False):
    """Generate one blog post for a given game/anime site."""
    info = GAME_SITE_INFO.get(site_dir)
    if not info:
        print(f"  UNKNOWN SITE: {site_dir}")
        return False

    blog_num = get_next_blog_num(site_dir)
    print(f"\n--- Blog post #{blog_num} for {site_dir} ({info['brand']}) ---")

    if dry_run:
        print(f"  [DRY RUN] Would create blog/blog-{blog_num}.html")
        return True

    # Check existing titles for dedup
    existing_titles = get_existing_blog_titles(site_dir)
    print(f"  Existing blog posts: {len(existing_titles)}")

    # Pick a random image
    image_file = pick_random_image(site_dir)
    if image_file:
        print(f"  Image: {image_file}")
    else:
        print(f"  No images found, skipping image")

    # Call DeepSeek for content
    user_msg = build_user_prompt(site_dir, existing_titles)
    try:
        content = reasonix_call_json(SYSTEM_PROMPT, user_msg, model="deepseek-v4-flash")
    except Exception as e:
        print(f"  FAILED: API error: {e}")
        return False

    if not content:
        print(f"  FAILED: Empty response from API")
        return False

    # Validate required fields
    for key in ["h1_title", "article_body_html"]:
        if key not in content:
            print(f"  FAILED: Missing field '{key}' in API response")
            return False

    h1 = content.get("h1_title", "Untitled")
    print(f"  Title: {h1}")

    # Check dup title
    if h1.strip().lower() in [t.strip().lower() for t in existing_titles]:
        print(f"  SKIP: duplicate title '{h1[:60]}'")
        return False

    # Generate HTML
    html = generate_blog_html(site_dir, content, image_file)

    # Save
    blog_dir = ROOT / site_dir / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    out_path = blog_dir / f"blog-{blog_num}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  OK: {out_path.relative_to(ROOT)}")

    time.sleep(2)
    return True


def generate_blog_batch(sites, dry_run=False):
    """Generate blog posts for multiple sites."""
    success = 0
    fail = 0
    for site in sites:
        ok = generate_blog(site, dry_run)
        if ok:
            success += 1
        else:
            fail += 1
    return success, fail


def main():
    parser = argparse.ArgumentParser(description="Generate game/anime wiki blog posts")
    parser.add_argument("--sites", nargs="*", help="Specific game/anime sites to generate for")
    parser.add_argument("--per-site", type=int, default=1, help="Blogs per site")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    target_sites = args.sites if args.sites else list(GAME_SITE_INFO.keys())

    total_ok = 0
    total_fail = 0
    for site_dir in target_sites:
        if site_dir not in GAME_SITE_INFO:
            print(f"Unknown game/anime site: {site_dir}")
            total_fail += 1
            continue
        for _ in range(args.per_site):
            ok = generate_blog(site_dir, args.dry_run)
            if ok:
                total_ok += 1
            else:
                total_fail += 1

    print(f"\n=== Done: {total_ok} blog posts created, {total_fail} failed ===")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
