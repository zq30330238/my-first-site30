"""Batch generate NEW articles for 6 sites via DeepSeek API. Runs unattended on Hengchuang server.

Usage: python3 shared/create_articles.py [--per-site N] [--dry-run]
"""

import re
import json
import sys
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.deepseek.com/anthropic/v1/messages"
API_TOKEN = "sk-07777fe5f4554dbcaeddce87c7ccb950"

SITES = {
    "sub-healthy": {"domain": "healthy.jycsd.com", "brand": "HealthyEats", "category": "健康饮食", "color": "green", "brandColor": "green-600", "brandHex": "#16a34a"},
    "sub-pets": {"domain": "pets.jycsd.com", "brand": "PetCareGuide", "category": "宠物护理", "color": "orange", "brandColor": "orange-600", "brandHex": "#ea580c"},
    "sub-home": {"domain": "home.jycsd.com", "brand": "HomeNest", "category": "家居园艺", "color": "emerald", "brandColor": "emerald-700", "brandHex": "#047857"},
    "sub-finance": {"domain": "finance.jycsd.com", "brand": "MoneyWise", "category": "个人理财", "color": "blue", "brandColor": "blue-700", "brandHex": "#1d4ed8"},
    "sub-tech": {"domain": "tech.jycsd.com", "brand": "TechPulse", "category": "科技数码", "color": "slate", "brandColor": "slate-700", "brandHex": "#334155"},
    "sub-travel": {"domain": "travel.jycsd.com", "brand": "TravelScope", "category": "旅行攻略", "color": "cyan", "brandColor": "cyan-700", "brandHex": "#0e7490"},
}

SYSTEM_PROMPT = """You are a professional English SEO content writer for US consumer websites.
Your task: write a COMPLETE HTML article file by replacing ONLY the content areas in a provided template.

CRITICAL RULES:
1. OUTPUT THE COMPLETE HTML FILE — from <!DOCTYPE html> to </html>. No truncation, no markdown wrapping.
2. Keep everything outside the article content area IDENTICAL — EXCEPT the sidebar "Related Articles" section: replace hardcoded "Article 1/2/3" placeholder text with the real article titles from the linked .html files. Read the linked article's <h1> or <title> to get the correct title.
3. The ad units MUST stay in the exact same positions within the article body — after the 1st, 3rd, and 5th <h2> sections respectively. Do not move or remove them.
4. Replace these content areas:
   - <title> and <meta name="description"> and <meta name="keywords">
   - <meta property="og:title">, <meta property="og:description">, <meta property="og:url">
   - <link rel="canonical">
   - <h1> article title
   - Breadcrumb text
   - <img> cover image (MUST use https://images.unsplash.com/photo-XXXXX?w=1200&h=630&fit=crop format with a real photo ID. NEVER use source.unsplash.com — that domain is dead and returns broken images.)
   - All text inside <div class="article-content">: <h2> headings, <p> paragraphs, <ul>/<ol> lists, <blockquote> callouts
   - Tag spans at the bottom of the article
   - <time datetime=""> date
   - JSON-LD NewsArticle: headline, description, datePublished, dateModified, mainEntityOfPage @id
5. Article structure: 1 h1 title → cover img → 5-6 h2 sections with 2-3 paragraphs each → ad units after h2 #1, #3, #5 → some h2s may have h3 subsections → 1 blockquote with key stat/tip → tags
6. Word count: 1000-1500 words for article body (inside article-content div)
7. Writing style: authoritative, practical, data-backed advice for US consumers. Use specific numbers, research findings, actionable steps. No emoji, no fluff, no AI phrases like "in today's world" or "it's important to note".
8. Target audience: everyday Americans looking for practical information.
9. URL format: https://<domain>/article-N.html (the script will provide the exact URL)
10. Date: use today's date provided in the prompt."""


