"""Batch generate NEW articles for 6 sites via DeepSeek API + template injection.

DeepSeek outputs article CONTENT only (JSON) — Python wraps it in site template.
Result: ~50% fewer tokens per article, global values in one place.

Usage: py shared/create_articles.py [--per-site N] [--dry-run]
"""

import os
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

from site_templates import (
    SITE_CONFIG, GLOBALS, TEMPLATE_SKELETON,
    render_article_html, quick_validate, get_content_generation_prompt,
)

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.deepseek.com/anthropic/v1/messages"
API_TOKEN = os.environ.get("DEEPSEEK_API_KEY", "")

SYSTEM_PROMPT = """You are a professional English SEO content writer for US consumer websites.
Output a JSON object with the article content fields listed below. Do NOT output HTML wrapper, header, footer, or sidebars — the Python pipeline handles template injection.

CRITICAL RULES:
1. Output ONLY valid JSON. No markdown wrapping, no ```json fence.
2. Cover image: MUST use a REAL 11-char Unsplash photo ID like a1b2c3d4e5f6-g7h8i9j0k1l2. NEVER use short numeric IDs (those are fake). NEVER use source.unsplash.com (dead domain).
3. Article body: 5-6 h2 sections, each with 2-3 <p> paragraphs. 1000-1500 words total. Include one <blockquote> with a key stat/tip.
4. Ad units go after h2 #1, #3, #5. Use the ad slot IDs provided.
5. Writing: authoritative, data-backed, actionable. US consumer audience. Specific numbers and research. No emoji, no fluff, no AI cliche phrases.

JSON STRUCTURE (exact keys):
{
  "title": "SEO title (60 chars max) — includes brand name",
  "description": "Meta description (150-160 chars)",
  "keywords": "5-8 comma-separated SEO keywords",
  "h1_title": "H1 article title (without brand name)",
  "breadcrumb": "Short breadcrumb text for nav",
  "cover_img_html": "<img src='https://images.unsplash.com/photo-REAL_ID?w=1200&h=630&fit=crop' alt='description' class='rounded-2xl mb-10 w-full'>",
  "article_body_html": "<h2>First Section</h2><div class='ad-unit'>...ad code...</div><p>Paragraph text...</p><h2>Second Section</h2>...",
  "tag_spans": "<span class='px-3 py-1 bg-brand-50 text-brand-700 text-sm rounded-full'>Tag1</span><span ...>Tag2</span>... (5-6 tags)",
  "json_ld": "{full JSON-LD NewsArticle schema object, string-escaped}",
  "read_time": "number as string e.g. '7'",
  "date_iso": "YYYY-MM-DD",
  "date_display": "Month DD, YYYY"
}

For article_body_html: include ad-unit divs exactly like this template between h2 sections:
<div class='ad-unit'><span class='ad-label'>Advertisement</span><ins class='adsbygoogle' style='display:block; min-height:280px' data-ad-client='<pub-id>' data-ad-slot='<slot-id>' data-ad-format='auto' data-full-width-responsive='true'></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div>"""


