#!/usr/bin/env python3
"""Batch hub article generator for jycsd.com - generates 20 new articles + 26 images"""

import os, json, time, urllib.request, sys, traceback, re
from pathlib import Path

BASE_DIR = Path(r"d:\AI网站文件夹\main-site")
ARTICLE_DIR = BASE_DIR / "article"
IMAGE_DIR = BASE_DIR / "images"
CACHE_FILE = BASE_DIR / "articles_cache.json"

DEEPSEEK_API = "https://api.deepseek.com/chat/completions"
DEEPSEEK_KEY = "sk-e69d05bf4a264f9ebb2d751dad68e080"
SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"

CATEGORY_COLORS = {
    "Healthy Eating": {"name": "green", "hex": "16a34a", "index_text": "green-600", "index_bg": "green-100", "index_text_bold": "green-700"},
    "Pet Care": {"name": "orange", "hex": "ea580c", "index_text": "orange-600", "index_bg": "orange-100", "index_text_bold": "orange-700"},
    "Home & Garden": {"name": "lime", "hex": "047857", "index_text": "lime-600", "index_bg": "lime-100", "index_text_bold": "lime-700"},
    "Personal Finance": {"name": "blue", "hex": "1d4ed8", "index_text": "blue-700", "index_bg": "blue-100", "index_text_bold": "blue-700"},
    "Technology": {"name": "slate", "hex": "334155", "index_text": "slate-600", "index_bg": "slate-100", "index_text_bold": "slate-700"},
    "Travel": {"name": "cyan", "hex": "0e7490", "index_text": "cyan-600", "index_bg": "cyan-100", "index_text_bold": "cyan-700"},
}

EXISTING_ARTICLES = [
    {"slug": "article-healthy-eating", "title": "Healthy Eating: A Practical Guide to Nourishing Your Body and Mind", "h1": "Healthy Eating: A Practical Guide to Nourishing Your Body and Mind", "category": "Healthy Eating", "sub_site": "HealthyEats", "sub_url": "https://healthy.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&h=400&fit=crop", "card_desc": "Discover what healthy eating really means, why it matters, and how to build balanced habits. Explore key principles and find deeper guides."},
    {"slug": "article-pet-care", "title": "Pet Care Basics: What Every Owner Should Know", "h1": "Pet Care Basics: What Every Owner Should Know", "category": "Pet Care", "sub_site": "PetCareHub", "sub_url": "https://pets.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&h=400&fit=crop", "card_desc": "A broad overview of pet care covering nutrition, exercise, grooming, and vet visits. Learn why these pillars matter for your pet's health."},
    {"slug": "article-home-garden", "title": "The Ultimate Home Garden Guide: Growing Your Way to Greener Living", "h1": "The Ultimate Home Garden Guide: Growing Your Way to Greener Living", "category": "Home & Garden", "sub_site": "HomeNest", "sub_url": "https://home.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&h=400&fit=crop", "card_desc": "Transform your living space with indoor plants, container gardens, and simple DIY projects that anyone can master."},
    {"slug": "article-personal-finance", "title": "Personal Finance for Beginners: Building Wealth One Step at a Time", "h1": "Personal Finance for Beginners: Building Wealth One Step at a Time", "category": "Personal Finance", "sub_site": "MoneyWise", "sub_url": "https://finance.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1500835556837-99ac94a94552?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1500835556837-99ac94a94552?w=600&h=400&fit=crop", "card_desc": "Master the essentials of budgeting, saving, and investing — no finance degree required, just practical steps that work."},
    {"slug": "article-technology", "title": "Technology Trends 2026: What Every User Should Know", "h1": "Technology Trends 2026: What Every User Should Know", "category": "Technology", "sub_site": "TechPulse", "sub_url": "https://tech.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop", "card_desc": "Stay ahead with our breakdown of the year's most important tech developments, from AI tools to smart home innovations."},
    {"slug": "article-travel", "title": "The Smart Traveler's Handbook: Tips for Affordable Adventures", "h1": "The Smart Traveler's Handbook: Tips for Affordable Adventures", "category": "Travel", "sub_site": "TravelScope", "sub_url": "https://travel.jycsd.com", "unsplash_article": "https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=1200&h=630&fit=crop", "unsplash_index": "https://images.unsplash.com/photo-1508873696983-2dfd5898f08b?w=600&h=400&fit=crop", "card_desc": "Discover budget-friendly strategies for planning unforgettable trips, from finding cheap flights to packing like a pro."},
]

