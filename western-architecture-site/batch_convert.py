#!/usr/bin/env python3
"""
Batch convert all 52 detail pages to the new template format.
Template: castles/gothic-castle.html
"""

import os
import re
import sys
from bs4 import BeautifulSoup, Tag, NavigableString

BASE_DIR = r"d:\AI网站文件夹\western-architecture-site"
CDN = "https://global-architecture.jycsd.com"
SITE_NAME = "Myers Architecture"

# Category config: directory -> (parent_label, parent_link, nav_active_index)
CATEGORIES = {
    "castles":              ("Castles & Palaces",     "/castles/",               "Castles"),
    "residential":          ("Residential",            "/residential/",          "Residential"),
    "architectural-styles": ("Architectural Styles",   "/architectural-styles/", "Styles"),
    "interior-styles":      ("Interior Styles",        "/interior-styles/",      "Interiors"),
    "landmarks":            ("Landmarks",              "/landmarks/",            "Landmarks"),
    "compare":              ("Compare",                "/compare/",              "Compare"),
}

NAV_LINKS = [
    ("Home",         "/"),
    ("Castles",      "/castles/"),
    ("Residential",  "/residential/"),
    ("Styles",       "/architectural-styles/"),
    ("Interiors",    "/interior-styles/"),
    ("Landmarks",    "/landmarks/"),
    ("Compare",      "/compare/"),
    ("About",        "/about"),
]

# Footer blocks — copied exactly from gothic-castle.html
FOOTER_HTML = r"""<footer class="bg-gray-900 text-gray-300 mt-16">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-white text-lg font-bold mb-3">Myers Architecture</h3>
                <p class="text-sm leading-relaxed">Exploring the beauty and diversity of global architectural traditions, from medieval castles to modernist masterpieces.</p>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Legal</h3>
                <ul class="space-y-2 text-sm">
                    <li><a href="/privacy-policy" class="hover:text-white transition-colors">Privacy Policy</a></li>
                    <li><a href="/terms" class="hover:text-white transition-colors">Terms of Service</a></li>
                    <li><a href="/cookie-policy" class="hover:text-white transition-colors">Cookie Policy</a></li>
                    <li><a href="/contact" class="hover:text-white transition-colors">Contact</a></li>
                </ul>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Our Network</h3>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-[#2c3e50] cursor-pointer">
                    <option value="">-- Network --</option>
                    <option value="https://www.jycsd.com">Main Site</option>
                    <option value="https://games.jycsd.com">Game Guides</option>
                    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-[#2c3e50] cursor-pointer">
                    <option value="">-- Content Sites --</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://auto.jycsd.com">AutoPulse</option>
                    <option value="https://moto.jycsd.com">MotoPulse</option>
                    <option value="https://food.jycsd.com">FlavorFusion</option>
                    <option value="https://entertainment.jycsd.com">PopCulture HQ</option>
                    <option value="https://clothing.jycsd.com">Myers Fashion</option>
                    <option value="https://chinese-architecture.jycsd.com">Chinese Architecture</option>
                    <option value="https://global-architecture.jycsd.com">Global Architecture</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-[#2c3e50] cursor-pointer">
                    <option value="">-- Game &amp; Anime Wikis --</option>
                    <option value="https://dragonball.jycsd.com">Dragon Ball Wiki</option>
                    <option value="https://naruto.jycsd.com">Naruto Wiki</option>
                    <option value="https://onepiece.jycsd.com">One Piece Wiki</option>
                    <option value="https://valorant.jycsd.com">Valorant Wiki</option>
                    <option value="https://fortnite.jycsd.com">Fortnite Wiki</option>
                    <option value="https://lol.jycsd.com">LoL Wiki</option>
                    <option value="https://eldenring.jycsd.com">Elden Ring Wiki</option>
                    <option value="https://minecraft.jycsd.com">Minecraft Wiki</option>
                    <option value="https://bleach.jycsd.com">Bleach Wiki</option>
                    <option value="https://hxh.jycsd.com">Hunter x Hunter Wiki</option>
                    <option value="https://jjk.jycsd.com">Jujutsu Kaisen Wiki</option>
                    <option value="https://jojo.jycsd.com">JoJo Wiki</option>
                    <option value="https://sao.jycsd.com">Sword Art Online Wiki</option>
                    <option value="https://tokyoghoul.jycsd.com">Tokyo Ghoul Wiki</option>
                    <option value="https://aot.jycsd.com">Attack on Titan Wiki</option>
                </select>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Contact</h3>
                <ul class="space-y-2 text-sm">
                    <li><a href="mailto:contact@jycsd.com" class="hover:text-white transition-colors">contact@jycsd.com</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-700 pt-6 text-center text-sm">
            <p>&copy; 2026 Myers Architecture. All rights reserved.</p>
        </div>
    </div>
</footer>"""