def get_next_article_num(site_dir):
    nums = []
    for f in (ROOT / site_dir).glob("article-*.html"):
        m = re.search(r'article-(\d+)', f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


def call_api(site_dir, article_num):
    """Ask DeepSeek to generate article content as JSON."""
    ctx = get_content_generation_prompt(site_dir, article_num)
    today = datetime.now().strftime("%Y-%m-%d")

    user_msg = f"""Generate a new SEO article for {ctx['brand']} ({ctx['category']}).

Site details:
- Brand: {ctx['brand']}
- Domain: {ctx['domain']}
- Article URL: {ctx['article_url']}
- Date: {today}
- AdSense pub ID: {GLOBALS['adsense_pub']}
- Ad slot 1: {ctx['adsense_slot_1']}
- Ad slot 2: {ctx['adsense_slot_2']}
- Ad slot 3: {ctx['adsense_slot_3']}

Write a fresh article on a topic in the {ctx['category']} niche. Output the JSON object as specified."""

    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 8192,
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

            # Extract JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            brace_idx = content.find("{")
            if brace_idx > 0:
                content = content[brace_idx:]
            brace_end = content.rfind("}")
            if brace_end > 0:
                content = content[:brace_end + 1]

            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"  Attempt {attempt+1} JSON parse failed: {e}", flush=True)
            time.sleep(3)
        except (URLError, HTTPError) as e:
            print(f"  Attempt {attempt+1} HTTP failed: {e}", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed ({type(e).__name__}): {e}", flush=True)
            time.sleep(5)
    return None


def count_words(html):
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return len(text.split())


def extract_title(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return "Untitled"


UNSPLASH_FAKE_RE = re.compile(r'photo-(\d{1,6})\?')

CATEGORY_PHOTOS = {
    "sub-pets": [
        "1552053831-3a2e697e8eea", "1514888286974-6c03e2ca1dba", "1548199973-03cce0bbc87b",
        "1601758228041-f3b2795255f1", "1583337130417-3346a1be6dee", "1587300003388-59208cc962cb",
        "1583511666407-5f2d7c5b5c46", "1522069169874-c58ec4b76be5", "1606567595334-d39972c85dbe",
    ],
    "sub-healthy": [
        "1490645935967-10de6ba17071", "1512621776951-a57141f2eefd", "1505576399279-565b52d4ac71",
        "1498837167922-ddd27525d352",
    ],
    "sub-home": [
        "1484154218962-a197022b5858", "1502672260266-1c1ef2d93688", "1558618666-83b2f28bea8f",
        "1564013799919-ab600027f443",
    ],
    "sub-finance": [
        "1554226655-67b1a2f2b5c5", "1579621970563-ebec7560ff3e", "1551839091-fb60f3b9d9a5",
        "1450101499163-8feaec89286c",
    ],
    "sub-tech": [
        "1518770660439-4636190af475", "1531297484001-80022131f5a1", "1496181133206-80ce9b88a853",
        "1504639725590-34d0984388bd",
    ],
    "sub-travel": [
        "1488646953014-3064f3b6b7a0", "1476514525535-e2521697c7c2", "1506192209153-aff2f5e6cf42",
        "1502920917128-1aa500764cbd",
    ],
}


def is_real_unsplash_url(url):
    m = UNSPLASH_FAKE_RE.search(url)
    if not m:
        return True
    return len(m.group(1)) > 9


def fix_cover_image_url(content, site_dir):
    """Replace AI-faked Unsplash photo IDs with real ones."""
    cover_html = content.get("cover_img_html", "")
    m = re.search(r'https://images\.unsplash\.com/photo-([^?]+)\?', cover_html)
    if not m:
        return content
    photo_id = m.group(1)
    if len(photo_id) > 9:
        return content
    photos = CATEGORY_PHOTOS.get(site_dir, CATEGORY_PHOTOS["sub-pets"])
    real_id = photos[hash(photo_id) % len(photos)]
    content["cover_img_html"] = cover_html.replace(photo_id, real_id)
    print(f"  Fixed fake Unsplash ID: {photo_id} → {real_id}")
    return content


def insert_index_card(site_dir, article_num, content):
    idx_path = ROOT / site_dir / "index.html"
    if not idx_path.exists():
        return
    html = idx_path.read_text(encoding="utf-8")
    grid_marker = 'class="grid md:grid-cols-2 lg:grid-cols-3 gap-8"'
    grid_pos = html.find(grid_marker)
    if grid_pos == -1:
        return

    first_card = html.find("<a href=", grid_pos)
    if first_card == -1:
        return

    cover_html = content.get("cover_img_html", "")
    cover_url = ""
    cover_m = re.search(r'src=[\'"]([^\'"]+)[\'"]', cover_html)
    if cover_m:
        cover_url = cover_m.group(1)
        cover_url = re.sub(r'w=\d+', 'w=400', cover_url)
        cover_url = re.sub(r'h=\d+', 'h=250', cover_url)
        cover_url = re.sub(r'(fit=crop)', r'\1', cover_url)
        if 'fit=crop' not in cover_url:
            cover_url += '&fit=crop'

    h1_title = content.get("h1_title", "")
    desc = content.get("description", "")
    if len(desc) > 100:
        desc = desc[:97] + "..."
    read_time = content.get("read_time", "7")
    date_display = content.get("date_display", datetime.now().strftime("%B %d, %Y"))

    new_card = f"""
            <a href="article-{article_num}.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url({cover_url})"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">{h1_title}</h3>
                    <p class="text-gray-500 text-sm">{desc}</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>{date_display}</span><span>&middot;</span><span>{read_time} min read</span>
                    </div>
                </div>
            </a>
"""
    html = html[:first_card] + new_card + html[first_card:]
    idx_path.write_text(html, encoding="utf-8")


def update_index_sidebar(site_dir, article_num, title):
    idx_path = ROOT / site_dir / "index.html"
    if not idx_path.exists():
        return

    html = idx_path.read_text(encoding="utf-8")
    sidebar_marker = 'Recent Posts'
    if sidebar_marker not in html:
        return

    short_title = title[:60] + "..." if len(title) > 60 else title
    new_item = f'<li><a href="article-{article_num}.html" class="text-gray-700 hover:text-brand-600 transition text-sm">{short_title}</a></li>\n'

    recent_pos = html.find(sidebar_marker)
    ul_start = html.find("<ul", recent_pos)
    ul_end = html.find(">", ul_start) + 1
    html = html[:ul_end] + "\n" + new_item + html[ul_end:]

    ul_end_new = html.find("</ul>", recent_pos)
    ul_content = html[html.find("<ul", recent_pos):ul_end_new]
    items = re.findall(r'<li>.*?</li>', ul_content, re.DOTALL)
    if len(items) > 12:
        for item in items[12:]:
            html = html.replace(item, "", 1)

    idx_path.write_text(html, encoding="utf-8")


def update_sitemap(site_dir, article_num):
    sm_path = ROOT / site_dir / "sitemap.xml"
    if not sm_path.exists():
        return

    domain = SITE_CONFIG[site_dir]["domain"]
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-site", type=int, default=5, help="Articles per site")
    parser.add_argument("--sites", nargs="*", help="Specific sites to generate for")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()

    target_sites = args.sites if args.sites else list(SITE_CONFIG.keys())
    total = 0
    results = []

    for site_dir in target_sites:
        if site_dir not in SITE_CONFIG:
            print(f"Unknown site: {site_dir}")
            continue

        cfg = SITE_CONFIG[site_dir]
        print(f"\n{'='*60}")
        print(f"Site: {site_dir} ({cfg['domain']}) - {cfg['category']}")
        print(f"{'='*60}")

        for i in range(args.per_site):
            article_num = get_next_article_num(site_dir)
            print(f"  Generating article-{article_num}.html...", flush=True)

            if args.dry_run:
                print(f"    [DRY RUN] Would create article-{article_num}.html")
                results.append((site_dir, article_num, "[dry run]", 0))
                continue

            # 1. Get content JSON from DeepSeek
            content = call_api(site_dir, article_num)
            if not content:
                print(f"    FAIL: API call failed after 3 attempts")
                continue

            # 2. Check required fields
            required = ["title", "h1_title", "article_body_html"]
            missing = [k for k in required if k not in content]
            if missing:
                print(f"    FAIL: Missing fields in AI output: {missing}")
                continue

            # 3. Fix AI-faked Unsplash photo IDs before rendering
            content = fix_cover_image_url(content, site_dir)

            # 4. Inject ad slot IDs if AI forgot them
            slots = cfg["adsense_slots"]
            for j, slot in enumerate(slots):
                placeholder = f"<slot-{j+1}>"
                if placeholder in content.get("article_body_html", ""):
                    content["article_body_html"] = content["article_body_html"].replace(
                        placeholder, slot
                    )

            # 5. Render full HTML via template
            content["article_url"] = f"https://{cfg['domain']}/article-{article_num}.html"
            html, _ = render_article_html(site_dir, content)

            # 6. Validate
            issues = quick_validate(html, site_dir)
            wc = count_words(content.get("article_body_html", ""))
            if wc < 800:
                issues.append(f"Word count too low: {wc} (need 800+)")
            # Check for fake Unsplash IDs in rendered HTML
            for fake_m in UNSPLASH_FAKE_RE.finditer(html):
                fid = fake_m.group(1)
                if len(fid) <= 9:
                    issues.append(f"Fake Unsplash photo ID: photo-{fid}")

            if issues:
                print(f"    FAIL: {'; '.join(issues)}")
                continue

            # 7. Save article
            out_path = ROOT / site_dir / f"article-{article_num}.html"
            out_path.write_text(html, encoding="utf-8")

            title = content.get("h1_title", extract_title(html))
            print(f"    OK: article-{article_num}.html — {wc} words — \"{title[:60]}\"")

            # 8. Update index + sitemap
            insert_index_card(site_dir, article_num, content)
            update_index_sidebar(site_dir, article_num, title)
            update_sitemap(site_dir, article_num)
            results.append((site_dir, article_num, title, wc))
            total += 1
            time.sleep(3)

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
        ["py", str(ROOT / "shared" / "pre_commit_audit.py")],
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
