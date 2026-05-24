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
import urllib.request
from datetime import datetime, timezone, timedelta
import random
from pathlib import Path

from reasonix_helper import reasonix_call_json, reasonix_call, ark_call_json

from site_templates import (
    SITE_CONFIG, GLOBALS, TEMPLATE_SKELETON,
    render_article_html, quick_validate, get_content_generation_prompt,
)

import random

TITLE_STARTERS = [
    "How to", "The Complete Guide to", "Why", "What",
    "Top", "Best", "Essential", "Simple",
]

ARTICLE_TEMPLATES = {
    "A": {
        "description": "List-style with deep analysis of each item. Each list item has its own mini-section with detailed explanation.",
        "h2_sections": "4-5 h2 sections (each covering one list item in depth)",
        "paragraphs_per_section": "2-4 paragraphs per section",
        "word_count": "1000-1400 words total",
        "ad_positions": "One ad unit after h2 #1 only",
        "title_style": "How-to / List",
        "tone": "Direct, instructional, bullet-point friendly",
    },
    "B": {
        "description": "Narrative storytelling format. Opens with a relatable scenario/anecdote, then transitions into analysis, ends with key takeaways summary section.",
        "h2_sections": "5-7 h2 sections (intro context → body analysis → summary)",
        "paragraphs_per_section": "2-5 paragraphs per section",
        "word_count": "1200-1800 words total",
        "ad_positions": "One ad unit after h2 #2 only",
        "title_style": "Why / Story-driven",
        "tone": "Conversational, engaging, builds curiosity",
    },
    "C": {
        "description": "Problem-driven Q&A format. Each h2 poses a question and the paragraphs answer it. Real reader pain points addressed directly.",
        "h2_sections": "5-6 h2 sections (each is a reader question)",
        "paragraphs_per_section": "2-3 paragraphs per section (answer each question thoroughly)",
        "word_count": "1000-1500 words total",
        "ad_positions": "Ad units after h2 #1 and after h2 #4",
        "title_style": "Question-driven / What",
        "tone": "Empathetic, authoritative, problem-solving",
    },
    "D": {
        "description": "Comparison or ranked listicle format. Ranks items/n options with pros/cons, comparison table in prose, detailed breakdown of each.",
        "h2_sections": "6-8 h2 sections (introduction + each option ranked + verdict)",
        "paragraphs_per_section": "1-3 paragraphs per section (concise, data-heavy)",
        "word_count": "1500-2200 words total",
        "ad_positions": "One ad unit after h2 #3 only",
        "title_style": "Best / Top / Comparison",
        "tone": "Data-backed, comparative, decisive",
    },
    "E": {
        "description": "Step-by-step tutorial/guide format. Each h2 is a sequential step. Practical tips, common mistakes, pro advice inline.",
        "h2_sections": "4-6 h2 sections (each is a numbered step in sequence)",
        "paragraphs_per_section": "3-5 paragraphs per step (detailed instructions)",
        "word_count": "1000-1400 words total",
        "ad_positions": "Ad units after h2 #1, #3, and #5 (if they exist)",
        "title_style": "Step-by-step / Guide",
        "tone": "Patient, thorough, beginner-friendly",
    },
}

ROOT = Path(__file__).resolve().parent.parent