STYLE_HTML = """<style>
        body { font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
        .article-content p { margin-bottom: 1.25rem; font-size: 1.0625rem; line-height: 1.8; color: #374151; }
        .article-content h2 { font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; border-left: 4px solid #2c3e50; padding-left: 1rem; }
        .article-content h3 { font-size: 1.375rem; font-weight: 600; color: #1f2937; margin-top: 1.75rem; margin-bottom: 0.75rem; }
        .article-content blockquote { border-left: 4px solid #2c3e50; background-color: #f0f4f8; padding: 1rem 1.5rem; margin: 2rem 0; border-radius: 0 0.5rem 0.5rem 0; font-style: italic; color: #4b5563; }
        .article-content ul, .article-content ol { margin-bottom: 1.25rem; padding-left: 1.5rem; font-size: 1.0625rem; line-height: 1.8; color: #374151; }
        .article-content li { margin-bottom: 0.5rem; }
        .article-content a { color: #2c3e50; text-decoration: underline; }
        .hero-title { text-shadow: 0 2px 12px rgba(0,0,0,0.7); }
    </style>"""


def build_nav_html(active_section):
    """Build the header nav HTML with the correct active state."""
    lines = []
    lines.append("""<header class="sticky top-0 z-50 bg-white/95 backdrop-blur shadow-sm border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <a href="/" class="text-xl font-bold text-gray-900 tracking-tight">Myers <span class="text-[#2c3e50]">Architecture</span></a>
            <nav class="hidden md:flex space-x-8 text-sm font-medium">""")

    for label, href in NAV_LINKS:
        if label == active_section:
            cls = 'text-[#2c3e50] font-semibold border-b-2 border-[#2c3e50]'
        else:
            cls = 'text-gray-700 hover:text-[#2c3e50] transition'
        lines.append(f'                <a href="{href}" class="{cls}">{label}</a>')

    lines.append("""            </nav>
            <button id="menu-btn" class="md:hidden p-2 rounded hover:bg-gray-100" aria-label="Menu">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
        </div>
        <div id="mobile-menu" class="hidden md:hidden pb-4 border-t border-gray-100 pt-2">""")

    for label, href in NAV_LINKS:
        if label == active_section:
            cls = 'text-[#2c3e50] font-semibold'
        else:
            cls = 'text-gray-700'
        lines.append(f'            <a href="{href}" class="block py-2 text-sm {cls}">{label}</a>')

    lines.append("""        </div>
    </div>
</header>
<script>
document.getElementById('menu-btn')?.addEventListener('click', function(){
    var m = document.getElementById('mobile-menu');
    if(m) m.classList.toggle('hidden');
});
</script>""")

    return '\n'.join(lines)


