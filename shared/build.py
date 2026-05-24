"""build.py — Rebuild all sites from templates + site_config.py
Usage: py shared/build.py          # rebuild all sites
       py shared/build.py --verify # check what would change
       py shared/build.py --site sub-pets  # rebuild single site
"""
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_config import SITES, GA_ID, ADSENSE_CLIENT, CONTACT_EMAIL, FORM_SUBMIT_URL

SHARED_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SHARED_DIR)

# === Template functions ===

def head(cfg, page_meta):
    """Generate <head> block with site config + page-specific meta."""
    name = cfg["brand_name"]
    desc = page_meta.get("description", cfg["brand_desc"])
    keywords = page_meta.get("keywords", "")
    title = page_meta.get("title", f"{name} | {cfg['brand_slogan']}")
    og_title = page_meta.get("og_title", title)
    og_desc = page_meta.get("og_description", desc)
    og_type = page_meta.get("og_type", "website")
    og_url = page_meta.get("og_url", cfg["base_url"] + "/")
    og_image = page_meta.get("og_image", "")
    og_site = page_meta.get("og_site_name", name)
    canonical = page_meta.get("canonical", og_url)
    robots = page_meta.get("robots", "index, follow")
    schema_name = page_meta.get("schema_name", name)
    schema_url = page_meta.get("schema_url", cfg["base_url"])
    noindex = "noindex, follow" if page_meta.get("noindex") else robots

    colors = cfg["colors"]
    colors_js = _build_colors_js(colors)

    fonts = cfg.get("font_sans", ['Roboto', 'Arial', 'Helvetica', 'sans-serif'])
    fonts_str = ",".join(f"'{f}'" for f in fonts)
    heading_fonts = cfg.get("font_heading")
    font_extend = ""
    if heading_fonts:
        hf = ",".join(f"'{f}'" for f in heading_fonts)
        font_extend = f",\n                        heading: [{hf}]"

    body_class = cfg.get("body_class", "bg-white text-gray-800 font-sans")

    head_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="{noindex}">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="{og_type}">
    <meta property="og:url" content="{og_url}">
    <meta property="og:site_name" content="{og_site}">
    <meta property="og:image" content="{og_image or cfg['base_url'] + '/images/default-og.jpg'}">
    <title>{title}</title>
    <link rel="canonical" href="{canonical}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {colors_js},
                    fontFamily: {{
                        sans: [{fonts_str}]{font_extend}
                    }}
                }}
            }}
        }}
    </script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">'''

    # Optional custom styles
    if cfg.get("body_class", "").startswith("bg-stone"):
        head_html += '''
    <style>
        .ad-container{background:#fafaf9;border:2px dashed #e7e5e4;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#a8a29e;font-size:14px;min-height:90px}
        .article-card:hover{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,0.08)}
        .article-card{transition:all .2s ease}
    </style>'''
    elif cfg.get("article_card_class") == "site-card":
        head_html += '''
    <style>
        .site-card:hover { transform: translateY(-6px); box-shadow: 0 20px 40px rgba(0,0,0,0.12); }
        .site-card { transition: all 0.3s ease; }
    </style>'''

    # Schema.org
    head_html += f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{schema_name}",
  "url": "{schema_url}",
  "logo": "{schema_url}/favicon.ico"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{schema_name}",
  "url": "{schema_url}",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": "{schema_url}/?s={{{{search_term_string}}}}",
    "query-input": "required name=search_term_string"
  }}
}}
</script>
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
</head>'''

    return head_html, body_class


def _build_colors_js(colors):
    """Convert color dict to JS object string."""
    parts = []
    for name, shades in colors.items():
        if isinstance(shades, dict):
            inner = ", ".join(f"{k}: '{v}'" for k, v in sorted(shades.items()))
            parts.append(f"'{name}': {{ {inner} }}")
        else:
            parts.append(f"'{name}': '{shades}'")
    return "{ " + ", ".join(parts) + " }"


def nav(cfg, current_page="index.html"):
    """Generate navigation bar."""
    logo_text = cfg["brand_logo_text"]
    logo_accent = cfg["brand_logo_accent"]
    accent_color = cfg.get("accent_text", "text-blue-600")
    accent_hover = cfg.get("accent_hover", "hover:text-blue-600")
    nav_items = cfg["nav_items"]

    items_html = ""
    for item in nav_items:
        is_current = item.get("href") == current_page
        cls = f'class="{accent_color} font-medium"' if is_current else f'class="text-gray-600 {accent_hover}"'
        items_html += f'\n                <a href="{item["href"]}" {cls}>{item["label"]}</a>'

    nav_html = f'''<body class="{cfg["body_class"]}">

<nav class="{cfg["nav_bg"]}">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <a href="index.html" class="text-2xl font-black text-gray-900 tracking-tight">{logo_text}<span class="{accent_color}">{logo_accent}</span></a>
        <div class="hidden md:flex items-center gap-8 text-sm font-medium">{items_html}
        </div>
        <button class="md:hidden text-gray-600 text-2xl">&#9776;</button>
    </div>