def build_system_prompt(force_template=None, topic=None):
    """Select article template (forced or random) and build a tailored SYSTEM_PROMPT."""
    if force_template and force_template in ARTICLE_TEMPLATES:
        template_key = force_template
    else:
        template_key = random.choice(list(ARTICLE_TEMPLATES.keys()))
    tmpl = ARTICLE_TEMPLATES[template_key]

    # Rule #2 + template selection changes based on whether a specific topic is assigned
    if topic:
        topic_rule = "2. YOU HAVE BEEN ASSIGNED A SPECIFIC TOPIC. Your h1_title MUST equal the TOPIC from the user message exactly. Do NOT invent a different title, different car brand, or different subject. Write ONLY about the assigned topic."
        # Force review/narrative templates for topic mode — never use listicle (A/C/E) which encourages topic drift
        if force_template is None:
            template_key = random.choice(['B', 'D'])
            tmpl = ARTICLE_TEMPLATES[template_key]
    else:
        topic_rule = "2. The user message lists topics ALREADY covered on this site. You MUST pick a COMPLETELY DIFFERENT topic — different sub-category, different angle, different keywords. Never rehash the same subject with slightly different wording."

    prompt = f"""You are a professional English SEO content writer for US consumer websites.
Output a JSON object with the article content fields listed below. Do NOT output HTML wrapper, header, footer, or sidebars — the Python pipeline handles template injection.

CRITICAL RULES:
1. Output ONLY valid JSON. No markdown wrapping, no ```json fence.
{topic_rule}
3. Always include one <blockquote> with a key stat or expert tip.
4. article_body_html MUST NOT contain any <script>, <ins>, <div class="ad-">, or adsbygoogle elements.
5. Writing: authoritative, data-backed, actionable. US consumer audience. Specific numbers. No emoji, no fluff, no AI cliche phrases.

ARTICLE FORMAT: {tmpl['description']}
- {tmpl['h2_sections']}
- {tmpl['paragraphs_per_section']}
- {tmpl['word_count']}
- Tone: {tmpl['tone']}

JSON STRUCTURE (exact keys):
{{
  "title": "SEO title (60 chars max) — includes brand name",
  "description": "Meta description (150-160 chars)",
  "keywords": "5-8 comma-separated SEO keywords",
  "h1_title": "H1 article title (without brand name)",
  "breadcrumb": "Short breadcrumb text for nav",
  "cover_image_prompt": "Brief description of the image for this article (e.g. 'A professional lawyer reviewing documents in a modern law office')",
  "article_body_html": "<h2>First Section</h2><p>Paragraph text...</p><h2>Second Section</h2><p>More text...</p>",
  "tag_spans": "<span class='px-3 py-1 bg-brand-50 text-brand-700 text-sm rounded-full'>Tag1</span><span ...>Tag2</span>... (5-6 tags)",
  "json_ld": "{{full JSON-LD NewsArticle schema object, string-escaped}}",
  "read_time": "number as string e.g. '7'",
  "date_iso": "YYYY-MM-DD",
  "date_display": "Month DD, YYYY"
}}

"""

    return prompt, template_key