def extract_old_page(filepath):
    """Extract all needed data from an old-format page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # --- Title ---
    title_tag = soup.find('title')
    page_title = title_tag.get_text(strip=True) if title_tag else ''

    # --- Meta description ---
    meta_desc = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag['content']

    # --- H1 ---
    h1_tag = soup.find('h1')
    h1_text = h1_tag.get_text(strip=True) if h1_tag else page_title

    # --- Canonical path (for og:url) ---
    canonical_tag = soup.find('link', rel='canonical')
    canonical_path = ''
    if canonical_tag and canonical_tag.get('href'):
        canonical_path = canonical_tag['href']

    # --- Base image name from hero img ---
    hero_img = soup.select_one('section img')
    base_img = ''
    if hero_img and hero_img.get('src'):
        src = hero_img['src']
        m = re.search(r'/([^/]+?)_hero\.jpg', src)
        if m:
            base_img = m.group(1)

    # --- Hero image URL ---
    hero_url = hero_img['src'] if hero_img and hero_img.get('src') else ''

    # --- Detail image (img before article-content, outside article-content div) ---
    detail_url = ''
    article_content_div = soup.find('div', class_='article-content')
    if article_content_div:
        # Find the img element just before article-content, within the same parent
        parent = article_content_div.parent
        if parent:
            prev = article_content_div.find_previous_sibling('img')
            if prev and prev.get('src'):
                detail_url = prev['src']

    if not detail_url:
        # fallback: find any img with _detail in src
        detail_img = soup.find('img', src=re.compile(r'_detail\.jpg'))
        if detail_img:
            detail_url = detail_img['src']

    # --- More image (img after article-content, outside article-content div) ---
    more_url = ''
    if article_content_div:
        parent = article_content_div.parent
        if parent:
            nxt = article_content_div.find_next_sibling('img')
            if nxt and nxt.get('src'):
                more_url = nxt['src']

    if not more_url:
        # fallback
        more_img = soup.find('img', src=re.compile(r'_more\.jpg'))
        if more_img:
            more_url = more_img['src']

    # --- Article body: inner HTML of article-content div ---
    article_body = ''
    if article_content_div:
        # Decode contents to get inner HTML
        article_body = ''.join(str(c) for c in article_content_div.contents)

    # --- Related articles section: the grid div with class grid-cols- ---
    related_html = ''
    # Find the grid div that's inside the related articles section
    # In old pages: <section class="max-w-7xl..."><h2>Related Articles</h2><div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
    related_section = soup.find('section', class_=re.compile(r'max-w-7xl'))
    if related_section:
        grid = related_section.find('div', class_=re.compile(r'grid-cols-'))
        if grid:
            related_html = str(grid)
        else:
            # Try finding by h2 text
            for h2 in related_section.find_all('h2'):
                if 'Related' in h2.get_text():
                    nxt = h2.find_next_sibling('div')
                    if nxt and nxt.get('class') and any('grid' in c for c in nxt.get('class', [])):
                        related_html = str(nxt)
                    break

    # --- Old breadcrumb category text ---
    category_text = ''
    breadcrumb_nav = soup.find('nav', class_=re.compile(r'max-w-7xl'))
    if breadcrumb_nav:
        # The last li with class text-gray-500 has the category
        lis = breadcrumb_nav.find_all('li')
        for li in lis:
            if li.get('class') and 'text-gray-500' in li.get('class'):
                category_text = li.get_text(strip=True)
                break

    # Also check for badge text
    if not category_text:
        badge = soup.find('span', class_=re.compile(r'rounded-full'))
        if badge:
            category_text = badge.get_text(strip=True)

    # Determine category from directory
    rel_path = os.path.relpath(filepath, BASE_DIR)
    dir_name = rel_path.split(os.sep)[0]

    if dir_name in CATEGORIES:
        parent_label, parent_link, nav_active = CATEGORIES[dir_name]
    else:
        parent_label = category_text or dir_name.capitalize()
        parent_link = '/' + dir_name + '/'
        nav_active = dir_name.capitalize()

    # Build clean URL path (no .html)
    rel_path_no_ext = re.sub(r'\.html$', '', rel_path).replace('\\', '/')
    page_url = f"{CDN}/{rel_path_no_ext}"

    # Description for hero (use meta description)
    hero_desc = meta_desc

    return {
        'page_title': page_title,
        'meta_desc': meta_desc,
        'h1_text': h1_text,
        'hero_url': hero_url,
        'detail_url': detail_url,
        'more_url': more_url,
        'article_body': article_body,
        'related_html': related_html,
        'parent_label': parent_label,
        'parent_link': parent_link,
        'nav_active': nav_active,
        'base_img': base_img,
        'page_url': page_url,
        'hero_desc': hero_desc,
    }


def generate_new_html(data):
    """Generate new template HTML from extracted data."""
    pt = data['page_title']
    md = data['meta_desc']
    h1 = data['h1_text']
    hero_url = data['hero_url']
    detail_url = data['detail_url']
    more_url = data['more_url']
    body = data['article_body']
    related = data['related_html']
    parent_label = data['parent_label']
    parent_link = data['parent_link']
    nav_active = data['nav_active']
    page_url = data['page_url']
    hero_desc = data['hero_desc']

    # Sanitize page title for JSON-LD
    pt_json = pt.replace(' \\', ' ').replace('"', '\\"').replace('—', '-')
    # Extract headline part for JSON-LD (before " — Myers Architecture")
    headline = pt.replace(' — Myers Architecture', '').replace(' - Myers Architecture', '')

    nav_html = build_nav_html(nav_active)

    # Update related links: remove .html extension
    if related:
        related = re.sub(r'href="([^"]+)\.html"', r'href="\1"', related)

    # Build hero alt text from h1
    hero_alt = h1.replace('"', '&quot;')

    # Build the hero section
    hero_section = f"""<!-- Hero -->
