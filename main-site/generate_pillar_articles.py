"""Generate 6 pillar articles for main-site using DeepSeek API."""
import json
import os
import sys
import time
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent
ARTICLE_DIR = ROOT / "article"
API_URL = os.environ.get("API_URL", "https://api.deepseek.com/anthropic")
API_TOKEN = os.environ.get("DEEPSEEK_API_KEY", "")

CATEGORIES = [
    {
        "slug": "article-healthy-eating",
        "name": "Healthy Eating",
        "sub_site": "HealthyEats",
        "sub_url": "https://healthy.jycsd.com",
        "color": "green",
        "hex": "#16a34a",
    },
    {
        "slug": "article-pet-care",
        "name": "Pet Care",
        "sub_site": "PetCare Hub",
        "sub_url": "https://pets.jycsd.com",
        "color": "orange",
        "hex": "#ea580c",
    },
    {
        "slug": "article-home-garden",
        "name": "Home & Garden",
        "sub_site": "HomeJoy",
        "sub_url": "https://home.jycsd.com",
        "color": "emerald",
        "hex": "#047857",
    },
    {
        "slug": "article-personal-finance",
        "name": "Personal Finance",
        "sub_site": "MoneyWise",
        "sub_url": "https://finance.jycsd.com",
        "color": "blue",
        "hex": "#1d4ed8",
    },
    {
        "slug": "article-technology",
        "name": "Technology",
        "sub_site": "TechNest",
        "sub_url": "https://tech.jycsd.com",
        "color": "slate",
        "hex": "#334155",
    },
    {
        "slug": "article-travel",
        "name": "Travel",
        "sub_site": "TravelScope",
        "sub_url": "https://travel.jycsd.com",
        "color": "cyan",
        "hex": "#0e7490",
    },
]

SYSTEM_PROMPT = """You are a professional lifestyle content writer. Output ONLY valid JSON, no markdown fences.

Write a comprehensive pillar/overview article. This is NOT a how-to guide — it's a broad overview article that introduces readers to the topic, explains why it matters, and points them toward deeper resources.

CRITICAL:
- 800-1200 words, 4-6 sections
- Natural, conversational tone — write like a human journalist, not AI
- Vary sentence length. Mix short punchy sentences with longer ones.
- NO emoji, NO cliche phrases like "delve into", "in today's digital age", "let's dive in"
- Include real statistics and data points
- End with a paragraph that naturally links to the relevant sub-site for more detailed guides

JSON format:
{
  "title": "SEO title (55-60 chars)",
  "description": "Meta description (150-160 chars)",
  "h1_title": "H1 heading (without brand name)",
  "article_body_html": "Full HTML body with <h2>, <p>, and one <blockquote> with a stat. No wrapper tags like <article> or <div>.",
  "read_time": "'5' or '6' or '7' as string",
  "date_iso": "YYYY-MM-DD",
  "date_display": "Month DD, YYYY"
}"""