def get_next_article_num(site_dir):
    nums = []
    for f in (ROOT / site_dir).glob("article-*.html"):
        m = re.search(r'article-(\d+)', f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1


def _try_api(template_key, ctx, user_msg, topic=None, max_attempts=3, delay=5):
    """Try calling DeepSeek with a specific template, retry on failure.
    Topic mode → deepseek-chat (Pro, strong instruction following).
    Free mode → deepseek-v4-flash (fast/cheap)."""
    system_prompt, _ = build_system_prompt(template_key, topic=topic)
    model = "deepseek-chat" if topic else "deepseek-v4-flash"
    for attempt in range(max_attempts):
        try:
            content = reasonix_call_json(system_prompt, user_msg, model=model)
            print(f"  Template {template_key}: OK", flush=True)
            return content
        except (json.JSONDecodeError, RuntimeError, TimeoutError, Exception) as e:
            print(f"  Template {template_key} attempt {attempt+1}/{max_attempts}: {type(e).__name__}: {e}", flush=True)
            if attempt < max_attempts - 1:
                time.sleep(delay * (attempt + 1))  # progressive delay
    return None


def call_api(site_dir, article_num, force_template=None, topic=None):
    """Ask DeepSeek to generate article content as JSON.
    Tries the selected template first, then falls back to others on failure."""
    ctx = get_content_generation_prompt(site_dir, article_num, topic=topic)
    today = datetime.now().strftime("%Y-%m-%d")

    if topic:
        extra = ""
        if topic.get('angle'):
            extra = "\nANGLE: " + topic['angle'] + "\nKEY POINTS TO COVER:\n- " + "\n- ".join(topic.get('key_points', []))
        user_msg = f"""CRITICAL INSTRUCTION — You MUST write about this EXACT topic:

TOPIC: {topic['title']}
CATEGORY: {topic['category']}{extra}

Your H1 title MUST be a natural variation of the topic above. Do NOT change the subject to a different car brand, different model, or generic listicle. If the topic is about BYD Seal, write about BYD Seal specifically — not "electric sedans in general." If the topic is about Huawei AITO M9, write about AITO M9 specifically.

Site details:
- Brand: {ctx['brand']}
- Domain: {ctx['domain']}
- Article URL: {ctx['article_url']}
- Date: {today}

Output the JSON object as specified. Minimum 1000 words of body content (not counting HTML tags)."""
    else:
        user_msg = f"""Generate a new SEO article for {ctx['brand']} ({ctx['category']}).

Site details:
- Brand: {ctx['brand']}
- Domain: {ctx['domain']}
- Article URL: {ctx['article_url']}
- Date: {today}
Write a fresh article on a topic in the {ctx['category']} niche. Output the JSON object as specified. Minimum 1000 words of body content (not counting HTML tags)."""

    # Scan existing articles for topic dedup
    existing_h1s = []
    site_path = ROOT / site_dir
    if site_path.exists():
        for f in sorted(site_path.glob("article-*.html")):
            html = f.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'<h1[^>]*class="[^"]*"[^>]*>([^<]+)</h1>', html)
            if m:
                existing_h1s.append(m.group(1).strip())
    if existing_h1s:
        dedup_msg = "\n\nALREADY COVERED TOPICS — DO NOT repeat, reword, or write about ANY of these:\n"
        for i, h1 in enumerate(existing_h1s, 1):
            dedup_msg += f"  {i}. {h1}\n"
        dedup_msg += "\nPick a COMPLETELY DIFFERENT topic. Diversify across sub-categories: reviews, comparisons, buying guides, industry news, technology trends, DIY, safety, regulations, etc."
        user_msg += dedup_msg

    # Templates ordered by reliability (A,C,D most stable; B,E more intermittent)
    if force_template:
        template_order = [force_template]
    else:
        template_order = ['A', 'C', 'D', 'B', 'E']

    for tkey in template_order:
        result = _try_api(tkey, ctx, user_msg, topic=topic)
        if result is not None:
            return result

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