def get_next_article_num(site_dir):
    nums = []
    for f in (ROOT / site_dir).glob("article-*.html"):
        m = re.search(r'article-(\d+)', f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


def get_template_html(site_dir):
    """Read the latest article as template."""
    nums = []
    for f in (ROOT / site_dir).glob("article-*.html"):
        m = re.search(r'article-(\d+)', f.name)
        if m:
            nums.append((int(m.group(1)), f))

    if not nums:
        return None, 1

    latest = max(nums, key=lambda x: x[0])
    return latest[1].read_text(encoding="utf-8"), latest[0] + 1


def call_api(template_html, article_path, site_info, article_num):
    domain = site_info["domain"]
    brand = site_info["brand"]
    category = site_info["category"]
    url = f"https://{domain}/article-{article_num}.html"
    today = datetime.now().strftime("%Y-%m-%d")

    user_msg = f"""TEMPLATE HTML FILE (use as structural template):
{template_html}

SITE INFO:
- Brand: {brand}
- Category: {category}
- Domain: {domain}
- Article URL: {url}
- Article number: {article_num}
- Date: {today}

INSTRUCTIONS:
1. Write a COMPLETELY NEW article on a fresh topic within the {category} niche.
2. Replace the title, meta tags, h1, breadcrumb, cover image URL, all article body content (h2s, paragraphs, lists, blockquotes), tags, and JSON-LD schema.
3. Keep ALL scripts, styles, header, footer, sidebar, and ad units IDENTICAL to the template.
4. Output the COMPLETE HTML file — every single line from <!DOCTYPE html> to </html>.
5. Word count: 1000-1500 words in the article-content div.

Make the new article topic different from the template's topic."""

    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 16384,
        "temperature": 0.8,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_msg}],
    }

    req = Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
    )

    for attempt in range(3):
        try:
            resp = urlopen(req, timeout=300)
            data = json.loads(resp.read().decode())
            text_blocks = [b["text"] for b in data["content"] if b["type"] == "text"]
            content = "\n".join(text_blocks)
            # Extract HTML
            if content.startswith("```html"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            doctype_idx = content.find("<!DOCTYPE html>")
            if doctype_idx > 0:
                content = content[doctype_idx:]
            html_end = content.rfind("</html>")
            if html_end > 0:
                content = content[:html_end + 7]
            return content.strip()
        except (URLError, HTTPError) as e:
            print(f"  Attempt {attempt+1} failed (HTTP): {e}", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed ({type(e).__name__}): {e}", flush=True)
            time.sleep(10)
    return None


def count_words(html):
    start = re.search(r'class="[^"]*article-content[^"]*"[^>]*>', html)
    if not start:
        return 0
    pos = start.end()
    depth = 1
    while depth > 0 and pos < len(html):
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
                inner = html[start.end():next_close]
                text = re.sub(r'<[^>]+>', ' ', inner)
                text = re.sub(r'\s+', ' ', text).strip()
                return len(text.split())
            pos = next_close + 6
    return 0


def validate_article(html, expected_num):
    errors = []
    if not html.startswith("<!DOCTYPE html>") or not html.strip().endswith("</html>"):
        errors.append("Missing DOCTYPE or </html>")
    if f"article-{expected_num}" not in html:
        errors.append(f"Wrong article number in URL (expected {expected_num})")
    ad_count = len(re.findall(r'class="ad-unit"', html))
    if ad_count != 3:
        errors.append(f"Wrong ad unit count: {ad_count} (expected 3)")
    wc = count_words(html)
    if wc < 800:
        errors.append(f"Word count too low: {wc} (need 800+)")
    if "adsbygoogle" not in html:
        errors.append("Missing AdSense script")
    if "G-GGNWR1X1GV" not in html:
        errors.append("Missing GA4 tag")
    if 'application/ld+json' not in html:
        errors.append("Missing JSON-LD schema")
    if "source.unsplash.com" in html:
        errors.append("Contains dead source.unsplash.com URLs — use images.unsplash.com/photo-XXXXX")
    if re.search(r'<p class="text-gray-700 text-sm mt-1">Article \d</p>', html):
        errors.append("Contains hardcoded 'Article N' placeholder in sidebar — replace with real titles")
    return errors, wc


def auto_fix_generated(html, site_dir):
    """Fix common AI generation mistakes before saving."""
    fixes = 0

    # Fix 1: source.unsplash.com → real Unsplash photo
    if "source.unsplash.com" in html:
        # Use a generic high-quality photo from the right domain based on category
        fallback = {
            "sub-pets": "1548199973-03cce0bbc87b",
            "sub-healthy": "1490645935967-10de6ba17071",
            "sub-home": "1484154218962-a197022b5858",
            "sub-finance": "1579621970563-ebec7560ff3e",
            "sub-tech": "1531297484001-80022131f5a1",
            "sub-travel": "1506192209153-aff2f5e6cf42",
        }
        photo_id = fallback.get(site_dir, "1548199973-03cce0bbc87b")
        new_url = f"https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop"
        html = re.sub(r'https://source\.unsplash\.com/[^"\s]+', new_url, html)
        fixes += 1

    # Fix 2: Replace hardcoded "Article N" in sidebar with real titles
    def replace_article_placeholder(m):
        num = m.group(1)
        linked = ROOT / site_dir / f"article-{num}.html"
        title = extract_title(linked) if linked.exists() else f"Article {num}"
        return f'<p class="text-gray-700 text-sm mt-1">{title}</p>'

    new_html, n = re.subn(
        r'<p class="text-gray-700 text-sm mt-1">Article (\d+)</p>',
        replace_article_placeholder,
        html
    )
    if n > 0:
        html = new_html
        fixes += n

    return html, fixes


def update_index_sidebar(site_dir, article_num, title):
    """Add new article to index.html Recent Posts sidebar (top of list, max 12)."""
    idx_path = ROOT / site_dir / "index.html"
    if not idx_path.exists():
        return

    html = idx_path.read_text(encoding="utf-8")
    domain = SITES[site_dir]["domain"]
    url = f"https://{domain}/article-{article_num}.html"

    # Find the Recent Posts section
    sidebar_marker = 'Recent Posts'
    if sidebar_marker not in html:
        return

    # Short title for sidebar
    short_title = title[:60] + "..." if len(title) > 60 else title

    new_item = f'<li><a href="article-{article_num}.html" class="text-gray-700 hover:text-brand-600 transition text-sm">{short_title}</a></li>\n'

    # Find insertion point: right after the first <li> in Recent Posts area, or after the opening <ul>
    recent_pos = html.find(sidebar_marker)
    ul_start = html.find("<ul", recent_pos)
    ul_end = html.find(">", ul_start) + 1

    html = html[:ul_end] + "\n" + new_item + html[ul_end:]

    # Keep max 12 items
    ul_end_new = html.find("</ul>", recent_pos)
    ul_content = html[html.find("<ul", recent_pos):ul_end_new]
    items = re.findall(r'<li>.*?</li>', ul_content, re.DOTALL)
    if len(items) > 12:
        # Find and remove the last excess items
        for item in items[12:]:
            html = html.replace(item, "", 1)

    idx_path.write_text(html, encoding="utf-8")


def update_sitemap(site_dir, article_num):
    """Add new article URL to sitemap.xml."""
    sm_path = ROOT / site_dir / "sitemap.xml"
    if not sm_path.exists():
        return

    domain = SITES[site_dir]["domain"]
    url = f"https://{domain}/article-{article_num}.html"
    today = datetime.now().strftime("%Y-%m-%d")

    new_entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.80</priority>
  </url>
"""

    xml = sm_path.read_text(encoding="utf-8")
    insert_pos = xml.rfind("</url>")
    if insert_pos == -1:
        return
    insert_pos = xml.find("\n", insert_pos) + 1

    xml = xml[:insert_pos] + new_entry + xml[insert_pos:]
    sm_path.write_text(xml, encoding="utf-8")


def extract_title(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m2 = re.search(r'<title>(.*?)</title>', html)
    if m2:
        return m2.group(1).strip()
    return "Untitled"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-site", type=int, default=5, help="Articles per site")
    parser.add_argument("--sites", nargs="*", help="Specific sites to generate for")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()

    target_sites = args.sites if args.sites else list(SITES.keys())
    total = 0
    results = []

    for site_dir in target_sites:
        if site_dir not in SITES:
            print(f"Unknown site: {site_dir}")
            continue

        info = SITES[site_dir]
        print(f"\n{'='*60}")
        print(f"Site: {site_dir} ({info['domain']}) - {info['category']}")
        print(f"{'='*60}")

        for i in range(args.per_site):
            article_num = get_next_article_num(site_dir)
            template, _ = get_template_html(site_dir)

            if not template:
                print(f"  SKIP: No template found for {site_dir}")
                continue

            print(f"  Generating article-{article_num}.html...", flush=True)

            if args.dry_run:
                print(f"    [DRY RUN] Would create article-{article_num}.html")
                results.append((site_dir, article_num, "[dry run]", 0))
                continue

            html = call_api(template, f"{site_dir}/article-{article_num}.html", info, article_num)

            if not html:
                print(f"    FAIL: API call failed after 3 attempts")
                continue

            # Auto-fix common AI generation mistakes
            html, auto_fixes = auto_fix_generated(html, site_dir)
            if auto_fixes > 0:
                print(f"    Auto-fixed {auto_fixes} issue(s) in generated HTML")

            errors, wc = validate_article(html, article_num)
            if errors:
                print(f"    FAIL: {'; '.join(errors)}")
                continue

            # Save article
            out_path = ROOT / site_dir / f"article-{article_num}.html"
            out_path.write_text(html, encoding="utf-8")

            title = extract_title(html)
            print(f"    OK: article-{article_num}.html — {wc} words — \"{title[:60]}...\"")

            # Update sidebar and sitemap
            update_index_sidebar(site_dir, article_num, title)
            update_sitemap(site_dir, article_num)

            results.append((site_dir, article_num, title, wc))
            total += 1
            time.sleep(3)  # Rate limit

    # Summary
    print(f"\n{'='*60}")
    print(f"Generated {total} new articles across {len(target_sites)} sites")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r[0]}/article-{r[1]}.html — {r[3]}w — {r[2][:50]}")

    if args.dry_run or total == 0:
        return 0

    # Audit
    print(f"\n{'='*60}")
    print("Running pre-commit audit...")
    print(f"{'='*60}")
    audit = subprocess.run(
        ["python3", str(ROOT / "shared" / "pre_commit_audit.py")],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(audit.stdout)
    if audit.stderr:
        print(audit.stderr)

    if audit.returncode != 0:
        print("ERROR: Audit failed. Fix issues before committing.")
        return 1

    # Commit + push
    print(f"\n{'='*60}")
    print("Committing and pushing...")
    print(f"{'='*60}")

    for r in results:
        subprocess.run(["git", "add", f"{r[0]}/article-{r[1]}.html"], cwd=str(ROOT), capture_output=True)
        subprocess.run(["git", "add", f"{r[0]}/index.html"], cwd=str(ROOT), capture_output=True)
        subprocess.run(["git", "add", f"{r[0]}/sitemap.xml"], cwd=str(ROOT), capture_output=True)

    msg = f'add: {total} new articles across {len(target_sites)} sites'
    subprocess.run(["git", "commit", "-m", msg], cwd=str(ROOT), capture_output=True)

    push = subprocess.run(["git", "push", "origin", "master"],
        cwd=str(ROOT), capture_output=True, text=True)
    print(push.stdout.strip())
    if push.stderr:
        print(push.stderr.strip())

    print("\nDone. GitHub Actions will auto-deploy to Cloudflare Pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