<section class="relative h-[40vh] min-h-[320px] overflow-hidden">
    <img src="{hero_url}" alt="{hero_alt}" class="absolute inset-0 w-full h-full object-cover">
    <div class="relative z-10 h-full flex flex-col justify-end pb-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
        <h1 class="hero-title text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-3 leading-tight">{h1}</h1>
        <p class="hero-title text-lg sm:text-xl text-white/90 max-w-3xl">{md}</p>
    </div>
</section>"""

    # Build detail figure
    detail_html = ''
    if detail_url:
        detail_html = f"""    <!-- detail image -->
    <figure class="my-10">
        <img src="{detail_url}" alt="{hero_alt}" class="w-full rounded-lg object-cover" style="max-height:600px">
        <figcaption class="text-sm text-gray-400 mt-3 text-center">A detailed view of {h1}. <em>Source: Myers Architecture Collection</em></figcaption>
    </figure>"""

    # Build more figure (placed before related articles, after article body)
    more_html = ''
    if more_url:
        more_html = f"""    <!-- more image -->
    <figure class="my-10">
        <img src="{more_url}" alt="{hero_alt}" class="w-full rounded-lg object-cover" style="max-height:600px">
        <figcaption class="text-sm text-gray-400 mt-3 text-center">Additional perspective of {h1}.</figcaption>
    </figure>"""

    # Build related articles section
    related_section_html = ''
    if related:
        related_section_html = f"""    <!-- Related Articles -->
    <div class="border-t border-gray-200 pt-10 mt-10">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Explore More {parent_label}</h2>
        {related}
    </div>"""
    else:
        related_section_html = f"""    <!-- Related Articles -->
    <div class="border-t border-gray-200 pt-10 mt-10">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Explore More {parent_label}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div class="p-4 text-gray-500 text-sm">Related articles coming soon.</div>
        </div>
    </div>"""

    # Clean body: fix image links inside body (they might use relative paths), remove old ad divs
    body = re.sub(r'<div class="my-8 p-6 bg-gray-100 rounded-lg.*?</div>', '', body, flags=re.DOTALL)

    # Build the main content
    main_content = f"""<main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="article-content">

    {body}

    {detail_html}

    {more_html}

    </div>