def generate_and_verify_image(title, category, description, site_dir, article_num, daily_count):
    """Generate article image via Seedream 5.0, verify with doubao, download locally.

    Args:
        title: Article H1 title
        category: Site category (e.g. "Legal Rights", "Health & Medical")
        description: Article meta description
        site_dir: Site directory name
        article_num: Article number
        daily_count: How many images generated today so far

    Returns:
        (image_url, daily_count) - relative URL to local image, updated count
        or ("", daily_count) if failed
    """
    SEEDREAM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    SEEDREAM_API_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
    SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
    MAX_DAILY = 50

    if daily_count >= MAX_DAILY:
        print(f"  WARNING: Daily image limit ({MAX_DAILY}) reached, skipping image generation")
        return ("", daily_count)

    output_dir = ROOT / site_dir / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"article-{article_num}.jpg"

    prompt = f"A professional, high-quality {category} themed photograph. {title}. Clean, well-lit, photorealistic style, suitable for a website article header, 16:9 landscape orientation. CRITICAL: Absolutely NO watermark, NO text, NO words, NO labels, NO title overlays, NO signature, NO logo anywhere on the image. The image must be completely free of any text or watermark elements."

    for attempt in range(2):
        try:
            body = json.dumps({
                "model": SEEDREAM_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": "2560x1440",
                "watermark": False,
            }).encode()

            req = urllib.request.Request(
                SEEDREAM_API_URL,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {SEEDREAM_API_KEY}"
                },
                method="POST"
            )

            print(f"  Generating image (attempt {attempt+1})...", flush=True)
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())

            img_url = data.get("data", [{}])[0].get("url", "")
            if not img_url:
                print(f"  Image API returned no URL (attempt {attempt+1})")
                daily_count += 1
                if attempt == 0:
                    prompt = f"Stock photography style image about {title}. Natural lighting, professional composition, suitable for {category} website header. CRITICAL: completely clean image, NO watermark, NO text, NO signature, NO label of any kind."
                continue

            # Download image
            print(f"  Downloading image...", flush=True)
            with urllib.request.urlopen(img_url, timeout=60) as img_resp:
                output_path.write_bytes(img_resp.read())
            print(f"  Image saved: {output_path}")

            # Compress image for web: resize to 1200px wide, JPEG quality 85
            try:
                from PIL import Image as PILImage
                img = PILImage.open(output_path)
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_size = (1200, int(img.height * ratio))
                    img = img.resize(new_size, PILImage.LANCZOS)
                # Convert RGBA to RGB for JPEG
                if img.mode == "RGBA":
                    bg = PILImage.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", quality=85, optimize=True)
                compressed_size = output_path.stat().st_size
                print(f"  Compressed: {output_path.name} ({compressed_size//1024}KB)")
            except ImportError:
                print(f"  Pillow not available, skipping compression")
            except Exception as comp_err:
                print(f"  Compression warning: {comp_err}")

            # Verify with doubao (reads result from temp file)
            verify_cmd = [
                sys.executable, str(ROOT / "shared" / "doubao_vision.py"),
                str(output_path),
                f"Is this image related to {category} AND free of any visible text/words/watermarks/titles? Answer YES or NO and explain briefly in one sentence."
            ]
            print(f"  Verifying image with doubao...", flush=True)
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, timeout=60)
            # doubao writes result to temp file, not stdout
            doubao_outfile = os.path.join(
                os.environ.get('TEMP', os.environ.get('TMP', '/tmp')),
                'doubao_vision_output.txt'
            )
            verify_output = ""
            if os.path.exists(doubao_outfile):
                with open(doubao_outfile, 'r', encoding='utf-8') as f:
                    verify_output = f.read().strip()
                os.unlink(doubao_outfile)  # clean up

            # Check for fatal doubao API errors (account overdue, auth failed, etc.)
            if verify_output.startswith("ERROR:FATAL_DOUBAO_ERROR:") or verify_result.returncode != 0:
                err_detail = verify_output.replace("ERROR:FATAL_DOUBAO_ERROR:", "").strip() if verify_output.startswith("ERROR:") else (verify_result.stderr or "doubao_vision.py exited with code " + str(verify_result.returncode))
                raise RuntimeError(
                    f"\n{'='*60}\n"
                    f"  DOUBAO API FATAL ERROR - Pipeline stopped\n"
                    f"  Error: {err_detail}\n"
                    f"  Action: Check doubao account balance or API key, then re-run.\n"
                    f"{'='*60}"
                )

            if verify_output.upper().startswith("YES"):
                print(f"  Image verification PASSED")
                daily_count += 1
                return (f"images/article-{article_num}.jpg", daily_count)
            else:
                print(f"  Image verification FAILED (attempt {attempt+1}): {verify_output[:200]}")
                daily_count += 1
                if attempt == 0:
                    prompt = f"A clean, professional stock photo style image on the topic of {title}. Photography with natural lighting, suitable for a {category} website. NO text, NO words, NO watermarks, NO title overlays, 16:9 landscape."
                if output_path.exists():
                    output_path.unlink()

        except Exception as e:
            print(f"  Image generation error (attempt {attempt+1}): {e}")
            daily_count += 1
            if attempt == 0:
                prompt = f"Stock photography style image on the topic of {title}. Natural lighting, professional composition, suitable for web article header in {category} niche."

    print(f"  Image generation FAILED after all attempts")
    if output_path.exists():
        output_path.unlink()
    return ("", daily_count)