NEW_ARTICLES = [
    {"slug": "article-meal-prep-101", "title": "Meal Prep 101: Save Time and Eat Better Every Week", "category": "Healthy Eating", "sub_site": "HealthyEats", "sub_url": "https://healthy.jycsd.com"},
    {"slug": "article-superfoods-truth", "title": "The Truth About Superfoods: What Science Says", "category": "Healthy Eating", "sub_site": "HealthyEats", "sub_url": "https://healthy.jycsd.com"},
    {"slug": "article-nutrition-labels", "title": "How to Read Nutrition Labels Like a Pro", "category": "Healthy Eating", "sub_site": "HealthyEats", "sub_url": "https://healthy.jycsd.com"},
    {"slug": "article-plant-based-eating", "title": "Plant-Based Eating: A Beginner's Transition Guide", "category": "Healthy Eating", "sub_site": "HealthyEats", "sub_url": "https://healthy.jycsd.com"},
    {"slug": "article-pet-adoption-guide", "title": "Pet Adoption Guide: What to Know Before You Bring a Pet Home", "category": "Pet Care", "sub_site": "PetCareHub", "sub_url": "https://pets.jycsd.com"},
    {"slug": "article-pet-health-issues", "title": "Common Pet Health Issues Every Owner Should Recognize", "category": "Pet Care", "sub_site": "PetCareHub", "sub_url": "https://pets.jycsd.com"},
    {"slug": "article-traveling-with-pets", "title": "Traveling with Pets: A Complete Safety Guide", "category": "Pet Care", "sub_site": "PetCareHub", "sub_url": "https://pets.jycsd.com"},
    {"slug": "article-pet-nutrition", "title": "Pet Nutrition: Choosing the Right Food for Your Companion", "category": "Pet Care", "sub_site": "PetCareHub", "sub_url": "https://pets.jycsd.com"},
    {"slug": "article-indoor-plant-care", "title": "Indoor Plant Care: A Beginner's Guide to Greener Living", "category": "Home & Garden", "sub_site": "HomeNest", "sub_url": "https://home.jycsd.com"},
    {"slug": "article-home-organization", "title": "Home Organization: Declutter Your Space in 7 Days", "category": "Home & Garden", "sub_site": "HomeNest", "sub_url": "https://home.jycsd.com"},
    {"slug": "article-energy-efficiency", "title": "Energy Efficiency at Home: Save Money and the Planet", "category": "Home & Garden", "sub_site": "HomeNest", "sub_url": "https://home.jycsd.com"},
    {"slug": "article-credit-score", "title": "Credit Score Explained: How to Build and Maintain Good Credit", "category": "Personal Finance", "sub_site": "MoneyWise", "sub_url": "https://finance.jycsd.com"},
    {"slug": "article-side-hustles", "title": "Side Hustles 2026: Turn Your Skills Into Extra Income", "category": "Personal Finance", "sub_site": "MoneyWise", "sub_url": "https://finance.jycsd.com"},
    {"slug": "article-retirement-planning", "title": "Retirement Planning in Your 30s: Start Now for a Comfortable Future", "category": "Personal Finance", "sub_site": "MoneyWise", "sub_url": "https://finance.jycsd.com"},
    {"slug": "article-insurance-basics", "title": "Insurance Basics: What Coverage You Actually Need", "category": "Personal Finance", "sub_site": "MoneyWise", "sub_url": "https://finance.jycsd.com"},
    {"slug": "article-cybersecurity-basics", "title": "Cybersecurity Basics: Protecting Your Digital Life", "category": "Technology", "sub_site": "TechPulse", "sub_url": "https://tech.jycsd.com"},
    {"slug": "article-smart-home-guide", "title": "Smart Home Guide: Devices That Actually Make Life Easier", "category": "Technology", "sub_site": "TechPulse", "sub_url": "https://tech.jycsd.com"},
    {"slug": "article-cloud-storage", "title": "Cloud Storage Showdown: Which Service Fits Your Needs?", "category": "Technology", "sub_site": "TechPulse", "sub_url": "https://tech.jycsd.com"},
    {"slug": "article-budget-travel", "title": "Budget Travel: How to See the World on a Shoestring", "category": "Travel", "sub_site": "TravelScope", "sub_url": "https://travel.jycsd.com"},
    {"slug": "article-solo-travel-safety", "title": "Solo Travel Safety: Essential Tips for First-Timers", "category": "Travel", "sub_site": "TravelScope", "sub_url": "https://travel.jycsd.com"},
]

def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {"articles": {}, "images": {}}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

def call_deepseek(prompt, retries=3):
    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    req = urllib.request.Request(
        DEEPSEEK_API,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_KEY}"},
        method="POST"
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode())
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"  DeepSeek attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
    return None

