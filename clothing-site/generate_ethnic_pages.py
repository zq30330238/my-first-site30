#!/usr/bin/env python3
"""Generate 56 ethnic group HTML pages from ethnic_data.json."""

import json
import os
import random
import glob

DATA_FILE = os.path.join(os.path.dirname(__file__), "ethnic_data.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "chinese", "56-ethnic-groups")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs(OUTPUT_DIR, exist_ok=True)

UNSPLASH_FALLBACKS = [
    "photo-1583391733956-3750e0ff4e8b?w=1200&h=600&fit=crop",
    "photo-1590736969955-71cc94901144?w=800&h=500&fit=crop",
    "photo-1607082349566-187342175e2f?w=800&h=500&fit=crop",
]

SITE_URL = "https://clothing.jycsd.com"
SITE_NAME = "Myers Fashion"
PUB_DATE = "2026-05-26"

AD_SCRIPT = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin></script>'
ADSENSE_META = '<meta name="google-adsense-account" content="ca-pub-2595917642864488">'

CATEGORIES_LINKS = [
    ("All 56 Ethnic Groups", "/chinese/56-ethnic-groups/"),
    ("Dynasty Fashion", "/chinese/dynasty-evolution/"),
    ("Fashion Week Trends", "/western/fashion-week-trends/"),
    ("Classic Pieces", "/western/classic-pieces/"),
    ("East vs West", "/compare/"),
]

FOOTER_NETWORK = [
    ("Main Site", "https://www.jycsd.com"),
    ("Healthy Living", "https://healthy.jycsd.com"),
    ("Pet Care", "https://pets.jycsd.com"),
    ("Home & Garden", "https://home.jycsd.com"),
    ("Personal Finance", "https://finance.jycsd.com"),
    ("Tech & Digital", "https://tech.jycsd.com"),
    ("Travel Guide", "https://travel.jycsd.com"),
    ("Entertainment", "https://entertainment.jycsd.com"),
    ("Auto World", "https://auto.jycsd.com"),
    ("Moto Sports", "https://moto.jycsd.com"),
    ("Food & Recipes", "https://food.jycsd.com"),
]

FOOTER_CONTENT = [
    ("Healthy Living", "https://healthy.jycsd.com"),
    ("Pet Care", "https://pets.jycsd.com"),
    ("Home & Garden", "https://home.jycsd.com"),
    ("Personal Finance", "https://finance.jycsd.com"),
    ("Tech & Digital", "https://tech.jycsd.com"),
    ("Travel Guide", "https://travel.jycsd.com"),
]

FOOTER_GAMES = [
    ("Games Hub", "https://games.jycsd.com"),
    ("Anime Hub", "https://anime.jycsd.com"),
    ("Dragon Ball Wiki", "https://dragonball.jycsd.com"),
    ("Naruto Wiki", "https://naruto.jycsd.com"),
    ("One Piece Wiki", "https://onepiece.jycsd.com"),
    ("Valorant Wiki", "https://valorant.jycsd.com"),
    ("Fortnite Wiki", "https://fortnite.jycsd.com"),
    ("LoL Wiki", "https://lol.jycsd.com"),
    ("Elden Ring Wiki", "https://eldenring.jycsd.com"),
    ("Minecraft Wiki", "https://minecraft.jycsd.com"),
]


def esc(text):
    """Escape text for HTML attribute/content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def make_meta_description(ethnic):
    """Generate 150-160 char meta description."""
    summary = ethnic["clothing_summary"]
    # Trim to ~155 chars at sentence boundary
    if len(summary) <= 155:
        return summary
    # Try sentence boundary
    for delim in [". ", "! ", "? "]:
        idx = summary.rfind(delim, 0, 155)
        if idx > 80:
            return summary[: idx + 1]
    # Fallback: trim to word boundary
    idx = summary.rfind(" ", 0, 155)
    return summary[:idx] + "..."


def make_title(ethnic):
    """Generate title: Name_en (Name_cn) Traditional Clothing: Key Feature — Myers Fashion"""
    return f"{ethnic['name_en']} ({ethnic['name_cn']}) Traditional Clothing: {ethnic['key_features'][0][:60].rstrip('.')} — Myers Fashion"


def make_keywords(ethnic):
    """Generate meta keywords."""
    parts = [
        ethnic["name_en"].split("(")[0].strip().replace(" ", " "),
        ethnic["name_cn"],
        "traditional clothing",
        "ethnic costume",
        "Chinese ethnic minorities",
        "56 ethnic groups",
    ]
    return ", ".join(parts)


def make_tags(ethnic):
    """Generate 6-8 tag strings."""
    base = [ethnic["name_en"].split("(")[0].strip()]
    cn = ethnic["name_cn"]

    # Extract keywords from key_features
    kw = set()
    for feat in ethnic["key_features"]:
        words = feat.split()[:4]
        for w in words:
            w_clean = w.strip(",. ")
            if len(w_clean) > 3 and w_clean.lower() not in ("with", "that", "from", "their", "this", "have", "been"):
                kw.add(w_clean)

    # Add specific cultural terms
    culture_terms = [
        "Embroidery", "Silver", "Traditional Dress", "Indigo", "Beadwork",
        "Brocade", "Silk", "Headdress", "Festival Attire", "Intangible Heritage",
        "Handwoven", "Ethnic Fashion", "Textile Art", "Cultural Heritage",
    ]
    for t in culture_terms:
        if any(t.lower() in f.lower() for f in ethnic["key_features"]) or t.lower() in ethnic["clothing_summary"].lower():
            kw.add(t)

    kw_list = list(kw)
    random.shuffle(kw_list)
    tags = [base[0]]
    if cn and len(tags) < 8:
        tags.append(cn)
    tags.extend(kw_list[:6])
    return tags[:8]


def generate_html(key, ethnic, all_keys, related_sample):
    """Generate full HTML page for one ethnic group."""
    name_en = ethnic["name_en"]
    name_cn = ethnic["name_cn"]
    title = make_title(ethnic)
    meta_desc = make_meta_description(ethnic)
    keywords = make_keywords(ethnic)
    page_url = f"{SITE_URL}/chinese/56-ethnic-groups/{key}.html"
    img_hero_id = random.choice(UNSPLASH_FALLBACKS)
    img_hero = f"https://images.unsplash.com/{img_hero_id}"
    img_og = f"https://images.unsplash.com/{img_hero_id.split('?')[0]}?w=1200&h=630&fit=crop"
    img_inline1 = f"https://images.unsplash.com/{random.choice(UNSPLASH_FALLBACKS)}"
    img_inline2 = f"https://images.unsplash.com/{random.choice(UNSPLASH_FALLBACKS)}"

    # Build key features HTML
    features_html = "<ul class=\"list-disc pl-6 mb-4 space-y-2 text-gray-700\">\n"
    for feat in ethnic["key_features"]:
        features_html += f"                <li>{esc(feat)}</li>\n"
    features_html += "            </ul>"

    # Build main garments section
    main_garments_html = ""
    mg = ethnic.get("main_garments", "")
    if mg:
        main_garments_html = f"""
            <h2>Traditional Garments</h2>
            <p>{esc(mg)}</p>"""

    # Build headwear section
    headwear_html = ""
    hw = ethnic.get("headwear", "")
    if hw:
        headwear_html = f"""
            <h2>Headwear and Adornments</h2>
            <p>{esc(hw)}</p>"""

    # Build embroidery section
    emb_html = ""
    emb = ethnic.get("embroidery", "")
    if emb:
        emb_html = f"""
            <h2>Embroidery and Decorative Arts</h2>
            <p>{esc(emb)}</p>"""

    # Build colors section
    colors_html = ""
    col = ethnic.get("colors", "")
    if col:
        colors_html = f"""
            <h2>Color Symbolism</h2>
            <p>{esc(col)}</p>"""

    # Build festival section
    fest_html = ""
    fest = ethnic.get("festival_attire", "")
    if fest:
        fest_html = f"""
            <h2>Festival Attire</h2>
            <p>{esc(fest)}</p>"""

    # Build modern influence section
    modern_html = ""
    mod = ethnic.get("modern_influence", "")
    if mod:
        modern_html = f"""
            <h2>Modern Influence and Preservation</h2>
            <p>{esc(mod)}</p>"""

    # Blockquote
    bq = ethnic.get("blockquote", "")
    blockquote_html = ""
    if bq:
        blockquote_html = f"""
            <blockquote>
                <p>{esc(bq)}</p>
            </blockquote>"""

    # Quick facts
    facts_html = ""
    region = esc(ethnic.get("region", "China"))
    pop = esc(ethnic.get("population", "Unknown"))
    # Extract 1-2 key crafts from key_features
    craft_words = []
    for feat in ethnic["key_features"]:
        for w in ["embroidery", "weaving", "silver", "beadwork", "batik", "brocade", "dyeing", "indigo", "applique", "needlework"]:
            if w in feat.lower() and w not in craft_words:
                craft_words.append(w.capitalize())
    craft_str = ", ".join(craft_words[:3]) if craft_words else "Textile arts"
    facts_html = f"""
                <div class="bg-gray-50 rounded-xl p-6">
                    <h3 class="font-bold text-lg mb-4 accent-text">Quick Facts</h3>
                    <ul class="space-y-3 text-sm text-gray-700">
                        <li><strong>Population:</strong> {pop}</li>
                        <li><strong>Major Regions:</strong> {region[:80]}{'...' if len(region) > 80 else ''}</li>
                        <li><strong>Language:</strong> {name_cn}</li>
                        <li><strong>Key Craft:</strong> {craft_str}</li>
                    </ul>
                </div>"""

    # Related ethnic groups
    related_html = ""
    if related_sample:
        items = "".join(
            f'<li><a href="/chinese/56-ethnic-groups/{rk}.html" class="text-gray-600 hover:text-gray-900 transition-colors flex items-center gap-2"><span class="w-1.5 h-1.5 accent-bg rounded-full"></span>{esc(data[rk]["name_en"].split("(")[0].strip())} ({data[rk]["name_cn"]})</a></li>\n                    '
            for rk in related_sample
        )
        related_html = f"""
                <div class="bg-gray-50 rounded-xl p-6">
                    <h3 class="font-bold text-lg mb-4 accent-text">Related Ethnic Groups</h3>
                    <ul class="space-y-3 text-sm">
                        {items}
                    </ul>
                </div>"""

    # Tags
    tags = make_tags(ethnic)
    tags_html = "".join(
        f'<a href="/chinese/56-ethnic-groups/" class="inline-block bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm px-3 py-1 rounded-full transition-colors">{esc(t)}</a>\n                    '
        for t in tags
    )

    # Breadcrumb label
    breadcrumb_label = esc(name_en.split("(")[0].strip())

    # Footer select options
    footer_network_opts = "".join(f'<option value="{url}">{label}</option>\n                    ' for label, url in FOOTER_NETWORK)
    footer_content_opts = "".join(f'<option value="{url}">{label}</option>\n                    ' for label, url in FOOTER_CONTENT)
    footer_games_opts = "".join(f'<option value="{url}">{label}</option>\n                    ' for label, url in FOOTER_GAMES)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(meta_desc)}">
    <meta name="keywords" content="{esc(keywords)}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{esc(meta_desc[:70])}">
    <meta property="og:description" content="{esc(meta_desc[:155])}">
    <meta property="og:image" content="{img_og}">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="en_US">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="{SITE_NAME}">
    <meta name="twitter:card" content="summary_large_image">
    {ADSENSE_META}
    <link rel="canonical" href="{page_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    {AD_SCRIPT}
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-GGNWR1X1GV');
    </script>
    <style>
        :root {{ --accent: #c41e3a; --accent-light: #fef2f2; }}
        body {{ font-family: 'Segoe UI', Roboto, Arial, sans-serif; }}
        .accent-text {{ color: var(--accent); }}
        .accent-bg {{ background-color: var(--accent); }}
        .accent-border {{ border-color: var(--accent); }}
        .hover-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }}
        .article-content h2 {{ color: var(--accent); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700; }}
        .article-content h3 {{ font-size: 1.2rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }}
        .article-content p {{ margin-bottom: 1rem; line-height: 1.8; color: #374151; }}
        .article-content blockquote {{ border-left: 4px solid var(--accent); background: var(--accent-light); padding: 1.25rem 1.5rem; margin: 1.5rem 0; border-radius: 0 0.5rem 0.5rem 0; font-style: italic; color: #4b5563; }}
    </style>
</head>
<body class="bg-white text-gray-900 min-h-screen">

<!-- Header -->
<header class="bg-white border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <a href="/" class="text-2xl font-bold accent-text tracking-tight">Myers Fashion</a>
        <nav class="hidden md:flex space-x-6 text-sm font-medium text-gray-600">
            <a href="/chinese/" class="hover:text-gray-900 transition-colors">Chinese</a>
            <a href="/western/" class="hover:text-gray-900 transition-colors">Western</a>
            <a href="/compare/" class="hover:text-gray-900 transition-colors">Compare</a>
            <a href="/about.html" class="hover:text-gray-900 transition-colors">About</a>
        </nav>
    </div>
</header>

<!-- Breadcrumb -->
<nav class="bg-gray-50 border-b border-gray-200" aria-label="Breadcrumb">
    <div class="max-w-7xl mx-auto px-4 py-3 text-sm text-gray-500">
        <a href="/" class="hover:text-gray-700 transition-colors">Home</a>
        <span class="mx-2">/</span>
        <a href="/chinese/" class="hover:text-gray-700 transition-colors">Chinese</a>
        <span class="mx-2">/</span>
        <a href="/chinese/56-ethnic-groups/" class="hover:text-gray-700 transition-colors">56 Ethnic Groups</a>
        <span class="mx-2">/</span>
        <span class="text-gray-900 font-medium">{breadcrumb_label}</span>
    </div>
</nav>

<!-- Hero -->
<section class="relative h-[400px] md:h-[500px] overflow-hidden">
    <img src="{img_hero}" alt="{esc(name_en)} traditional clothing" loading="eager" class="w-full h-full object-cover">
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
    <div class="absolute bottom-0 left-0 right-0 max-w-7xl mx-auto px-4 pb-12">
        <p class="text-sm uppercase tracking-widest text-red-300 mb-2">56 Ethnic Groups</p>
        <h1 class="text-3xl md:text-5xl font-bold text-white leading-tight">{esc(ethnic['clothing_summary'][:80])}{'...' if len(ethnic['clothing_summary']) > 80 else ''}</h1>
    </div>
</section>

<!-- Main Content + Sidebar -->
<div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col lg:flex-row gap-10">

        <!-- Article -->
        <article class="flex-1 max-w-3xl article-content">

            <p class="text-lg text-gray-600 leading-relaxed mb-8">{esc(ethnic['clothing_summary'])}</p>

            <h2>Key Features of {esc(name_en.split('(')[0].strip())} Attire</h2>
            {features_html}

            {main_garments_html}

            {headwear_html}

            <figure class="my-8">
                <img src="{img_inline1}" alt="{esc(name_en)} traditional clothing and textile details" loading="lazy" class="w-full rounded-lg">
                <figcaption class="text-sm text-gray-500 mt-2 text-center">{esc(name_en)} traditional garments — details and craftsmanship.</figcaption>
            </figure>

            {emb_html}

            {blockquote_html}

            {colors_html}

            {fest_html}

            <figure class="my-8">
                <img src="{img_inline2}" alt="{esc(name_en)} festival attire and cultural dress" loading="lazy" class="w-full rounded-lg">
                <figcaption class="text-sm text-gray-500 mt-2 text-center">{esc(name_en)} festival attire and ceremonial clothing.</figcaption>
            </figure>

            {modern_html}

            <!-- Fun Fact -->
            <div class="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg my-8">
                <p class="text-sm font-semibold text-amber-800 mb-1">Did You Know?</p>
                <p class="text-sm text-amber-700">{esc(ethnic.get('fun_fact', ''))}</p>
            </div>

            <!-- Tags -->
            <div class="mt-12 pt-8 border-t border-gray-200">
                <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Tags</h3>
                <div class="flex flex-wrap gap-2">
                    {tags_html}
                </div>
            </div>

        </article>

        <!-- Sidebar -->
        <aside class="w-full lg:w-80 shrink-0">
            <div class="sticky top-24 space-y-8">

                <!-- Categories -->
                <div class="bg-gray-50 rounded-xl p-6">
                    <h3 class="font-bold text-lg mb-4 accent-text">Categories</h3>
                    <ul class="space-y-3 text-sm">
                        {''.join(f'<li><a href="{url}" class="text-gray-600 hover:text-gray-900 transition-colors flex items-center gap-2"><span class="w-1.5 h-1.5 accent-bg rounded-full"></span>{esc(label)}</a></li>\n                        ' for label, url in CATEGORIES_LINKS)}
                    </ul>
                </div>

                {related_html}

                {facts_html}

            </div>
        </aside>

    </div>
</div>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-400 py-12 mt-12">
    <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
                <h3 class="text-white font-bold text-lg mb-3">Myers Fashion</h3>
                <p class="text-sm leading-relaxed">Your comprehensive guide to traditional Chinese clothing and global fashion trends. Part of the Myers Media network.</p>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Network</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
                    <option value="">— Myers Media Network —</option>
                    {footer_network_opts}
                </select>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Content Sites</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
                    <option value="">— Lifestyle —</option>
                    {footer_content_opts}
                </select>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Game & Anime Wikis</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
                    <option value="">— Game & Anime —</option>
                    {footer_games_opts}
                </select>
            </div>
        </div>
        <div class="border-t border-gray-800 pt-6 flex flex-col md:flex-row justify-between text-sm">
            <p>&copy; 2026 Myers Fashion. All rights reserved.</p>
            <div class="flex gap-4 mt-2 md:mt-0">
                <a href="/about.html" class="hover:text-white transition-colors">About</a>
                <a href="/contact.html" class="hover:text-white transition-colors">Contact</a>
                <a href="/privacy-policy.html" class="hover:text-white transition-colors">Privacy</a>
                <a href="/cookie-policy.html" class="hover:text-white transition-colors">Cookies</a>
                <a href="/terms.html" class="hover:text-white transition-colors">Terms</a>
            </div>
        </div>
    </div>
</footer>

<!-- JSON-LD: Organization -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Myers Media",
  "url": "{SITE_URL}",
  "description": "Traditional Chinese clothing and global fashion guide",
  "foundingDate": "2024",
  "founder": {{ "@type": "Person", "name": "Jordan Myers" }},
  "sameAs": ["https://www.jycsd.com"]
}}
</script>

<!-- JSON-LD: WebSite -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{SITE_NAME}",
  "url": "{SITE_URL}",
  "description": "Your comprehensive guide to traditional Chinese clothing and global fashion trends.",
  "publisher": {{ "@type": "Organization", "name": "Myers Media" }}
}}
</script>

<!-- JSON-LD: Article -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{esc(meta_desc[:80])}",
  "description": "{esc(meta_desc[:155])}",
  "image": "{img_og}",
  "author": {{ "@type": "Organization", "name": "Myers Fashion" }},
  "publisher": {{ "@type": "Organization", "name": "Myers Media" }},
  "datePublished": "{PUB_DATE}",
  "dateModified": "{PUB_DATE}",
  "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{page_url}" }}
}}
</script>

</body>
</html>
"""
    return html


# Generation loop
keys = list(data.keys())
random.seed(42)

count = 0
for key in keys:
    ethnic = data[key]

    # Pick 5 random related groups (excluding current)
    others = [k for k in keys if k != key]
    random.shuffle(others)
    related_sample = others[:5]

    html = generate_html(key, ethnic, keys, related_sample)

    outpath = os.path.join(OUTPUT_DIR, f"{key}.html")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)
    count += 1
    print(f"  [{count}/56] {key} -> {key}.html")

print(f"\nGenerated {count}/56 pages to {OUTPUT_DIR}")