def update_category_page_images(site_dir, article_num, content):
    """Replace gradient placeholder in category pages with real background image."""
    cover_url = content.get("cover_img_url", "")
    if not cover_url:
        return
    full_path = ROOT / site_dir / cover_url
    if not full_path.exists():
        return

    site_path = ROOT / site_dir
    for cat_file in site_path.glob("category-*.html"):
        html = cat_file.read_text(encoding="utf-8")
        pattern = re.compile(
            r'<div class="h-48 bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">\s*'
            r'<span class="text-white/20 text-6xl font-black">' + str(article_num) + r'</span>\s*'
            r'</div>'
        )
        if pattern.search(html):
            replacement = f'<div class="h-48 bg-cover bg-center" style="background-image:url({cover_url})"></div>'
            html = pattern.sub(replacement, html)
            cat_file.write_text(html, encoding="utf-8")
            print(f"    Updated category image: {cat_file.name} article-{article_num}")


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

    cover_url = content.get("cover_img_url", "")

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

    # Limit index grid cards to 12 (newest first)
    after_grid = html[grid_pos:]
    cards_in_grid = re.findall(r'<a href="article-\d+\.html".*?</a>\s*', after_grid, re.DOTALL)
    if len(cards_in_grid) > 12:
        for card in cards_in_grid[12:]:
            after_grid = after_grid.replace(card, "", 1)
        html = html[:grid_pos] + after_grid

    # Ensure "View All Articles" button exists when 12+ cards (only add once)
    if 'View All Articles' not in html:
        after_grid = html[grid_pos:]
        cards_in_grid = re.findall(r'<a href="article-\d+\.html".*?</a>\s*', after_grid, re.DOTALL)
        if len(cards_in_grid) >= 12:
            # Find the closing </div> of the article grid (the div with grid class)
            grid_section_end = html.find('</section>', grid_pos)
            if grid_section_end == -1:
                grid_section_end = html.find('<section', grid_pos)
            if grid_section_end == -1:
                grid_section_end = html.find('<footer', grid_pos)
            if grid_section_end != -1:
                button_html = """
        <div class="text-center mt-10">
            <a href="articles.html" class="inline-block bg-brand-700 hover:bg-brand-800 text-white font-semibold px-8 py-3 rounded-full text-lg transition-colors">
                View All Articles →
            </a>
        </div>
"""
                html = html[:grid_section_end] + button_html + "\n" + html[grid_section_end:]

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