UNSPLASH_IDS = {
    "article-healthy-eating": "1540189549336-e6e99c3679fe",
    "article-pet-care": "1548199973-03cce0bbc87b",
    "article-home-garden": "1484154218962-a197022b5858",
    "article-personal-finance": "1500835556837-99ac94a94552",
    "article-technology": "1518770660439-4636190af475",
    "article-travel": "1508873696983-2dfd5898f08b",
}

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{description}}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{{title}}">
    <meta property="og:description" content="{{description}}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://www.jycsd.com/article/{{slug}}.html">
    <meta property="og:site_name" content="Myers Media">
    <title>{{title}} | Myers Media</title>
    <link rel="canonical" href="https://www.jycsd.com/article/{{slug}}.html">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: { 'primary': { 50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a' }, 'navy': '#0f1a3c' },
                    fontFamily: { sans: ['Roboto','Arial','Helvetica','sans-serif'], heading: ['Georgia','Times New Roman','serif'] }
                }
            }
        }
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        .article-content h2 { font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; font-family: Georgia, serif; }
        .article-content p { margin-bottom: 1.25rem; line-height: 1.8; font-size: 1.1rem; color: #374151; }
        .article-content blockquote { border-left: 4px solid {{hex}}; padding: 1rem 1.5rem; margin: 2rem 0; background: #f8fafc; border-radius: 0 8px 8px 0; font-style: italic; }
        .article-content ul { margin-bottom: 1.25rem; padding-left: 1.5rem; }
        .article-content li { margin-bottom: 0.5rem; line-height: 1.7; }
    </style>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
    <script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'G-GGNWR1X1GV');</script>
</head>
<body class="bg-white text-gray-800 font-sans">
<nav class="bg-white/95 backdrop-blur border-b border-gray-100">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" class="text-2xl font-black text-gray-900 tracking-tight">Myers<span class="text-primary-600">Media</span></a>
        <div class="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="/" class="text-gray-600 hover:text-primary-600">Home</a>
            <a href="/#sites" class="text-gray-600 hover:text-primary-600">Our Sites</a>
            <a href="/#articles" class="text-primary-600 font-medium">Articles</a>
            <a href="/about.html" class="text-gray-600 hover:text-primary-600">About</a>
        </div>
        <button class="md:hidden text-gray-600 text-2xl">☰</button>
    </div>
</nav>

<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <nav class="text-sm text-gray-400 mb-8">
        <a href="/" class="hover:text-primary-600 transition">Home</a>
        <span class="mx-2">/</span>
        <a href="/#articles" class="hover:text-primary-600 transition">Articles</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{{name}}</span>
    </nav>

    <article>
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-heading font-bold text-gray-900 leading-tight mb-4">{{h1_title}}</h1>
            <div class="flex items-center text-sm text-gray-400 space-x-4">
                <time datetime="{{date_iso}}">{{date_display}}</time>
                <span>{{read_time}} min read</span>
            </div>
        </header>

        <div class="mb-10 rounded-2xl overflow-hidden">
            <img src="https://images.unsplash.com/photo-{{unsplash_id}}?w=1200&h=630&fit=crop" alt="{{name}}" class="w-full h-64 md:h-80 object-cover">
        </div>

        <div class="article-content">
            {{article_body_html}}
        </div>
    </article>

    <div class="mt-12 p-8 bg-gray-50 rounded-2xl border border-gray-200 text-center">
        <h3 class="text-xl font-bold text-gray-900 mb-2">Explore More on {{sub_site}}</h3>
        <p class="text-gray-500 mb-4">Visit our dedicated {{name}} site for in-depth guides, expert tips, and the latest updates.</p>
        <a href="{{sub_url}}" target="_blank" rel="noopener" class="inline-block bg-primary-700 hover:bg-primary-800 text-white font-bold px-8 py-3 rounded-full text-base transition-colors">
            Visit {{sub_site}} →
        </a>
    </div>
</main>

<footer class="bg-white border-t border-gray-100 text-gray-600 py-12">
    <div class="max-w-6xl mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-gray-900 text-lg font-black mb-3">Myers<span class="text-primary-600">Media</span></h3>
                <p class="text-sm leading-relaxed text-gray-500">Your gateway to expert lifestyle guides.</p>
            </div>
            <div>
                <h4 class="text-gray-900 font-semibold mb-3">Our Network</h4>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-white text-gray-600 text-sm rounded px-3 py-2 mb-3 border border-gray-200 focus:outline-none focus:border-primary-500 cursor-pointer">
                    <option value="">— Network —</option>
                    <option value="https://www.jycsd.com">Main Site</option>
                    <option value="https://games.jycsd.com">Game Guides</option>
                    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-white text-gray-600 text-sm rounded px-3 py-2 border border-gray-200 focus:outline-none focus:border-primary-500 cursor-pointer">
                    <option value="">— More Sites —</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                </select>
            </div>
            <div>
                <h4 class="text-gray-900 font-semibold mb-3">Legal</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="privacy-policy.html" class="text-gray-500 hover:text-primary-600 transition-colors">Privacy Policy</a></li>
                    <li><a href="terms.html" class="text-gray-500 hover:text-primary-600 transition-colors">Terms of Service</a></li>
                    <li><a href="cookie-policy.html" class="text-gray-500 hover:text-primary-600 transition-colors">Cookie Policy</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-gray-900 font-semibold mb-3">Contact</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="contact.html" class="text-gray-500 hover:text-primary-600 transition-colors">Get in Touch</a></li>
                    <li><a href="mailto:contact@jycsd.com" class="text-gray-500 hover:text-primary-600 transition-colors">contact@jycsd.com</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-100 pt-6 text-center text-sm text-gray-400">
            <p>&copy; {{year}} Myers Media. All rights reserved.</p>
        </div>
    </div>
</footer>
</body>
</html>"""


def call_api(category):
    """Call DeepSeek API to generate article content."""
    prompt = f"""Write a comprehensive pillar article about {category['name']} for a US consumer audience.

This is the main overview article on jycsd.com that introduces readers to the topic of {category['name']}. It should:
- Explain the importance of {category['name']} in everyday life
- Cover 4-6 broad subtopics (not too specific)
- Include one interesting statistic in a blockquote
- End with a paragraph that naturally transitions to visiting {category['sub_url']} for more detailed guides
- Sound like a human wrote it — vary your sentence structure

Today's date: {category.get('date_iso', '')}
"""

    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 4096,
        "temperature": 0.9,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
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
            if brace_idx >= 0:
                content = content[brace_idx:]
            brace_end = content.rfind("}")
            if brace_end > 0:
                content = content[:brace_end + 1]

            return json.loads(content)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(3)
    return None


def render_article(cat, ai_output, year):
    """Render article HTML from template."""
    html = ARTICLE_TEMPLATE
    html = html.replace("{{slug}}", cat["slug"])
    html = html.replace("{{name}}", cat["name"])
    html = html.replace("{{color}}", cat["color"])
    html = html.replace("{{hex}}", cat["hex"])
    html = html.replace("{{sub_site}}", cat["sub_site"])
    html = html.replace("{{sub_url}}", cat["sub_url"])
    html = html.replace("{{unsplash_id}}", UNSPLASH_IDS[cat["slug"]])
    html = html.replace("{{description}}", ai_output.get("description", ""))
    html = html.replace("{{title}}", ai_output.get("title", ""))
    html = html.replace("{{h1_title}}", ai_output.get("h1_title", ""))
    html = html.replace("{{article_body_html}}", ai_output.get("article_body_html", ""))
    html = html.replace("{{read_time}}", ai_output.get("read_time", "5"))
    html = html.replace("{{date_iso}}", ai_output.get("date_iso", ""))
    html = html.replace("{{date_display}}", ai_output.get("date_display", ""))
    html = html.replace("{{year}}", year)
    return html


def main():
    from datetime import datetime
    year = str(datetime.now().year)
    today = datetime.now().strftime("%Y-%m-%d")
    today_display = datetime.now().strftime("%B %d, %Y")

    os.makedirs(ARTICLE_DIR, exist_ok=True)
    success = 0

    for cat in CATEGORIES:
        print(f"\n{'='*60}")
        print(f"Generating: {cat['slug']} ({cat['name']})")
        print(f"{'='*60}")

        cat["date_iso"] = today
        cat["date_display"] = today_display

        content = call_api(cat)
        if not content:
            print(f"  FAIL: API returned no content for {cat['slug']}")
            continue

        content.setdefault("date_iso", today)
        content.setdefault("date_display", today_display)

        html = render_article(cat, content, year)

        out_path = ARTICLE_DIR / f"{cat['slug']}.html"
        out_path.write_text(html, encoding="utf-8")

        # Count words
        body = content.get("article_body_html", "")
        text = re.sub(r'<[^>]+>', ' ', body)
        wc = len(text.split())

        title = content.get("h1_title", "untitled")
        print(f"  OK: {out_path.name} — {wc} words — \"{title[:60]}\"")
        success += 1
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(CATEGORIES)} articles generated")
    print(f"{'='*60}")
    return 0 if success == len(CATEGORIES) else 1


if __name__ == "__main__":
    sys.exit(main())