</nav>'''

    return nav_html


def footer(cfg):
    """Generate standard footer."""
    brand = cfg["footer_brand"]
    accent = cfg.get("footer_accent_color", "primary-400")
    desc = cfg["brand_desc"]
    base = cfg["base_url"]
    domain = cfg["domain"]

    return f'''
<footer class="bg-gray-900 text-gray-400 py-12">
    <div class="max-w-6xl mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-white text-lg font-black mb-3">{brand}</h3>
                <p class="text-sm leading-relaxed">{desc}</p>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Legal</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="privacy-policy.html" class="hover:text-white transition-colors">Privacy Policy</a></li>
                    <li><a href="terms.html" class="hover:text-white transition-colors">Terms of Service</a></li>
                    <li><a href="cookie-policy.html" class="hover:text-white transition-colors">Cookie Policy</a></li>
                    <li><a href="contact.html" class="hover:text-white transition-colors">Contact</a></li>
                </ul>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Contact</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="mailto:{CONTACT_EMAIL}" class="hover:text-white transition-colors">{CONTACT_EMAIL}</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-800 pt-6 text-center text-sm">
            <p>&copy; 2026 {brand}. All rights reserved.</p>
        </div>
    </div>
</footer>'''


def contact_form(cfg):
    """Generate standard contact form with FormSubmit + success modal."""
    domain = cfg["base_url"]

    return f'''<form class="space-y-5" action="{FORM_SUBMIT_URL}" method="POST">
                    <input type="hidden" name="_next" value="{domain}/contact.html?success=1">
                    <input type="hidden" name="_captcha" value="false">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
                        <input type="text" name="name" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 bg-white focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none" placeholder="John Doe" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Your Email</label>
                        <input type="email" name="email" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 bg-white focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none" placeholder="john@example.com" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                        <input type="text" name="subject" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 bg-white focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none" placeholder="How can we help?">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                        <textarea rows="4" name="message" class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-gray-800 bg-white focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none resize-none" placeholder="Tell us what's on your mind..." required></textarea>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors">
                        Send Message
                    </button>
                </form>'''


def success_modal():
    return '''
                <div id="form-success" class="hidden fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
                    <div class="bg-white rounded-2xl p-8 max-w-md mx-4 text-center shadow-2xl">
                        <div class="text-5xl mb-4">&#10003;</div>
                        <h3 class="text-xl font-bold text-gray-900 mb-2">Message Sent!</h3>
                        <p class="text-gray-600 mb-6">Thank you for reaching out. We have received your message and will get back to you shortly.</p>
                        <button onclick="document.getElementById('form-success').classList.add('hidden')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-lg transition-colors">Close</button>
                    </div>
                </div>
                <script>
                (function() {
                    if (window.location.search.includes('success=1')) {
                        document.getElementById('form-success').classList.remove('hidden');
                        var newUrl = window.location.protocol + '//' + window.location.host + window.location.pathname;
                        window.history.replaceState({}, document.title, newUrl);
                    }
                })();
                </script>'''


# === Page type generators ===

# These wrap page-specific BODY content with standard head/nav/footer
# Each takes cfg + page_meta dict + content_html string

def wrap_page(cfg, page_meta, body_content, current_page="index.html"):
    """Return complete HTML for a page."""
    h, body_class = head(cfg, page_meta)
    n = nav(cfg, current_page)
    f = footer(cfg)
    return h + "\n" + n + "\n" + body_content + "\n" + f + "\n</body>\n</html>"


# === Content extraction (for migrating existing pages) ===

def extract_body(html):
    """Extract content between </nav> and <footer."""
    m = re.search(r'</nav>\s*\n(.*?)<footer', html, re.DOTALL)
    if m:
        return m.group(1)
    return None


def rebuild_file(filepath, cfg, page_meta=None, body_content=None, current_page="index.html"):
    """Rebuild a single HTML file from templates."""
    if body_content is None:
        with open(filepath, "r", encoding="utf-8") as f:
            old_html = f.read()
        body_content = extract_body(old_html)
        if body_content is None:
            print(f"  SKIP {filepath}: can't extract body")
            return False

    if page_meta is None:
        # Try to extract meta from old file
        page_meta = _extract_meta(filepath)

    new_html = wrap_page(cfg, page_meta, body_content, current_page)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)
    return True


def _extract_meta(filepath):
    """Extract page meta from existing file's <head>."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except:
        return {}

    meta = {}
    patterns = {
        "description": r'<meta name="description" content="([^"]*)"',
        "keywords": r'<meta name="keywords" content="([^"]*)"',
        "title": r'<title>(.*?)</title>',
        "og_title": r'<meta property="og:title" content="([^"]*)"',
        "og_description": r'<meta property="og:description" content="([^"]*)"',
        "og_url": r'<meta property="og:url" content="([^"]*)"',
        "canonical": r'<link rel="canonical" href="([^"]*)"',
        "robots": r'<meta name="robots" content="([^"]*)"',
        "og_site_name": r'<meta property="og:site_name" content="([^"]*)"',
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, html)
        if m:
            meta[key] = m.group(1)
    return meta


# === Category page builder ===

def build_category_pages(site_dir=None):
    """Generate category landing pages for sites that need them."""
    from category_config import CATEGORIES
    built = 0

    sites_to_build = [site_dir] if site_dir else CATEGORIES.keys()

    for site_key in sites_to_build:
        if site_key not in CATEGORIES or site_key not in SITES:
            continue
        cfg = SITES[site_key]
        site_path = os.path.join(ROOT, site_key)
        categories = CATEGORIES[site_key]

        for cat_name, cat_info in categories.items():
            slug = cat_info["slug"]
            out_path = os.path.join(site_path, f"category-{slug}.html")

            page_meta = {
                "title": cat_info["title"],
                "description": cat_info["desc"],
                "og_title": cat_info["title"],
                "og_description": cat_info["desc"],
                "og_url": f"{cfg['base_url']}/category-{slug}.html",
                "canonical": f"{cfg['base_url']}/category-{slug}.html",
                "robots": "index, follow",
            }

            articles_html = _build_article_cards(site_path, cat_info["articles"], cat_info["slug"])

            hero_color = cfg.get("colors", {}).get("brand", cfg.get("colors", {}).get("primary", {}))
            if isinstance(hero_color, dict):
                hero_from = hero_color.get(900, hero_color.get(800, "#1e3a8a"))
                hero_to = hero_color.get(700, hero_color.get(600, "#1d4ed8"))
            else:
                hero_from = "#1e3a8a"
                hero_to = "#1d4ed8"

            accent = cfg.get("accent_text", "text-blue-600").replace("text-", "")

            body = f'''
    <section class="bg-gradient-to-br from-gray-900 via-{accent}-900 to-{accent}-800 text-white py-16 md:py-20">
        <div class="max-w-4xl mx-auto px-6 text-center">
            <h1 class="text-4xl md:text-5xl font-black mb-4">{cat_info["hero_title"]}</h1>
            <p class="text-lg text-white/80">{cat_info["hero_subtitle"]}</p>
        </div>
    </section>

    <section class="max-w-6xl mx-auto px-4 py-12">
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
    {articles_html}
        </div>
    </section>'''

            html = wrap_page(cfg, page_meta, body, current_page=f"category-{slug}.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  category-{slug}.html ({len(cat_info['articles'])} articles)")
            built += 1

    print(f"\nCategory pages built: {built}")
    return built


def _build_article_cards(site_path, article_nums, category_slug):
    """Generate article card HTML for a list of article numbers."""
    cards = []
    for num in sorted(article_nums):
        fpath = os.path.join(site_path, f"article-{num}.html")
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            title_m = re.search(r'<title>(.*?)</title>', content)
            title = title_m.group(1) if title_m else f"Article {num}"
            title = re.sub(r'\s*\|.*$', '', title).strip()
            desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
            desc = desc_m.group(1) if desc_m else ""
            if len(desc) > 150:
                desc = desc[:147] + "..."
            img_m = re.search(r'<img[^>]*src="([^"]*)"', content)
            img_src = img_m.group(1) if img_m else ""

            cards.append(f'''            <a href="article-{num}.html" class="site-card block bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group">
                <div class="h-48 overflow-hidden">
                    <img src="{img_src}" alt="{title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
                </div>
                <div class="p-5">
                    <h3 class="font-bold text-gray-900 mb-2 group-hover:text-brand-600 transition-colors">{title}</h3>
                    <p class="text-sm text-gray-500 leading-relaxed">{desc}</p>
                </div>
            </a>''')
        except Exception as e:
            print(f"    WARN: article-{num}.html — {e}")

    return "\n".join(cards)


# === Main ===

def build_all(verify=False):
    """Rebuild all pages across all sites."""
    built = 0
    skipped = 0
    for site_dir, cfg in SITES.items():
        site_path = os.path.join(ROOT, site_dir)
        if not os.path.isdir(site_path):
            continue
        html_files = [f for f in os.listdir(site_path) if f.endswith(".html")]
        for fname in html_files:
            fpath = os.path.join(site_path, fname)
            meta = _extract_meta(fpath)
            if verify:
                print(f"  [VERIFY] {site_dir}/{fname}")
                continue
            ok = rebuild_file(fpath, cfg, page_meta=meta, current_page=fname)
            if ok:
                built += 1
            else:
                skipped += 1

    print(f"\nBuilt: {built}, Skipped: {skipped}")
    return built, skipped


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--categories" in args:
        site_only = None
        if "--site" in args:
            idx = args.index("--site")
            site_only = args[idx + 1]
        build_category_pages(site_only)
    elif "--verify" in args:
        build_all(verify=True)
    elif "--site" in args:
        idx = args.index("--site")
        site_name = args[idx + 1]
        site_path = os.path.join(ROOT, site_name)
        cfg = SITES[site_name]
        for fname in sorted(os.listdir(site_path)):
            if fname.endswith(".html"):
                fpath = os.path.join(site_path, fname)
                meta = _extract_meta(fpath)
                rebuild_file(fpath, cfg, page_meta=meta, current_page=fname)
                print(f"  {fname}")
        print(f"Done: {site_name}")
    else:
        build_all()