def update_articles_page(site_dir, article_num, content):
    """Create or update articles.html as a paginated list view (25 items/page)."""
    art_dir = ROOT / site_dir
    idx_path = art_dir / "index.html"
    if not idx_path.exists():
        return

    idx_html = idx_path.read_text(encoding="utf-8")

    # Extract head section
    head_end = idx_html.find('</head>')
    if head_end == -1:
        return
    head_section = idx_html[:head_end + 7]

    title_tag = re.search(r'<title>(.*?)</title>', head_section, re.DOTALL)
    if title_tag:
        new_title = f"All Articles - {title_tag.group(1)}"
        head_section = head_section.replace(title_tag.group(0), f'<title>{new_title}</title>')

    # Extract nav
    nav_start = idx_html.find('<nav')
    nav_html = ""
    if nav_start != -1:
        nav_end = idx_html.find('</nav>', nav_start) + 6
        nav_html = idx_html[nav_start:nav_end]

    # Extract footer
    footer_start = idx_html.find('<footer')
    footer_html = ""
    if footer_start != -1:
        footer_end = idx_html.find('</footer>', footer_start) + 9
        footer_html = idx_html[footer_start:footer_end]

    # Scan all article files for metadata
    articles = []
    for f in sorted(art_dir.glob("article-*.html")):
        m = re.search(r'article-(\d+)', f.name)
        if not m:
            continue
        art_num = int(m.group(1))
        art_html = f.read_text(encoding="utf-8")

        # H1 title
        title = "Untitled"
        h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', art_html, re.DOTALL)
        if h1_m:
            title = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip()

        # Date from <time datetime="YYYY-MM-DD">
        date_display = ""
        time_m = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', art_html)
        if time_m:
            try:
                dt = datetime.strptime(time_m.group(1), "%Y-%m-%d")
                date_display = dt.strftime("%B %d, %Y")
            except ValueError:
                date_display = time_m.group(1)

        # Read time from "X min read"
        read_time = ""
        read_m = re.search(r'(\d+)\s*min\s*read', art_html, re.IGNORECASE)
        if not read_m:
            read_m = re.search(r'(\d+)\s*min', art_html)
        if read_m:
            read_time = read_m.group(1) + " min"

        articles.append((art_num, title, date_display, read_time))

    # Handle empty case
    if not articles:
        (art_dir / "articles.html").write_text(f"""<!DOCTYPE html>
<html lang="en">
{head_section}
<body class="bg-gray-50 text-gray-800">

{nav_html}

<main class="max-w-4xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">All Articles</h1>
    <p class="text-gray-500 text-center py-12">No articles yet.</p>
</main>

{footer_html}
</body>
</html>""", encoding="utf-8")
        return

    # Sort newest first, paginate 25/page
    articles.sort(key=lambda x: x[0], reverse=True)
    PER_PAGE = 25
    total_pages = (len(articles) + PER_PAGE - 1) // PER_PAGE

    for page in range(1, total_pages + 1):
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        page_articles = articles[start:end]

        filename = "articles.html" if page == 1 else f"articles-{page}.html"
        filepath = art_dir / filename

        # Build list rows
        rows = []
        for art_num, title, date_display, read_time in page_articles:
            rows.append(f"""            <a href="article-{art_num}.html" class="flex items-center justify-between py-3 px-4 hover:bg-gray-50 border-b border-gray-100 transition">
              <span class="text-gray-900 font-medium truncate pr-4">{title}</span>
              <div class="flex items-center gap-6 text-sm text-gray-400 shrink-0">
                <span>{date_display}</span>
                <span class="w-16 text-right">{read_time}</span>
              </div>
            </a>""")
        all_rows = "\n".join(rows)

        # Build pagination nav
        nav_items = []
        # Previous
        if page == 1:
            nav_items.append('          <span class="px-3 py-2 text-gray-300">← Previous</span>')
        else:
            prev_href = "articles.html" if page == 2 else f"articles-{page - 1}.html"
            nav_items.append(f'          <a href="{prev_href}" class="px-3 py-2 text-brand-600 hover:text-brand-700 font-medium">← Previous</a>')

        # Page numbers
        for p in range(1, total_pages + 1):
            href = "articles.html" if p == 1 else f"articles-{p}.html"
            if p == page:
                nav_items.append(f'          <span class="px-3 py-2 bg-brand-600 text-white rounded">{p}</span>')
            else:
                nav_items.append(f'          <a href="{href}" class="px-3 py-2 text-gray-600 hover:text-brand-600 rounded">{p}</a>')

        # Next
        if page == total_pages:
            nav_items.append('          <span class="px-3 py-2 text-gray-300">Next →</span>')
        else:
            nav_items.append(f'          <a href="articles-{page + 1}.html" class="px-3 py-2 text-brand-600 hover:text-brand-700 font-medium">Next →</a>')

        pagination = "\n".join(nav_items)

        filepath.write_text(f"""<!DOCTYPE html>
<html lang="en">
{head_section}
<body class="bg-gray-50 text-gray-800">

{nav_html}

<main class="max-w-4xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">All Articles</h1>
    <div class="bg-white rounded-lg shadow-sm border border-gray-100">
{all_rows}
    </div>
    <nav class="flex items-center justify-center gap-3 mt-10 text-sm">
{pagination}
    </nav>
</main>

{footer_html}
</body>
</html>""", encoding="utf-8")


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
    parser.add_argument("--template", help="Force a specific article template (A/B/C/D/E)")
    parser.add_argument("--with-images", action="store_true", help="Generate images via Seedream (costs money; default uses free DuckDuckGo+Unsplash via collect_content_images.py)")
    args = parser.parse_args()

    if args.template and args.template not in ARTICLE_TEMPLATES:
        print(f"ERROR: --template must be one of {list(ARTICLE_TEMPLATES.keys())}, got '{args.template}'")
        return 1

    target_sites = args.sites if args.sites else list(SITE_CONFIG.keys())
    total = 0
    results = []
    daily_image_count = 0

    for site_dir in target_sites:
        if site_dir not in SITE_CONFIG:
            print(f"Unknown site: {site_dir}")
            continue

        cfg = SITE_CONFIG[site_dir]
        print(f"\n{'='*60}")
        print(f"Site: {site_dir} ({cfg['domain']}) - {cfg['category']}")
        print(f"{'='*60}")

        # Collect predefined topics (used first before AI free-generation)
        predefined_topics = cfg.get("predefined_topics", [])
        topics_queue = list(predefined_topics)
        if predefined_topics:
            print(f"  Predefined topics available: {len(predefined_topics)} (will use before free-generation)")

        for i in range(args.per_site):
            article_num = get_next_article_num(site_dir)
            print(f"  Generating article-{article_num}.html...", flush=True)

            if args.dry_run:
                print(f"    [DRY RUN] Would create article-{article_num}.html")
                results.append((site_dir, article_num, "[dry run]", 0))
                continue

            # Pop next predefined topic, or None for AI to choose freely
            topic = topics_queue.pop(0) if topics_queue else None

            # 1. Get content JSON from DeepSeek
            content = call_api(site_dir, article_num, args.template, topic=topic)
            if not content:
                print(f"    FAIL: API call failed after 3 attempts")
                continue

            # 2. Check for duplicate title
            h1 = content.get("h1_title", "").strip().lower()
            if h1:
                existing_h1s = set()
                for f in (ROOT / site_dir).glob("article-*.html"):
                    h = re.search(r'<h1[^>]*>([^<]+)</h1>', f.read_text(encoding="utf-8", errors="ignore"))
                    if h:
                        existing_h1s.add(h.group(1).strip().lower())
                if h1 in existing_h1s:
                    print(f"    SKIP: duplicate title '{h1[:60]}' — already exists in {site_dir}")
                    continue

            # 3. Check required fields
            required = ["title", "h1_title", "article_body_html"]
            missing = [k for k in required if k not in content]
            if missing:
                print(f"    FAIL: Missing fields in AI output: {missing}")
                continue

            # 3. Generate article image (only if --with-images; default: free images via collect_content_images.py)
            if args.with_images:
                image_url, daily_image_count = generate_and_verify_image(
                    content.get("h1_title", ""),
                    cfg["category"],
                    content.get("description", ""),
                    site_dir, article_num, daily_image_count
                )
                content["cover_img_url"] = image_url
            else:
                content["cover_img_url"] = f"images/article-{article_num}.jpg"

            # 4. Render full HTML via template
            content["article_url"] = f"https://{cfg['domain']}/article-{article_num}.html"
            html, _ = render_article_html(site_dir, content)

            # 4.5 Randomize date to avoid all articles showing same date
            days_ago = random.randint(7, 90)
            rand_date = datetime.now() - timedelta(days=days_ago)
            date_iso = rand_date.strftime("%Y-%m-%d")
            date_display = rand_date.strftime("%B %d, %Y")
            html = re.sub(r'<time datetime="[^"]*"', f'<time datetime="{date_iso}"', html)
            html = re.sub(r'"datePublished":\s*"[^"]*"', f'"datePublished": "{date_iso}"', html)
            html = re.sub(r'"dateModified":\s*"[^"]*"', f'"dateModified": "{date_iso}"', html)
            content["date_display"] = date_display

            # 5. Validate
            issues = quick_validate(html, site_dir)
            wc = count_words(content.get("article_body_html", ""))
            if wc < 900:
                issues.append(f"Word count too low: {wc} (need 1000+)")

            if issues:
                print(f"    FAIL: {'; '.join(issues)}")
                continue

            # 6. Save article
            out_path = ROOT / site_dir / f"article-{article_num}.html"
            out_path.write_text(html, encoding="utf-8")

            title = content.get("h1_title", extract_title(html))
            print(f"    OK: article-{article_num}.html — {wc} words — \"{title[:60]}\"")

            # 7. Update index + category pages + sitemap
            insert_index_card(site_dir, article_num, content)
            update_category_page_images(site_dir, article_num, content)
            update_articles_page(site_dir, article_num, content)
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
        [sys.executable, str(ROOT / "shared" / "pre_commit_audit.py")],
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