def call_seedream(prompt, retries=3):
    payload = {
        "model": "doubao-seedream-4-5-251128",
        "prompt": prompt,
        "n": 1,
        "size": "2560x1440"
    }
    req = urllib.request.Request(
        SEEDREAM_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SEEDREAM_KEY}"},
        method="POST"
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode())
                return data["data"][0]["url"]
        except Exception as e:
            print(f"  Seedream attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
    return None

def download_image(url, filepath):
    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            filepath.write_bytes(resp.read())
        try:
            from PIL import Image
            img = Image.open(filepath)
            if img.width > 1200:
                ratio = 1200 / img.width
                new_size = (1200, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                img.save(filepath, "JPEG", quality=85)
        except ImportError:
            pass
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False

def generate_article_content(article, cache):
    slug = article["slug"]
    if slug in cache["articles"]:
        print(f"  Using cached content for {slug}")
        return cache["articles"][slug]

    cc = CATEGORY_COLORS[article["category"]]
    prompt = f"""You are writing a hub/overview article for a lifestyle portal called Myers Media (jycsd.com). Write an engaging, informative article about: {article["title"]}

Category: {article["category"]}
Audience: General readers, English native speakers
Tone: Professional, warm, authoritative

Requirements:
- 800-1200 words
- 4-6 h2 sections
- Include specific data points, statistics, or expert insights
- Start with a strong introductory paragraph before the first h2
- End with a paragraph that naturally points readers to visit {article["sub_site"]} (mention it by name) for more in-depth guides and resources
- Do NOT use markdown - return pure JSON

Return valid JSON with this exact structure:
{{
    "title": "SEO title for the page | Myers Media",
    "h1_title": "Main H1 heading for the page (should be engaging and clear)",
    "description": "Meta description, max 155 chars",
    "article_body_html": "Full article HTML with <p> and <h2> tags only. Do NOT wrap in a container div. Use <blockquote> for statistics.",
    "read_time": "number only, e.g. 8",
    "card_description": "Short description for homepage card, max 120 chars"
}}"""

    result = call_deepseek(prompt)
    if result:
        cache["articles"][slug] = result
        save_cache(cache)
        return result
    return None

def generate_image_file(article, cache):
    image_name = f"{article['slug']}-image.jpg"
    image_path = IMAGE_DIR / image_name
    if image_path.exists():
        print(f"  Image exists: {image_name}")
        cache["images"][article["slug"]] = str(image_path)
        save_cache(cache)
        return True
    if article["slug"] in cache.get("images", {}):
        print(f"  Image cached for {article['slug']}, checking file...")
        if IMAGE_DIR.exists():
            existing = list(IMAGE_DIR.glob(f"{article['slug']}*"))
            if existing:
                return True

    cc = CATEGORY_COLORS[article["category"]]
    prompt = f"Stock photography style image on the topic of: {article['title']}. Professional photography, natural lighting, suitable for lifestyle website header, high quality, magazine style, {article['category']} theme."

    img_url = call_seedream(prompt)
    if img_url:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        if download_image(img_url, image_path):
            cache.setdefault("images", {})[article["slug"]] = str(image_path)
            save_cache(cache)
            print(f"  Image saved: {image_name}")
            return True
    return False

def render_article_html(article, article_data):
    slug = article["slug"]
    cc = CATEGORY_COLORS[article["category"]]
    image_name = f"{slug}-image.jpg"
    h1_title = article_data.get("h1_title", article["title"])
    seo_title = article_data.get("title", f"{article['title']} | Myers Media")
    meta_desc = article_data.get("description", f"Learn about {article['title']} - comprehensive guide from Myers Media.")
    article_body = article_data.get("article_body_html", "<p>Content coming soon.</p>")
    read_time = article_data.get("read_time", "8")
    page_url = f"https://www.jycsd.com/article/{slug}.html"

    # Insert mid-content ad after the 5th </p>
    body_with_ad = article_body
    p_count = 0
    insert_pos = -1
    for m in re.finditer(r'</p>', article_body):
        p_count += 1
        if p_count == 5:
            insert_pos = m.end()
            break
    if insert_pos > 0:
        mid_ad = f"""</p>

        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-2595917642864488"
             data-ad-slot="6470642127"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{
        }});
        </script>

        <p>"""
        body_with_ad = article_body[:insert_pos] + mid_ad + article_body[insert_pos:]

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
    <meta charset="UTF-8">
<meta name="google-adsense-account" content="ca-pub-2595917642864488">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{seo_title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Myers Media">
    <title>{seo_title}</title>
    <link rel="canonical" href="{page_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{ 'primary': {{ 50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a' }}, 'navy': '#0f1a3c' }},
                    fontFamily: {{ sans: ['Roboto','Arial','Helvetica','sans-serif'], heading: ['Georgia','Times New Roman','serif'] }}
                }}
            }}
        }}
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <style>
        .article-content h2 {{ font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; font-family: Georgia, serif; }}
        .article-content p {{ margin-bottom: 1.25rem; line-height: 1.8; font-size: 1.1rem; color: #374151; }}
        .article-content blockquote {{ border-left: 4px solid #{cc["hex"]}; padding: 1rem 1.5rem; margin: 2rem 0; background: #f8fafc; border-radius: 0 8px 8px 0; font-style: italic; }}
        .article-content ul {{ margin-bottom: 1.25rem; padding-left: 1.5rem; }}
        .article-content li {{ margin-bottom: 0.5rem; line-height: 1.7; }}
    </style>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
    <script>window.dataLayer = window.dataLayer || [];function gtag(){{dataLayer.push(arguments);}}gtag('js', new Date());gtag('config', 'G-GGNWR1X1GV');</script>
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
        <button class="md:hidden text-gray-600 text-2xl">&#9776;</button>
    </div>
</nav>

<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <nav class="text-sm text-gray-400 mb-8">
        <a href="/" class="hover:text-primary-600 transition">Home</a>
        <span class="mx-2">/</span>
        <a href="/#articles" class="hover:text-primary-600 transition">Articles</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{article["title"]}</span>
    </nav>

    <article>
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-heading font-bold text-gray-900 leading-tight mb-4">{h1_title}</h1>
            <div class="flex items-center text-sm text-gray-400 space-x-4">
                <time datetime="2026-05-21">May 21, 2026</time>
                <span>{read_time} min read</span>
            </div>
        </header>

        <div class="mb-10 rounded-2xl overflow-hidden">
            <img src="../images/{image_name}" alt="{article["title"]}" class="w-full h-64 md:h-80 object-cover">
        </div>

        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-2595917642864488"
             data-ad-slot="6968613870"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>

        <div class="article-content">
            {body_with_ad}
        </div>

        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-2595917642864488"
             data-ad-slot="4688206363"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>

    </article>

    <div class="mt-12 p-8 bg-gray-50 rounded-2xl border border-gray-200 text-center">
        <h3 class="text-xl font-bold text-gray-900 mb-2">Explore More on {article["sub_site"]}</h3>
        <p class="text-gray-500 mb-4">Visit our dedicated {article["category"]} site for in-depth guides, expert tips, and the latest updates.</p>
        <a href="{article["sub_url"]}" target="_blank" rel="noopener" class="inline-block bg-primary-700 hover:bg-primary-800 text-white font-bold px-8 py-3 rounded-full text-base transition-colors">
            Visit {article["sub_site"]} →
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
            <p>&copy; 2026 Myers Media. All rights reserved.</p>
        </div>
    </div>
</footer>
</body>
</html>'''
    return html

def generate_card_html(article, article_data=None):
    slug = article["slug"]
    cc = CATEGORY_COLORS[article["category"]]
    image_name = f"{slug}-image.jpg"

    if article_data and "card_description" in article_data:
        desc = article_data["card_description"]
    elif "card_desc" in article:
        desc = article["card_desc"]
    else:
        desc = f"Learn about {article['title']}. Expert guides and practical tips."

    h3_title = article.get("h1_title", article["title"])
    if len(h3_title) > 70:
        h3_title = h3_title[:67] + "..."

    return f"""            <!-- Article Card: {article["category"]} -->
            <a href="article/{slug}.html" class="article-card block bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group">
                <div class="h-48 bg-gray-200 overflow-hidden">
                    <img src="images/{image_name}" alt="{article["title"]}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy">
                </div>
                <div class="p-6">
                    <span class="category-badge inline-block bg-{cc["index_bg"]} text-{cc["index_text_bold"]} text-xs font-bold px-3 py-1 rounded-full mb-3">{article["category"]}</span>
                    <h3 class="text-lg font-bold text-gray-900 mb-2 leading-snug">{h3_title}</h3>
                    <p class="text-sm text-gray-500 leading-relaxed mb-4">{desc}</p>
                    <span class="text-{cc["index_text"]} font-semibold text-sm group-hover:underline">Read More &rarr;</span>
                </div>
            </a>"""

def update_index_html(all_articles_with_data):
    index_path = BASE_DIR / "index.html"
    original = index_path.read_text(encoding="utf-8")

    # 1. Replace Unsplash URLs in existing cards
    for art in EXISTING_ARTICLES:
        local_img = f"images/{art['slug']}-image.jpg"
        original = original.replace(art["unsplash_index"], local_img)

    # 2. Generate ALL card HTML (existing + new)
    all_cards_html = ""
    for article, data in all_articles_with_data:
        all_cards_html += generate_card_html(article, data) + "\n\n"

    # 3. Find and replace the grid content in Featured Articles section
    # First locate the articles section (avoid matching the sites grid)
    articles_section = original.find('<section id="articles"')
    if articles_section == -1:
        print("ERROR: Could not find articles section in index.html")
        return False

    grid_start_marker = '<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">'
    grid_end_marker = '        </div>\n    </div>\n</section>\n\n<!-- Latest from Our Network'

    grid_start = original.find(grid_start_marker, articles_section)
    grid_end = original.find(grid_end_marker)

    if grid_start == -1 or grid_end == -1:
        print("ERROR: Could not find grid markers in index.html")
        return False

    # Replace everything between grid start and grid end
    new_grid_content = f"{grid_start_marker}\n\n{all_cards_html}"
    modified = original[:grid_start] + new_grid_content + original[grid_end:]

    # 4. Replace Unsplash URLs in the article files too
    for art in EXISTING_ARTICLES:
        article_path = ARTICLE_DIR / f"{art['slug']}.html"
        if article_path.exists():
            content = article_path.read_text(encoding="utf-8")
            local_img_article = f"../images/{art['slug']}-image.jpg"
            if art["unsplash_article"] in content:
                content = content.replace(art["unsplash_article"], local_img_article)
                article_path.write_text(content, encoding="utf-8")
                print(f"  Updated image in {art['slug']}.html")

    index_path.write_text(modified, encoding="utf-8")
    return True

def process_existing_articles_images(cache):
    """Generate images for the 6 existing articles"""
    print("\n=== Processing images for 6 existing articles ===")
    success = 0
    for art in EXISTING_ARTICLES:
        print(f"  [{art['slug']}] {art['title']}")
        if generate_image_file(art, cache):
            success += 1
        time.sleep(1)
    return success

def process_new_articles(cache):
    """Generate content + images + HTML for 20 new articles"""
    print("\n=== Generating 20 new articles ===")
    content_ok = 0
    image_ok = 0
    html_ok = 0
    results = []

    for i, art in enumerate(NEW_ARTICLES):
        print(f"\n[{i+1}/20] {art['slug']}: {art['title']}")

        # Step 1: Generate content
        print("  Generating content via DeepSeek...")
        data = generate_article_content(art, cache)
        if not data:
            print("  FAILED content generation, skipping")
            continue
        content_ok += 1

        # Step 2: Generate image
        print("  Generating image via Seedream...")
        if generate_image_file(art, cache):
            image_ok += 1
        time.sleep(1)

        # Step 3: Render HTML
        print("  Rendering HTML...")
        html = render_article_html(art, data)
        article_path = ARTICLE_DIR / f"{art['slug']}.html"
        article_path.write_text(html, encoding="utf-8")
        html_ok += 1
        print(f"  Saved: {article_path.name}")

        results.append((art, data))

    return content_ok, image_ok, html_ok, results

def main():
    print("=" * 60)
    print("  Myers Media Hub Article Generator")
    print("=" * 60)

    os.makedirs(ARTICLE_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    cache = load_cache()
    print(f"Loaded cache: {len(cache.get('articles', {}))} articles, {len(cache.get('images', {}))} images")

    # Step 1: Generate images for 6 existing articles
    existing_images = process_existing_articles_images(cache)

    # Step 2: Generate 20 new articles (content + images + HTML)
    content_ok, image_ok, html_ok, new_results = process_new_articles(cache)

    # Step 3: Update index.html
    print("\n=== Updating index.html ===")
    all_results = []
    for art in EXISTING_ARTICLES:
        all_results.append((art, None))
    all_results.extend(new_results)

    if update_index_html(all_results):
        print("index.html updated successfully!")
    else:
        print("FAILED to update index.html")

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Existing article images generated: {existing_images}/6")
    print(f"  New articles content generated:   {content_ok}/20")
    print(f"  New article images generated:     {image_ok}/20")
    print(f"  New article HTML files rendered:  {html_ok}/20")

    article_files = list(ARTICLE_DIR.glob("article-*.html"))
    image_files = list(IMAGE_DIR.glob("article-*.jpg")) + list(IMAGE_DIR.glob("article-*.png"))
    print(f"\n  Total article files: {len(article_files)}")
    print(f"  Total image files:   {len(image_files)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