{related_section_html}
</main>"""

    # Build the complete HTML
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pt}</title>
    <meta name="description" content="{md}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{page_url}">
    <meta property="og:title" content="{pt}">
    <meta property="og:description" content="{md}">
    <meta property="og:image" content="{hero_url}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Myers Architecture">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{pt}">
    <meta name="twitter:description" content="{md}">
    <meta name="twitter:image" content="{hero_url}">
    <meta name="google-adsense-account" content="ca-pub-2595917642864488">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
    <script>window.dataLayer = window.dataLayer || []; function gtag(){{dataLayer.push(arguments);}} gtag('js', new Date()); gtag('config', 'G-GGNWR1X1GV');</script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config = {{ theme: {{ extend: {{ colors: {{ accent: '#2c3e50', 'accent-light': '#f0f4f8' }} }} }} }}</script>
    {STYLE_HTML}
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "{headline}",
        "image": "{hero_url}",
        "datePublished": "2026-05-27",
        "author": {{ "@type": "Organization", "name": "Myers Architecture" }},
        "publisher": {{ "@type": "Organization", "name": "Myers Architecture", "logo": {{ "@type": "ImageObject", "url": "{CDN}/images/index_hero.jpg" }} }}
    }}
    </script>
</head>
<body class="bg-white text-gray-800 antialiased">

{nav_html}

{hero_section}

<nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
    <ol class="flex flex-wrap items-center gap-2 text-sm text-gray-400">
        <li><a href="/" class="hover:text-[#2c3e50]">Home</a></li>
        <li>/</li>
        <li><a href="{parent_link}" class="hover:text-[#2c3e50]">{parent_label}</a></li>
        <li>/</li>
        <li class="text-gray-600">{h1}</li>
    </ol>
</nav>

{main_content}

{FOOTER_HTML}
</body>
</html>"""

    return full_html


def main():
    pages = [
        # Castles (6)
        "castles/baroque-palace.html",
        "castles/edinburgh-castle.html",
        "castles/medieval-fortress.html",
        "castles/neuschwanstein.html",
        "castles/renaissance-castle.html",
        "castles/windsor-castle.html",
        # Residential (10)
        "residential/american-suburban.html",
        "residential/apartment-types.html",
        "residential/english-cottage.html",
        "residential/french-chateau.html",
        "residential/japanese-ikkodate.html",
        "residential/mediterranean-villa.html",
        "residential/modern-mansion.html",
        "residential/scandinavian-cabin.html",
        "residential/townhouse-europe.html",
        "residential/victorian-house.html",
        # Architectural Styles (11)
        "architectural-styles/art-deco.html",
        "architectural-styles/art-nouveau.html",
        "architectural-styles/baroque-rococo.html",
        "architectural-styles/bauhaus-modernism.html",
        "architectural-styles/brutalist.html",
        "architectural-styles/classical-greek-roman.html",
        "architectural-styles/deconstructivism.html",
        "architectural-styles/gothic-architecture.html",
        "architectural-styles/neoclassical.html",
        "architectural-styles/postmodern.html",
        "architectural-styles/renaissance-architecture.html",
        # Interior Styles (10)
        "interior-styles/bohemian.html",
        "interior-styles/coastal.html",
        "interior-styles/farmhouse.html",
        "interior-styles/industrial-loft.html",
        "interior-styles/japandi.html",
        "interior-styles/maximalist.html",
        "interior-styles/mid-century-modern.html",
        "interior-styles/modern-minimalist.html",
        "interior-styles/scandinavian.html",
        "interior-styles/transitional.html",
        # Landmarks (7)
        "landmarks/burj-khalifa.html",
        "landmarks/colosseum.html",
        "landmarks/eiffel-tower.html",
        "landmarks/fallingwater.html",
        "landmarks/sagrada-familia.html",
        "landmarks/sydney-opera-house.html",
        "landmarks/villa-savoye.html",
        # Compare (3)
        "compare/east-west-courtyard.html",
        "compare/symmetry-vs-asymmetry.html",
        "compare/wood-vs-stone.html",
    ]

    success = 0
    failures = []

    for rel_path in pages:
        filepath = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(filepath):
            failures.append((rel_path, "File not found"))
            continue

        try:
            data = extract_old_page(filepath)
            new_html = generate_new_html(data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            success += 1
            print(f"  OK  {rel_path}")
        except Exception as e:
            failures.append((rel_path, str(e)))
            print(f"  FAIL {rel_path}: {e}")

    print(f"\n{'='*60}")
    print(f"Converted: {success}/{len(pages)} pages")
    if failures:
        print(f"Failures: {len(failures)}")
        for path, reason in failures:
            print(f"  - {path}: {reason}")
    else:
        print("All pages converted successfully!")


if __name__ == "__main__":
    main()
