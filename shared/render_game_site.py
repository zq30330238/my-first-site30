"""Render a complete game/anime guide site from structured data.
Usage: py shared/render_game_site.py <site_key>
       py shared/render_game_site.py --all
       py shared/render_game_site.py --all --data anime_site_data.json
"""
import sys, json, re, os, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "shared" / "game_site_data.json"

GA4_ID = "G-GGNWR1X1GV"
ADSENSE_PUB = "ca-pub-2595917642864488"

ANIME_ITEM_TYPES = [
    {"key": "transformations", "name": "Transformations", "slug": "transformations", "singular": "Transformation"},
    {"key": "techniques", "name": "Techniques", "slug": "techniques", "singular": "Technique"},
    {"key": "sagas", "name": "Sagas", "slug": "sagas", "singular": "Saga"},
    {"key": "races_organizations", "name": "Races & Organizations", "slug": "races", "singular": "Race/Organization"},
]


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def is_anime_data(data):
    return data.get("site_type") == "anime" or "transformations" in data


def get_anime_item_types(data):
    types = []
    for t in ANIME_ITEM_TYPES:
        if data.get(t["key"]):
            types.append(t)
    return types


def get_all_categories(data):
    cats = list(data.get("categories", []))
    existing_slugs = {c["slug"] for c in cats}
    for atype in ANIME_ITEM_TYPES:
        if data.get(atype["key"]) and atype["slug"] not in existing_slugs:
            items = data[atype["key"]]
            first_img = items[0].get("image", "") if items else ""
            cats.append({
                "name": atype["name"],
                "slug": atype["slug"],
                "color": data.get("accent", "#888"),
                "character_img": first_img,
                "count": str(len(items)) + "+",
            })
    return cats


def get_char_category_slug(data, char):
    link = char.get("link", "")
    parts = link.strip("/").split("/")
    if len(parts) >= 2:
        return parts[-1]
    cats = data.get("categories", [])
    return cats[0]["slug"] if cats else "characters"


def resolve_char_detail_url(data, char):
    cat_slug = get_char_category_slug(data, char)
    char_slug = slugify(char["name"])
    return f"/guides/{cat_slug}/{char_slug}.html"


def resolve_char_detail_path(data, char):
    cat_slug = get_char_category_slug(data, char)
    char_slug = slugify(char["name"])
    return f"guides/{cat_slug}/{char_slug}.html"


def validate_prerender(data, site_dir):
    warnings = []
    images_dir = site_dir / "images"
    img_files = set()
    if images_dir.exists():
        img_files = {f.name for f in images_dir.iterdir() if f.is_file()}

    if not data.get("site_name"):
        warnings.append("Missing site_name")
    if not data.get("domain"):
        warnings.append("Missing domain")
    if not data.get("categories"):
        warnings.append("No categories defined")

    for cat in data.get("categories", []):
        for field in ["name", "slug"]:
            if not cat.get(field):
                warnings.append(f"Category missing {field}: {cat}")

    for char in data.get("characters", []):
        for field in ["name", "image"]:
            if not char.get(field):
                warnings.append(f"Character '{char.get('name', '?')}' missing {field}")
        img = char.get("image", "")
        if img and img not in img_files:
            warnings.append(f"Character image not found: {img}")

    for cat in data.get("categories", []):
        cimg = cat.get("character_img", "")
        if cimg and cimg not in img_files:
            warnings.append(f"Category image not found: {cimg}")

    for guide in data.get("guide_cards", []):
        gimg = guide.get("image", "")
        if gimg and gimg not in img_files:
            warnings.append(f"Guide image not found: {gimg}")

    for topic in data.get("hot_topics", []):
        timg = topic.get("image", "")
        if timg and timg not in img_files:
            warnings.append(f"Hot topic image not found: {timg}")

    for atype in get_anime_item_types(data):
        for item in data.get(atype["key"], []):
            for field in ["name", "image"]:
                if not item.get(field):
                    warnings.append(f"{atype['singular']} '{item.get('name', '?')}' missing {field}")
            img = item.get("image", "")
            if img and img not in img_files:
                warnings.append(f"{atype['singular']} image not found: {img}")

    return warnings


def generate_search_index(data):
    entries = []
    for cat in data.get("categories", []):
        entries.append({
            "name": cat["name"],
            "desc": f"Category — {cat.get('count', '')} guides",
            "type": "category",
            "url": f"/guides/{cat['slug']}/",
            "color": cat.get("color", data.get("accent", "#888")),
        })
    for char in data.get("characters", []):
        entries.append({
            "name": char["name"],
            "desc": char.get("role", "") or char.get("desc", ""),
            "type": "character",
            "url": resolve_char_detail_url(data, char),
            "color": char.get("color", data.get("accent", "#888")),
        })
    for guide in data.get("guide_cards", []):
        entries.append({
            "name": guide["title"],
            "desc": guide.get("category", ""),
            "type": "guide",
            "url": guide.get("link", "/"),
            "color": guide.get("cat_color", data.get("accent", "#888")),
        })
    for topic in data.get("hot_topics", []):
        entries.append({
            "name": topic["title"],
            "desc": topic.get("desc", ""),
            "type": "hot_topic",
            "url": topic.get("link", "/"),
            "color": data.get("accent", "#888"),
        })
    for atype in get_anime_item_types(data):
        for item in data.get(atype["key"], []):
            item_slug = slugify(item["name"])
            entries.append({
                "name": item["name"],
                "desc": item.get("desc", ""),
                "type": atype["singular"].lower().replace("/", "_"),
                "url": f"/guides/{atype['slug']}/{item_slug}.html",
                "color": item.get("color", data.get("accent", "#888")),
            })
    return entries


def generate_robots_txt(data, site_dir):
    domain = data.get("domain", "example.com")
    body = f"""User-agent: *
Allow: /
Sitemap: https://{domain}/sitemap.html
"""
    (site_dir / "robots.txt").write_text(body.strip() + "\n", encoding="utf-8")


def generate_about_contact(data, site_dir):
    accent = data.get("accent", "#ff6b35")
    site_name = data.get("site_name", "Wiki")
    tagline = data.get("tagline", "")
    domain = data.get("domain", "")
    site_key = data.get("site_key", "")
    ga_id = data.get("ga_id", "G-GGNWR1X1GV")
    adsense_id = data.get("adsense_id", "ca-pub-2595917642864488")

    base = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, follow">
<meta name="google-adsense-account" content="{adsense_id}">
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{{{theme:{{{{extend:{{{{colors:{{{{accent:'{accent}',accentDark:'{accent}'}}}}}}}}}}}}}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_id}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>function gtag(){{{{dataLayer.push(arguments)}}}}gtag('js',new Date());gtag('config','{ga_id}');</script>
<style>
*{{{{margin:0;padding:0;box-sizing:border-box}}}}
body{{{{font-family:'Inter',Arial,sans-serif;background:#fff;color:#111827;font-size:16px;line-height:1.6}}}}
</style>
</head>
<body class="bg-white text-gray-900 font-sans">
<nav class="border-b border-gray-200 py-4 px-6"><a href="/" class="text-xl font-bold">{site_name.split(' ')[0]} <span style="color:{accent}">{site_name.split(' ')[1] if ' ' in site_name else 'Wiki'}</span></a></nav>
<main class="max-w-3xl mx-auto px-6 py-16">
"""

    about = base + f"""<title>About — {site_name}</title>
<meta name="description" content="About {site_name} — {tagline}">
<link rel="canonical" href="https://{domain}/about.html">
<h1 class="text-4xl font-bold mb-6">About {site_name}</h1>
<p class="text-lg text-gray-600 mb-4">{site_name} is a comprehensive English-language encyclopedia. {tagline}</p>
<p class="text-lg text-gray-600 mb-4">{site_name} is part of the Myers Media network, dedicated to creating high-quality reference content.</p>
</main>
<footer class="border-t border-gray-200 py-8 px-6 text-center text-sm text-gray-400"><p>&copy; 2026 {site_name}. Part of Myers Media.</p></footer>
</body>
</html>"""

    contact = base + f"""<title>Contact — {site_name}</title>
<meta name="description" content="Contact {site_name} for inquiries, corrections, or feedback.">
<link rel="canonical" href="https://{domain}/contact.html">
<h1 class="text-4xl font-bold mb-6">Contact Us</h1>
<p class="text-lg text-gray-600 mb-4">Have a suggestion, correction, or just want to say hi? We'd love to hear from you.</p>
<p class="text-lg text-gray-600 mb-4">Email: <a href="mailto:zq30330238@gmail.com" class="text-blue-600 hover:underline">zq30330238@gmail.com</a></p>
</main>
<footer class="border-t border-gray-200 py-8 px-6 text-center text-sm text-gray-400"><p>&copy; 2026 {site_name}. Part of Myers Media.</p></footer>
</body>
</html>"""

    (site_dir / "about.html").write_text(about, encoding="utf-8")
    (site_dir / "contact.html").write_text(contact, encoding="utf-8")


def generate_sitemap_xml(data, site_dir, site_key):
    domain = data.get("domain", "example.com")
    urls = []
    urls.append(f"  <url><loc>https://{domain}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>")
    for cat in data.get("categories", []):
        urls.append(f"  <url><loc>https://{domain}/guides/{cat['slug']}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    for char in data.get("characters", []):
        detail_url = resolve_char_detail_url(data, char)
        urls.append(f"  <url><loc>https://{domain}{detail_url}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    for atype in get_anime_item_types(data):
        if atype["slug"] not in {c["slug"] for c in data.get("categories", [])}:
            urls.append(f"  <url><loc>https://{domain}/guides/{atype['slug']}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
        for item in data.get(atype["key"], []):
            item_slug = slugify(item["name"])
            urls.append(f"  <url><loc>https://{domain}/guides/{atype['slug']}/{item_slug}.html</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    (site_dir / "sitemap.xml").write_text(body.strip() + "\n", encoding="utf-8")




def generate_sitemap_html(data, site_dir, site_key):
    tc = theme_colors(data)
    accent = data.get("accent", "#ff6b35")
    site_name = data.get("site_name", "Wiki")
    domain = data.get("domain", "")
    adsense_id = data.get("adsense_id", "ca-pub-2595917642864488")
    ga_id = data.get("ga_id", "G-GGNWR1X1GV")
    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    nav_links = render_nav_links(data)
    mobile_nav_links = render_mobile_nav_links(data)
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    copyright_note = render_copyright_note(data)

    sections = []
    static_pages = []
    for cat in data.get("categories", []):
        static_pages.append((cat["name"], f"/guides/{cat['slug']}/"))
    static_links = chr(10).join(
        f"""<a href="{url}" class="block text-textPrimary hover:text-accent transition-colors py-2 px-3 rounded-lg hover:bg-bgSecondary">{name}</a>"""
        for name, url in static_pages
    )
    sections.append(f"""<h2 class="text-2xl font-bold text-accent mb-4 mt-10">Main Pages</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">{static_links}</div>""")

    chars = sorted(data.get("characters", []), key=lambda c: c.get("name", ""))
    if chars:
        char_links = []
        for char in chars:
            detail_url = resolve_char_detail_url(data, char)
            char_links.append(f"""<a href="{detail_url}" class="block text-textPrimary hover:text-accent transition-colors py-2 px-3 rounded-lg hover:bg-bgSecondary">{char['name']}</a>""")
        sections.append(f"""<h2 class="text-2xl font-bold text-accent mb-4 mt-10">Characters ({len(chars)})</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-4 gap-3">{chr(10).join(char_links)}</div>""")

    for atype in get_anime_item_types(data):
        items = data.get(atype["key"], [])
        if not items:
            continue
        items = sorted(items, key=lambda i: i.get("name", ""))
        item_links = []
        for item in items:
            item_slug = slugify(item["name"])
            item_links.append(f"""<a href="/guides/{atype['slug']}/{item_slug}.html" class="block text-textPrimary hover:text-accent transition-colors py-2 px-3 rounded-lg hover:bg-bgSecondary">{item['name']}</a>""")
        sections.append(f"""<h2 class="text-2xl font-bold text-accent mb-4 mt-10">{atype['name']} ({len(items)})</h2>
<div class="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-4 gap-3">{chr(10).join(item_links)}</div>""")

    content_body = chr(10).join(sections)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sitemap — {site_name}</title>
<meta name="description" content="Sitemap for {site_name} — browse all characters, guides, and pages.">
<meta property="og:title" content="Sitemap — {site_name}">
<meta property="og:description" content="Sitemap for {site_name}">
<meta name="robots" content="index, follow">
<meta name="google-adsense-account" content="{adsense_id}">
<link rel="canonical" href="https://{domain}/sitemap.html">
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{theme:{{extend:{{colors:{{bgPrimary:"{tc['bgPrimary']}",bgSecondary:"{tc['bgSecondary']}",bgCard:"{tc['bgCard']}",textPrimary:"{tc['textPrimary']}",textSecondary:"{tc['textSecondary']}",accent:"{accent}"}},fontFamily:{{sans:["Inter","Arial","sans-serif"]}}}}}}}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_id}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{ga_id}');</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Inter",Arial,sans-serif;background:{tc['bodyBg']};color:{tc['textPrimary']};font-size:16px;line-height:1.6}}
</style>
</head>
<body class="bg-bgPrimary text-textPrimary font-sans">

<nav class="fixed top-0 w-full z-50 border-b" style="background:{tc['navBg']};border-color:#{tc['navBorder']}">
<div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
<a href="/" class="flex items-center gap-2.5 flex-shrink-0">
{nav_logo}
<span class="text-xl font-bold tracking-tight">{nav_brand}</span>
</a>
<div class="hidden lg:flex items-center gap-6 text-sm font-medium">
<a href="/" class="text-textSecondary hover:text-accent transition-colors">Home</a>
{nav_links}
</div>
<button class="lg:hidden text-textSecondary text-2xl" id="menuBtn" aria-label="Menu">&#9776;</button>
</div>
</nav>

<main class="max-w-7xl mx-auto px-4 py-24">
<h1 class="text-4xl font-black mb-2">Sitemap</h1>
<p class="text-textSecondary mb-8">Browse all pages on {site_name}.</p>
{content_body}
</main>

<footer class="bg-bgSecondary border-t py-16 px-4" style="border-color:#{tc['borderHex']}">
<div class="max-w-7xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
<div>
<div class="flex items-center gap-2.5 mb-4">
{footer_logo}
<span class="text-xl font-bold">{footer_brand}</span>
</div>
<p class="text-sm text-textSecondary leading-relaxed">{footer_blurb}</p>
</div>
<div>
<h4 class="font-bold mb-4">Categories</h4>
<ul class="space-y-2 text-sm text-textSecondary">
{footer_cats}
</ul>
</div>
<div>
<h4 class="font-bold mb-4">{footer_links_title}</h4>
{footer_links}
</div>
<div>
<h4 class="font-bold mb-4">About</h4>
<ul class="space-y-2 text-sm text-textSecondary">
<li><a href="/about.html" class="hover:text-accent transition-colors">About</a></li>
<li><a href="/contact.html" class="hover:text-accent transition-colors">Contact</a></li>
<li><a href="/sitemap.html" class="hover:text-accent transition-colors">Sitemap</a></li>
</ul>
</div>
</div>
<div class="max-w-7xl mx-auto mt-12 pt-6 border-t text-center text-sm text-textSecondary" style="border-color:#{tc['borderHex']}">
<p>&copy; 2026 {site_name} by <a href="https://www.jycsd.com" class="text-accent hover:underline">Myers Media</a>. {copyright_note}</p>
</div>
</footer>

</body>
</html>"""
    (site_dir / "sitemap.html").write_text(html, encoding="utf-8")
    print(f"  sitemap.html: {site_dir / 'sitemap.html'}")


def render_breadcrumb(data, category=None, item_name=None):
    domain = data.get("domain", "")
    home = f'<a href="/" class="text-accent hover:underline">Home</a>'
    if not category:
        return f'<nav class="text-sm text-textSecondary mb-4" aria-label="Breadcrumb">{home}</nav>'
    cat_name = category["name"] if isinstance(category, dict) else category
    cat_slug = category["slug"] if isinstance(category, dict) else slugify(cat_name)
    cat_link = f'<a href="/guides/{cat_slug}/" class="text-accent hover:underline">{cat_name}</a>'
    parts = [home, cat_link]
    if item_name:
        parts.append(f'<span class="text-textSecondary">{item_name}</span>')
    return '<nav class="text-sm text-textSecondary mb-4" aria-label="Breadcrumb">' + ' <span class="mx-1.5">&#8250;</span> '.join(parts) + '</nav>'


def _esc_json(val):
    """Escape a string value for safe embedding in a JSON template."""
    return val.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def schema_org_person(data, char):
    domain = data.get("domain", "example.com")
    url = resolve_char_detail_url(data, char)
    name = _esc_json(char['name'])
    desc = _esc_json(char.get('desc', char.get('role', '')))
    image = _esc_json(char.get('image', ''))
    role = _esc_json(char.get('role', ''))
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "{name}",
  "description": "{desc}",
  "url": "https://{domain}{url}",
  "image": "https://{domain}/images/{image}",
  "jobTitle": "{role}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "https://{domain}{url}"
  }}
}}
</script>'''


def schema_org_creative_work(data, char):
    domain = data.get("domain", "example.com")
    url = resolve_char_detail_url(data, char)
    name = _esc_json(char['name'])
    desc = _esc_json(char.get('desc', ''))
    role = _esc_json(char.get('role', ''))
    site_name = _esc_json(data['site_name'])
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{name} Guide — {site_name}",
  "description": "In-depth guide for {name} — {desc}",
  "url": "https://{domain}{url}",
  "about": {{
    "@type": "Person",
    "name": "{name}",
    "description": "{role}"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Myers Media"
  }}
}}
</script>'''


def schema_org_anime_item(data, item, item_type):
    domain = data.get("domain", "example.com")
    item_slug = slugify(item["name"])
    atype = None
    for t in ANIME_ITEM_TYPES:
        if t["key"] == item_type:
            atype = t
            break
    slug = atype["slug"] if atype else item_type
    url = f"https://{domain}/guides/{slug}/{item_slug}.html"
    name = _esc_json(item['name'])
    desc = _esc_json(item.get('desc', '')[:200])
    site_name = _esc_json(data['site_name'])
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{name} — {site_name}",
  "description": "{desc}",
  "url": "{url}",
  "publisher": {{
    "@type": "Organization",
    "name": "Myers Media"
  }}
}}
</script>'''


def theme_colors(data):
    t = data.get("theme", "dark")
    if t == "light":
        return {
            "bgPrimary": "#ffffff",
            "bgSecondary": "#f3f4f6",
            "bgCard": "#ffffff",
            "textPrimary": "#111827",
            "textSecondary": "#4b5563",
            "border": "#e5e7eb",
            "borderHex": "e5e7eb",
            "navBg": "rgba(255,255,255,0.95)",
            "navBorder": "e5e7eb",
            "cardBorder": "e5e7eb",
            "cardBorderHover": "accent/50",
            "footerBorder": "e5e7eb",
            "bodyBg": "#ffffff",
            "shadow": "0 4px 20px rgba(0,0,0,.08)",
            "glow": "0 8px 30px {accent}40",
        }
    return {
        "bgPrimary": "#0d1117",
        "bgSecondary": "#161b22",
        "bgCard": "#1a1f2e",
        "textPrimary": "#e6edf3",
        "textSecondary": "#8b949e",
        "border": "rgba(75,85,99,0.3)",
        "borderHex": "374151",
        "navBg": "rgba(13,17,23,0.95)",
        "navBorder": "374151",
        "cardBorder": "374151",
        "cardBorderHover": "accent/50",
        "footerBorder": "374151",
        "bodyBg": "#0d1117",
        "shadow": "0 4px 20px rgba(0,0,0,.3)",
        "glow": "0 8px 30px {accent}26",
    }


def get_nav_label(data):
    st = data.get("site_type", "game")
    return "Anime Hub" if st == "anime" else "Game Hub"


def get_nav_url(data):
    st = data.get("site_type", "game")
    return data.get("hub_url", "https://anime.jycsd.com" if st == "anime" else "https://games.jycsd.com")


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical_url}">
<meta name="google-adsense-account" content="ca-pub-2595917642864488">
{schema_markup}
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{theme:{{extend:{{colors:{{bgPrimary:'{bgPrimary}',bgSecondary:'{bgSecondary}',bgCard:'{bgCard}',textPrimary:'{textPrimary}',textSecondary:'{textSecondary}',accent:'{accent}',accentDark:'{accent_dark}'}},fontFamily:{{sans:['Inter','Arial','sans-serif']}}}}}}}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_pub}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{ga_id}');</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',Arial,sans-serif;background:{bodyBg};color:{textPrimary};font-size:16px;line-height:1.6}}
.carousel-slide{{position:absolute;inset:0;opacity:0;transition:opacity .8s ease-in-out;pointer-events:none}}
.carousel-slide.active{{opacity:1;pointer-events:auto}}
.carousel-dot{{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,.3);cursor:pointer;transition:background .3s}}
.carousel-dot.active{{background:{accent}}}
.card-hover:hover{{transform:translateY(-2px);box-shadow:{glow};transition:all .3s ease}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
.float-anim{{animation:float 3s ease-in-out infinite}}
.char-img{{filter:drop-shadow(0 10px 30px rgba(0,0,0,.5))}}
img[src$=".png"]{{mix-blend-mode:normal}}
.search-dropdown{{position:absolute;top:100%;left:0;right:0;background:{bgCard};border:1px solid #{navBorder};border-radius:0 0 8px 8px;max-height:320px;overflow-y:auto;display:none;z-index:60;box-shadow:0 12px 40px rgba(0,0,0,.4)}}
.search-dropdown.active{{display:block}}
.search-result{{display:flex;align-items:center;gap:10px;padding:10px 14px;cursor:pointer;transition:background .15s;border-bottom:1px solid rgba(75,85,99,.15)}}
.search-result:hover,.search-result.focused{{background:rgba(255,255,255,.05)}}
.search-result:last-child{{border-bottom:none}}
.search-result .sr-type{{font-size:10px;text-transform:uppercase;letter-spacing:.8px;padding:2px 7px;border-radius:999px;flex-shrink:0}}
.search-empty{{padding:20px;text-align:center;color:{textSecondary};font-size:14px}}
.masonry-grid{{columns:2;column-gap:1rem}}
.masonry-grid>*{{break-inside:avoid;margin-bottom:1rem}}
@media(min-width:768px){{.masonry-grid{{columns:3}}}}
@media(min-width:1024px){{.masonry-grid{{columns:4}}}}
@media(min-width:1280px){{.masonry-grid{{columns:5}}}}
.scroll-snap-x{{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:1rem;scrollbar-width:none;padding-bottom:4px}}
.scroll-snap-x::-webkit-scrollbar{{display:none}}
.scroll-snap-x>*{{scroll-snap-align:start;flex-shrink:0}}
.gradient-overlay{{background:linear-gradient(to top,rgba(0,0,0,0.85) 0%,rgba(0,0,0,0.3) 50%,transparent 100%)}}
.text-shadow{{text-shadow:0 2px 8px rgba(0,0,0,0.6)}}
.carousel-arrow{{position:absolute;top:50%;transform:translateY(-50%);z-index:10;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.15);backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,0.2);color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:22px;transition:all .3s;opacity:0}}
.carousel-arrow:hover{{background:rgba(255,255,255,0.3)}}
.carousel:hover .carousel-arrow{{opacity:1}}
.back-to-top{{position:fixed;bottom:32px;right:32px;z-index:999;width:44px;height:44px;border-radius:50%;background:#ff6b35;color:#111;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer;opacity:0.35;transition:all .3s;box-shadow:0 4px 15px rgba(255,107,53,.4);border:none}}.back-to-top.visible{{opacity:1}}.back-to-top:hover{{transform:translateY(-3px);box-shadow:0 6px 20px rgba(255,107,53,.6)}}
.show-more-wrap{{text-align:center;margin-top:1.5rem}}
.show-more-btn{{display:inline-block;padding:10px 32px;border-radius:999px;font-weight:700;font-size:14px;cursor:pointer;transition:all .2s;border:2px solid;background:transparent}}
.show-more-btn:hover{{transform:translateY(-2px)}}
</style>
</head>
<body>

<nav class="fixed top-0 w-full z-50 border-b" style="background:{navBg};border-color:#{navBorder}">
<div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
<a href="/" class="flex items-center gap-2.5 flex-shrink-0">
{nav_logo}
<span class="text-xl font-bold tracking-tight">{nav_brand}</span>
</a>
<div class="hidden lg:flex items-center gap-6 text-sm font-medium">
<a href="{site_hub_url}" class="text-textSecondary hover:text-accent transition-colors">{site_hub_label}</a>
{nav_links}
</div>
<div class="hidden lg:flex items-center relative flex-1 max-w-xs ml-2" id="searchWrap">
<input type="text" id="searchInput" placeholder="Search..." autocomplete="off"
 class="w-full bg-bgSecondary text-textPrimary text-sm px-3 py-2 rounded-lg border focus:outline-none focus:border-accent transition-colors"
 style="border-color:#{navBorder}">
<div class="search-dropdown" id="searchDropdown"></div>
</div>
<button class="lg:hidden text-textSecondary text-2xl" id="menuBtn" aria-label="Menu">&#9776;</button>
</div>
<div id="mobileMenu" class="hidden lg:hidden bg-bgPrimary border-t border-gray-800 px-4 py-4 space-y-3 text-sm font-medium">
<div class="relative mb-2">
<input type="text" id="searchInputMobile" placeholder="Search..." autocomplete="off"
 class="w-full bg-bgSecondary text-textPrimary text-sm px-3 py-2 rounded-lg border focus:outline-none focus:border-accent transition-colors"
 style="border-color:#{navBorder}">
<div class="search-dropdown" id="searchDropdownMobile"></div>
</div>
<a href="{site_hub_url}" class="block text-textSecondary hover:text-accent transition-colors">{site_hub_label}</a>
{mobile_nav_links}
</div>
</nav>

{hero_section}

{breadcrumb_html}

{category_cards_section}
{guide_section}
{hot_topics_section}
{character_section}


{category_index_section}

{char_detail_section}

<footer class="bg-bgSecondary border-t py-16 px-4" style="border-color:#{footerBorderHex}">
<div class="max-w-7xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
<div>
<div class="flex items-center gap-2.5 mb-4">
{footer_logo}
<span class="text-xl font-bold">{footer_brand}</span>
</div>
<p class="text-sm text-textSecondary leading-relaxed">{footer_blurb}</p>
</div>
<div>
<h4 class="font-bold mb-4">Categories</h4>
<ul class="space-y-2 text-sm text-textSecondary">
{footer_categories}
</ul>
</div>
<div>
<h4 class="font-bold mb-4">{footer_links_title}</h4>
{footer_links}
</div>
<div>
<h4 class="font-bold mb-4">About</h4>
<ul class="space-y-2 text-sm text-textSecondary">
<li><a href="/about.html" class="hover:text-accent transition-colors">About</a></li>
<li><a href="/contact.html" class="hover:text-accent transition-colors">Contact</a></li>
<li><a href="/sitemap.html" class="hover:text-accent transition-colors">Sitemap</a></li>
</ul>
</div>
</div>
<div class="max-w-7xl mx-auto mt-12 pt-6 border-t text-center text-sm text-textSecondary" style="border-color:#{footerBorderHex}">
<p>&copy; 2026 {site_name} by <a href="https://www.jycsd.com" class="text-accent hover:underline">Myers Media</a>. {copyright_note}</p>
</div>
</footer>

<script>
function toggleReadMore(){{var s=document.getElementById('descShort');var f=document.getElementById('descFull');var t=document.getElementById('descToggle');if(!f)return;if(f.style.display==='none'||!f.style.display){{f.style.display='inline';s.style.display='none';t.textContent=' Read less';}}else{{f.style.display='none';s.style.display='inline';t.textContent='... Read more';}}}}
(function(){{
var slides=document.querySelectorAll('.carousel-slide');
var dots=document.querySelectorAll('.carousel-dot');
var current=0;
function goTo(idx){{if(!slides.length)return;slides[current].classList.remove('active');dots[current].classList.remove('active');current=idx;slides[current].classList.add('active');dots[current].classList.add('active')}}
dots.forEach(function(dot){{dot.addEventListener('click',function(){{goTo(parseInt(this.dataset.slide))}})}});
document.getElementById('carouselPrev')?.addEventListener('click',function(){{goTo((current-1+slides.length)%slides.length)}});
document.getElementById('carouselNext')?.addEventListener('click',function(){{goTo((current+1)%slides.length)}});
if(slides.length>1)setInterval(function(){{goTo((current+1)%slides.length)}},5000);
document.getElementById('menuBtn').addEventListener('click',function(){{document.getElementById('mobileMenu').classList.toggle('hidden')}});
var btt=document.getElementById('backToTop');if(btt){{window.addEventListener('scroll',function(){{if(window.scrollY>300){{btt.classList.add('visible')}}else{{btt.classList.remove('visible')}}}});btt.addEventListener('click',function(){{window.scrollTo({{top:0,behavior:'smooth'}})}})}}
{search_js}
}})();
</script>
<button class="back-to-top" id="backToTop" aria-label="Back to top">&#8593;</button>
</body>
</html>'''

SEARCH_JS = '''
var searchData=[];
(function(){var si=document.getElementById('searchInput');var sim=document.getElementById('searchInputMobile');var dd=document.getElementById('searchDropdown');var ddm=document.getElementById('searchDropdownMobile');var focusIdx=-1;
function loadIdx(){var xhr=new XMLHttpRequest();xhr.open('GET','/search-index.json',true);xhr.onload=function(){if(xhr.status===200){try{searchData=JSON.parse(xhr.responseText)}catch(e){}}};xhr.send()}
function filter(q,ddEl){focusIdx=-1;ddEl.innerHTML='';if(!q||q.length<2){ddEl.classList.remove('active');return}
q=q.toLowerCase();var matches=[];for(var i=0;i<searchData.length;i++){var s=searchData[i];if(s.name.toLowerCase().indexOf(q)!==-1||s.desc.toLowerCase().indexOf(q)!==-1){matches.push(s);if(matches.length>=8)break}}
if(!matches.length){ddEl.innerHTML='<div class="search-empty">No results found</div>';ddEl.classList.add('active');return}
for(var i=0;i<matches.length;i++){var m=matches[i];var typeColors={character:'rgba(255,107,53,.2)',category:'rgba(100,180,255,.2)',guide:'rgba(100,200,100,.2)',hot_topic:'rgba(255,180,50,.2)'};var tc=m.color||'#888';var div=document.createElement('div');div.className='search-result';div.setAttribute('data-url',m.url);div.innerHTML='<span class="sr-type" style="color:'+tc+';background:'+(typeColors[m.type]||'rgba(150,150,150,.2)')+'">'+m.type.replace('_',' ')+'</span><span style="flex:1;min-width:0"><strong style="display:block;font-size:14px">'+m.name+'</strong><small style="color:#8b949e;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+(m.desc||'')+'</small></span>';div.addEventListener('click',function(){{window.location.href=this.getAttribute('data-url')}});ddEl.appendChild(div)}ddEl.classList.add('active')}
function navigate(ddEl,dir){var items=ddEl.querySelectorAll('.search-result');if(!items.length)return;focusIdx+=dir;if(focusIdx<0)focusIdx=items.length-1;if(focusIdx>=items.length)focusIdx=0;for(var i=0;i<items.length;i++)items[i].classList.toggle('focused',i===focusIdx)}
function selectFocused(ddEl){var items=ddEl.querySelectorAll('.search-result');if(focusIdx>=0&&focusIdx<items.length)window.location.href=items[focusIdx].getAttribute('data-url')}
if(si){si.addEventListener('input',function(){{filter(this.value,dd)}});si.addEventListener('keydown',function(e){{if(e.key==='ArrowDown'){e.preventDefault();navigate(dd,1)}else if(e.key==='ArrowUp'){e.preventDefault();navigate(dd,-1)}else if(e.key==='Enter'){e.preventDefault();if(focusIdx<0){focusIdx=0;var fi=dd.querySelectorAll('.search-result');if(fi.length>0)window.location.href=fi[0].getAttribute('data-url')}else{selectFocused(dd)}}else if(e.key==='Escape'){dd.classList.remove('active')}}});si.addEventListener('focus',function(){{if(this.value.length>=2)filter(this.value,dd)}});si.addEventListener('blur',function(){{setTimeout(function(){{dd.classList.remove('active')}},200)}})}
if(sim){sim.addEventListener('input',function(){{filter(this.value,ddm)}});sim.addEventListener('keydown',function(e){{if(e.key==='ArrowDown'){e.preventDefault();navigate(ddm,1)}else if(e.key==='ArrowUp'){e.preventDefault();navigate(ddm,-1)}else if(e.key==='Enter'){e.preventDefault();if(focusIdx<0){focusIdx=0;var fi=ddm.querySelectorAll('.search-result');if(fi.length>0)window.location.href=fi[0].getAttribute('data-url')}else{selectFocused(ddm)}}else if(e.key==='Escape'){ddm.classList.remove('active')}}});sim.addEventListener('focus',function(){{if(this.value.length>=2)filter(this.value,ddm)}});sim.addEventListener('blur',function(){{setTimeout(function(){{ddm.classList.remove('active')}},200)}})}
loadIdx();
})();
'''


def render_nav_logo(data):
    logo = data.get("logo_image", "")
    if logo:
        return f'<img src="/images/{logo}" alt="{data["site_name"]}" class="w-12 h-12 object-contain rounded-lg">'
    img = data["categories"][0].get("character_img", "")
    if img:
        return f'<img src="/images/{img}" alt="{data["site_name"]}" class="w-12 h-12 object-contain rounded-lg">'
    first_char = data["site_name"][0]
    return f'<div class="w-14 h-14 rounded-xl bg-gradient-to-br from-accent to-accentDark flex items-center justify-center text-2xl font-black text-white">{first_char}</div>'


def render_nav_brand(data):
    name = data["site_name"]
    if name.endswith("Guide"):
        return f'{name[:-5]}<span class="text-accent">{name[-5:]}</span>'
    parts = name.split()
    if len(parts) > 1:
        return f'{parts[0]} <span class="text-accent">{" ".join(parts[1:])}</span>'
    return name


def render_nav_links(data):
    links = []
    for cat in data["categories"]:
        links.append(f'<a href="/guides/{cat["slug"]}/" class="text-textSecondary hover:text-accent transition-colors">{cat["name"]}</a>')
    if is_anime_data(data):
        for atype in ANIME_ITEM_TYPES:
            if data.get(atype["key"]) and atype["slug"] not in {c["slug"] for c in data.get("categories", [])}:
                links.append(f'<a href="/guides/{atype["slug"]}/" class="text-textSecondary hover:text-accent transition-colors">{atype["name"]}</a>')
    return '\n'.join(links)


def render_mobile_nav_links(data):
    links = []
    for cat in data["categories"]:
        links.append(f'<a href="/guides/{cat["slug"]}/" class="block text-textSecondary hover:text-accent transition-colors">{cat["name"]}</a>')
    if is_anime_data(data):
        for atype in ANIME_ITEM_TYPES:
            if data.get(atype["key"]) and atype["slug"] not in {c["slug"] for c in data.get("categories", [])}:
                links.append(f'<a href="/guides/{atype["slug"]}/" class="block text-textSecondary hover:text-accent transition-colors">{atype["name"]}</a>')
    return '\n'.join(links)


def render_carousel(data):
    chars = data.get("characters", [])
    cats = data["categories"]
    accent = data["accent"]
    hero_title = data.get("hero_title", data["site_name"])
    hero_subtitle = data.get("hero_subtitle", "")

    if not chars:
        slide = f'''<div class="carousel-slide active">
<div class="absolute inset-0 bg-gray-950"></div>
<div class="absolute inset-0" style="background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
<div class="relative max-w-7xl mx-auto px-4 h-full flex items-center justify-center">
<div class="text-center">
<h1 class="text-4xl md:text-6xl font-black text-white text-shadow mb-4">{hero_title}</h1>
<p class="text-lg text-gray-300 text-shadow mb-6 max-w-lg mx-auto">{hero_subtitle}</p>
<div class="flex gap-3 justify-center">
<a href="/guides/{cats[0]["slug"]}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">Explore {cats[0]["name"]}</a>
</div>
</div></div></div>'''
        return slide, ''

    count = min(len(chars), 8)
    if count < 5:
        count = len(chars)
    selected = chars[:count]
    slides = []
    dots = []

    for i, char in enumerate(selected):
        active = " active" if i == 0 else ""
        heading_tag = "1" if i == 0 else "2"
        char_detail_url = resolve_char_detail_url(data, char)

        slides.append(f'''<div class="carousel-slide{active}">
<div class="absolute inset-0 bg-gray-950"></div>
<a href="{char_detail_url}"><img src="/images/{char["image"]}" alt="{char["name"]}" class="absolute inset-0 w-full h-full object-contain" loading="eager"></a>
<div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
<div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-7xl mx-auto px-4">
<h{heading_tag} class="text-4xl md:text-6xl font-black text-white text-shadow mb-2">{char["name"]}</h{heading_tag}>
<p class="text-lg text-gray-300 text-shadow max-w-xl">{char.get("role", "")}</p>
<a href="{char_detail_url}" class="inline-block mt-4 bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">View Guide</a>
</div>
</div>''')
        dots.append(f'<div class="carousel-dot{active}" data-slide="{i}"></div>')

    return '\n'.join(slides), '\n'.join(dots)


def render_category_hero(data, category):
    cat_name = category["name"]
    cat_slug = category["slug"]
    cat_color = category.get("color", data["accent"])
    cat_count = category.get("count", "")
    cat_img = category.get("character_img", "")

    image_html = ""
    if cat_img:
        image_html = f'<img src="/images/{cat_img}" alt="{cat_name} — category overview" title="{cat_name} category" class="char-img h-[380px] max-h-[380px] w-auto object-contain" loading="eager">'

    return f'''<section class="relative w-full overflow-hidden pt-28 pb-16" style="background:linear-gradient(135deg, #111827 0%, #1a1f2e 50%, {cat_color}18 100%)">
<div class="absolute inset-0 opacity-15" style="background:radial-gradient(ellipse at 30% 50%, {cat_color}, transparent 70%);"></div>
<div class="relative max-w-7xl mx-auto px-4">
<div class="grid md:grid-cols-2 gap-8 items-center">
<div>
<span class="inline-block text-xs font-bold uppercase tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full mb-4">Category</span>
<h1 class="text-4xl md:text-6xl font-black mb-4">All {cat_name}</h1>
<p class="text-lg text-textSecondary mb-4 max-w-lg">Browse our complete collection of {cat_name.lower()} guides — {cat_count} guides covering every {cat_name.lower()} in {data["site_name"]}.</p>
<div class="flex gap-3">
<a href="/" class="border border-textSecondary/30 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">Home</a>
</div>
</div>
<div class="hidden md:flex justify-center items-end">
{image_html}
</div>
</div>
</div>
</section>'''


def render_category_cards(data):
    cards = []
    all_cats = get_all_categories(data)
    border_hex = theme_colors(data)["borderHex"]
    for cat in all_cats:
        if cat.get("character_img"):
            img_html = f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]} category" class="w-full h-full object-cover char-img group-hover:scale-110 transition-transform" style="object-position:center top" loading="eager">'
        else:
            sys.stderr.write(f"WARNING: {data.get('site_name','?')} category '{cat['name']}' missing character_img\n")
            img_html = f'<span style="font-size:24px;font-weight:bold;color:{cat.get("color", data["accent"])}">{cat["name"][0]}</span>'
        cards.append(f'''<a href="/guides/{cat["slug"]}/" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex items-center p-5 gap-5 flex-1 min-w-[180px]" style="border-color:#{border_hex}">
<div class="w-20 h-20 md:w-24 md:h-24 flex-shrink-0 flex items-center justify-center bg-bgPrimary rounded-xl overflow-hidden">{img_html}</div>
<div class="flex-1 min-w-0">
<div class="font-bold text-base md:text-lg">{cat["name"]}</div>
<div class="text-sm text-textSecondary mt-1">{cat["count"]} guides</div>
</div>
</a>''')
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<h2 class="text-2xl font-black mb-6">All Categories</h2>
<div class="flex flex-wrap gap-4 justify-center items-stretch">
{"".join(cards)}
</div></section>'''


def render_guide_section(data):
    cards_data = data.get("guide_cards", [])
    if not cards_data:
        return ""
    cards = []
    border_hex = theme_colors(data)["borderHex"]
    for g in cards_data:
        if g.get("image"):
            img_tag = f'<img src="/images/{g["image"]}" alt="{g["title"]}" title="{g["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" style="object-position:center top" loading="eager">'
        else:
            sys.stderr.write(f"WARNING: {data.get('site_name','?')} guide '{g.get('title','?')}' missing image field\n")
            img_tag = f'<span style="font-size:24px;font-weight:bold;color:{g.get("cat_color", data["accent"])}">{g["title"][0]}</span>'
        cards.append(f'''<a href="{g["link"]}" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[160px]" style="border-color:#{border_hex}">
<div class="w-48 md:w-56 lg:w-64 flex-shrink-0 bg-bgPrimary flex items-center justify-center relative overflow-hidden p-4">
<div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 50% 50%, {g.get("cat_color", data["accent"])}, transparent);"></div>
{img_tag}
</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<span class="text-sm font-semibold px-2 py-1 rounded self-start" style="color:{g.get("cat_color", data["accent"])};background:{g.get("cat_color", data["accent"])}1a">{g["category"]}</span>
<h3 class="font-bold text-lg mt-2 mb-1 leading-snug group-hover:text-accent transition-colors">{g["title"]}</h3>
<time class="text-sm text-textSecondary mt-2 block">{g["date"]}</time>
</div>
</a>''')
    cols = min(len(cards_data), 2)
    first_cat_slug = data["categories"][0]["slug"]
    return f'''<section class="max-w-7xl mx-auto px-4 py-16">
<div class="flex items-end justify-between mb-8">
<div><p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Fresh Content</p><h2 class="text-3xl font-black">Latest Guides</h2></div>
<a href="/guides/{first_cat_slug}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All &rarr;</a>
</div>
<div class="grid lg:grid-cols-{cols} gap-5">
{"".join(cards)}
</div></section>'''


def render_hot_topics(data):
    topics = data.get("hot_topics", [])
    if not topics:
        return ""
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for t in topics:
        img_html = (f'<img src="/images/{t["image"]}" alt="{t["title"]}" title="{t["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" style="object-position:center top" loading="eager">'
                    if t.get("image") else
                    f'<div class="w-full h-full flex items-center justify-center text-3xl font-black" style="color:{t.get("color", data["accent"])};background:{t.get("color", data["accent"])}15">{t["title"][0]}</div>')
        items.append(f'''<a href="{t["link"]}" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[130px]" style="border-color:#{border_hex}">
<div class="w-32 md:w-40 lg:w-48 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img_html}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-lg group-hover:text-accent transition-colors">{t["title"]}</h3>
<p class="text-base text-textSecondary mt-1.5">{t["desc"]}</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">Read Guide</span>
</div>
</a>''')
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<div class="flex items-end justify-between mb-6">
<div><p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Trending</p><h2 class="text-2xl font-black">Hot Topics This Month</h2></div>
<a href="/guides/{data["categories"][0]["slug"]}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All &rarr;</a>
</div>
<div class="space-y-3">{"".join(items)}</div></section>'''


def render_character_section(data):
    chars = data.get("characters", [])
    if not chars:
        return ""
    items = []
    for c in chars:
        detail_url = resolve_char_detail_url(data, c)
        if c.get("image"):
            img = f'<img src="/images/{c["image"]}" alt="{c["name"]} — {c.get("role", "")}" title="{c["name"]} — {c.get("role", "")}" class="w-full h-auto block" loading="eager">'
        else:
            fc = c["name"][0]
            cc = c.get("color", data["accent"])
            img = f'<div class="w-full min-h-[200px] flex items-center justify-center text-3xl font-black" style="color:{cc};background:{cc}15">{fc}</div>'
        items.append(f'''<div class="break-inside-avoid mb-4 relative group rounded-xl overflow-hidden">
<a href="{detail_url}" class="block relative overflow-hidden rounded-xl">
{img}
<div class="gradient-overlay absolute bottom-0 left-0 right-0 p-4 pt-12">
<h3 class="font-bold text-lg text-white text-shadow">{c["name"]}</h3>
<p class="text-xs text-gray-300 mt-0.5 text-shadow">{c.get("role", "")[:60]}</p>
</div>
</a>
</div>''')
    
    visible = items[:12]
    hidden = items[12:]
    
    extra = ""
    if hidden:
        hidden_items = "".join(hidden)
        extra = f'''<div id="moreChars" style="display:none"><div class="masonry-grid">{hidden_items}</div></div>
<div class="show-more-wrap"><button class="show-more-btn" style="color:{data["accent"]};border-color:{data["accent"]}" onclick="var el=document.getElementById('moreChars'),btn=this;el.style.display=el.style.display==='none'?'block':'none';btn.textContent=el.style.display==='none'?'Show All':'Show Less'">Show All ({len(hidden)} more)</button></div>'''
    
    first_cat = data["categories"][0]["slug"]
    return f'''<section class="max-w-7xl mx-auto px-4 py-16">
<div class="flex items-end justify-between mb-8">
<div><p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Characters</p><h2 class="text-3xl font-black">Meet the <span class="text-accent">Characters</span></h2></div>
<a href="/guides/{first_cat}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All &rarr;</a>
</div>
<div class="masonry-grid">
{"".join(visible)}
</div>{extra}</section>'''
def render_category_index(data):
    cats = data["categories"]
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for cat in cats:
        img_html = (f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]}" class="w-full h-full object-cover" style="object-position:center top" loading="eager">'
                    if cat.get("character_img") else
                    f'<div class="w-full h-full flex items-center justify-center text-2xl font-black" style="color:{cat.get("color", data["accent"])};background:{cat.get("color", data["accent"])}15">{cat["name"][0]}</div>')
        items.append(f'''<a href="/guides/{cat["slug"]}/" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[120px]" style="border-color:#{border_hex}">
<div class="w-36 md:w-44 lg:w-52 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img_html}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-xl group-hover:text-accent transition-colors">{cat["name"]}</h3>
<p class="text-base text-textSecondary mt-1">{cat["name"]} &mdash; Complete Guide</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">{cat["count"]} guides</span>
</div>
</a>''')
    first_cat = cats[0]["slug"]
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<div class="flex items-end justify-between mb-8">
<h2 class="text-3xl font-black">Every Guide Category</h2>
<a href="/guides/{first_cat}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All &rarr;</a>
</div>
<div class="flex flex-wrap gap-4 justify-center">
{"".join(items)}
</div></section>'''


def render_footer(data):
    all_cats = get_all_categories(data)
    cats = '\n'.join(
        f'<li><a href="/guides/{c["slug"]}/" class="hover:text-accent transition-colors">{c["name"]}</a></li>'
        for c in all_cats[:5]
    )
    links = '''<select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-accent cursor-pointer">
    <option value="">— Network —</option>
    <option value="https://www.jycsd.com">Myers Media</option>
    <option value="https://games.jycsd.com">Game Guides</option>
    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
</select>
<select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-accent cursor-pointer">
    <option value="">— More Sites —</option>
    <option value="https://healthy.jycsd.com">HealthyEats</option>
    <option value="https://pets.jycsd.com">PetCare Hub</option>
    <option value="https://home.jycsd.com">HomeJoy</option>
    <option value="https://finance.jycsd.com">MoneyWise</option>
    <option value="https://tech.jycsd.com">TechNest</option>
    <option value="https://travel.jycsd.com">TripRoute</option>
</select>'''
    links_title = "Our Network"
    return cats, links, links_title


def render_footer_blurb(data):
    st = data.get("site_type", "game")
    if st == "anime":
        return "Expert anime character guides, power system breakdowns, and arc analyses. Part of the Anime Hub Network."
    return "Expert game guides, tier lists, and walkthroughs. Part of the Game Hub Network."


def render_copyright_note(data):
    st = data.get("site_type", "game")
    if st == "anime":
        return "All anime characters and trademarks belong to their respective owners."
    return "All game trademarks belong to their respective owners."


def render_char_detail_page(data, char):
    tc = theme_colors(data)
    site_name = data["site_name"]
    domain = data["domain"]
    accent = data["accent"]
    cat_slug = get_char_category_slug(data, char)
    char_slug = slugify(char["name"])
    char_color = char.get("color", accent)

    cat_name = cat_slug.replace("-", " ").title()
    cat_obj = None
    for c in data.get("categories", []):
        if c["slug"] == cat_slug:
            cat_obj = c
            cat_name = c["name"]
            break

    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    copyright_note = render_copyright_note(data)

    title_tag = f"{char['name']} — {site_name}"
    meta_desc = char.get("desc", "") or f"{char['name']} — {char.get('role', '')} character guide for {site_name}."
    canonical = f"https://{domain}/guides/{cat_slug}/{char_slug}.html"

    breadcrumb_html = render_breadcrumb(data, {"name": cat_name, "slug": cat_slug}, char["name"])

    img_html = ""
    if char.get("image"):
        img_html = f'<img src="/images/{char["image"]}" alt="{char["name"]} — {char.get("role", "")}" title="{char["name"]} — {char.get("role", "")}" class="w-full h-auto max-h-[600px] object-contain" loading="eager">'
    else:
        first_letter = char["name"][0]
        img_html = f'<div class="w-full h-96 flex items-center justify-center text-6xl font-black" style="color:{char_color};background:{char_color}15">{first_letter}</div>'

    role_html = ""
    if char.get("role"):
        role_html = f'<span class="inline-block text-sm font-bold px-3 py-1 rounded-full" style="color:{char_color};background:{char_color}1a">{char["role"]}</span>'

    # Description with read-more: show 2 sentences initially
    full_desc = char.get("desc", "")
    short_desc = full_desc
    has_more_desc = False
    if full_desc:
        sep = full_desc.replace(". ", ".|||").replace("! ", "!|||").replace("? ", "?|||").split("|||")
        if len(sep) > 2:
            short_desc = " ".join(sep[:2])
            has_more_desc = True

    info_items = []
    if char.get("species"):
        info_items.append(("Species", char["species"]))
    if char.get("first_appearance"):
        info_items.append(("First Appearance", char["first_appearance"]))
    if char.get("power_level"):
        info_items.append(("Power Level", char["power_level"]))
    if char.get("signature_moves"):
        moves = char["signature_moves"]
        if isinstance(moves, list):
            moves = ", ".join(moves[:4])
        info_items.append(("Signature Moves", moves))

    info_badges_html = ""
    if info_items:
        info_badges_html = "".join(
            f'<div class="bg-bgSecondary/50 rounded-lg px-4 py-2 border text-center flex-shrink-0" style="border-color:#{tc["borderHex"]}">'
            f'<span class="text-xs font-bold uppercase tracking-wider text-accent opacity-80 block">{k}</span>'
            f'<span class="text-sm font-medium mt-0.5 block">{v}</span></div>'
            for k, v in info_items
        )

    related_html = _render_related_characters(data, char)
    schema = schema_org_person(data, char)

    # Description HTML with optional read-more
    desc_html = f'<span id="descShort">{short_desc}</span>'
    if has_more_desc:
        desc_html += f'<span id="descFull" style="display:none">{full_desc}</span>'
        desc_html += f' <span>... <a href="javascript:void(0)" onclick="toggleReadMore()" id="descToggle" class="text-accent font-medium">Read more</a></span>'

    char_detail_html = f"""<section class="max-w-7xl mx-auto px-4 py-12">
<!-- Sidebar ads -->
<div class="hidden xl:block fixed left-0 top-1/2 -translate-y-1/2 z-40 w-[160px] ml-4">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-3 py-6 text-center text-sm text-textSecondary/50 h-[600px] flex flex-col items-center justify-center" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>
<div class="hidden xl:block fixed right-0 top-1/2 -translate-y-1/2 z-40 w-[160px] mr-4">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-3 py-6 text-center text-sm text-textSecondary/50 h-[600px] flex flex-col items-center justify-center" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>

<div class="max-w-4xl mx-auto">
<div class="flex justify-center mb-6">
<div class="bg-bgPrimary rounded-2xl border flex items-center justify-center w-full max-w-[80%]" style="border-color:#{tc["borderHex"]}">
<div class="p-4 w-full flex items-center justify-center" style="max-height:600px">
{img_html}
</div>
</div>
</div>
<div class="text-center mb-6">
{breadcrumb_html}
<h1 class="text-4xl md:text-5xl font-black mb-2">{char["name"]}</h1>
{role_html}
<p class="text-textSecondary mt-2 text-sm">Category: <a href="/guides/{cat_slug}/" class="text-accent hover:underline">{cat_name}</a> &middot; <a href="/" class="text-accent hover:underline">Home</a></p>
</div>
<div class="flex flex-wrap justify-center gap-3 mb-8">
{info_badges_html}
</div>
<!-- Ad slot -->
<div class="max-w-3xl mx-auto my-8">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-4 py-8 text-center text-sm text-textSecondary/50" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>
<div class="max-w-3xl mx-auto">
<p class="text-base text-textSecondary leading-relaxed">{desc_html}</p>
</div>
<!-- Ad slot before related -->
<div class="max-w-3xl mx-auto my-8">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-4 py-8 text-center text-sm text-textSecondary/50" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>
{related_html}
</div>
</section>"""

    return HTML_TEMPLATE.format(
        title_tag=title_tag,
        meta_desc=meta_desc[:160],
        og_title=f"{char['name']} — {site_name}",
        canonical_url=canonical,
        schema_markup=schema,
        bgPrimary=tc["bgPrimary"],
        bgSecondary=tc["bgSecondary"],
        bgCard=tc["bgCard"],
        textPrimary=tc["textPrimary"],
        textSecondary=tc["textSecondary"],
        bodyBg=tc["bodyBg"],
        navBg=tc["navBg"],
        navBorder=tc["navBorder"],
        glow=tc["glow"].format(accent=accent),
        accent=accent,
        accent_dark=data.get("accent_dark", accent),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section="",
        breadcrumb_html="",
        category_cards_section="",
        guide_section="",
        hot_topics_section="",
        character_section="",
        category_index_section="",
        char_detail_section=char_detail_html,
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
        footer_links_title=footer_links_title,
        footer_blurb=footer_blurb,
        footerBorderHex=tc["borderHex"],
        site_name=site_name,
        copyright_note=copyright_note,
        search_js=SEARCH_JS,
    )

def _render_related_characters(data, current_char):
    chars = data.get("characters", [])
    others = [c for c in chars if c["name"] != current_char["name"]]
    if not others:
        return ""

    rng = random.Random(current_char["name"])
    rng.shuffle(others)
    related = others[:8]

    items = []
    border_hex = theme_colors(data)["borderHex"]
    for c in related:
        detail_url = resolve_char_detail_url(data, c)
        if c.get("image"):
            img = f'<img src="/images/{c["image"]}" alt="{c["name"]} — {c.get("role", "")}" title="{c["name"]}" class="w-full h-full object-cover" style="object-position:center top" loading="eager">'
        else:
            first_char = c["name"][0]
            cc = c.get("color", data["accent"])
            img = f'<div class="w-full h-full flex items-center justify-center text-2xl font-black" style="color:{cc};background:{cc}20">{first_char}</div>'
        items.append(f'''<div class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex-shrink-0 w-40" style="border-color:#{border_hex}">
<a href="{detail_url}" class="block">
<div class="w-full aspect-square bg-bgPrimary overflow-hidden flex items-center justify-center">{img}</div>
<div class="p-3 text-center">
<h4 class="font-bold text-sm">{c["name"]}</h4>
<p class="text-xs text-textSecondary mt-0.5">{c.get("role", "")}</p>
</div>
</a>
</div>''')

    return f'''<div class="max-w-7xl mx-auto px-4 pb-12">
<div class="border-t pt-10" style="border-color:#{theme_colors(data)["borderHex"]}">
<h2 class="text-2xl font-black mb-6">Related Characters</h2>
<div class="scroll-snap-x pb-2">
{"".join(items)}
</div>
</div></div>'''

def render_category_page(data, category):
    tc = theme_colors(data)
    site_name = data["site_name"]
    domain = data["domain"]
    accent = data["accent"]
    cat_name = category["name"]
    cat_slug = category["slug"]
    cat_count = category.get("count", "")

    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    copyright_note = render_copyright_note(data)

    title_tag = f"All {cat_name} Guides — {site_name}"
    meta_desc = f"Complete {cat_name.lower()} guide collection for {site_name}. {cat_count} in-depth guides covering every {cat_name.lower()}."
    canonical = f"https://{domain}/guides/{cat_slug}/"

    char_html = ""
    chars = data.get("characters", [])
    if chars:
        filtered_chars = [c for c in chars if get_char_category_slug(data, c) == cat_slug]
        if filtered_chars:
            char_html = _render_full_characters_grid(data, filtered_chars, cat_name)

    return HTML_TEMPLATE.format(
        title_tag=title_tag,
        meta_desc=meta_desc,
        og_title=f"{cat_name} Guides — {site_name}",
        canonical_url=canonical,
        schema_markup="",
        bgPrimary=tc["bgPrimary"],
        bgSecondary=tc["bgSecondary"],
        bgCard=tc["bgCard"],
        textPrimary=tc["textPrimary"],
        textSecondary=tc["textSecondary"],
        bodyBg=tc["bodyBg"],
        navBg=tc["navBg"],
        navBorder=tc["navBorder"],
        glow=tc["glow"].format(accent=accent),
        accent=accent,
        accent_dark=data.get("accent_dark", accent),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section="",
        breadcrumb_html="",
        category_cards_section="",
        guide_section="",
        hot_topics_section="",
        character_section=char_html,
        category_index_section="",
        char_detail_section="",
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
        footer_links_title=footer_links_title,
        footer_blurb=footer_blurb,
        footerBorderHex=tc["borderHex"],
        site_name=site_name,
        copyright_note=copyright_note,
        search_js=SEARCH_JS,
    )


def _render_filtered_guides(data, guides, cat_name):
    cards = []
    border_hex = theme_colors(data)["borderHex"]
    for g in guides:
        if g.get("image"):
            img_tag = f'<img src="/images/{g["image"]}" alt="{g["title"]}" title="{g["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" style="object-position:center top" loading="eager">'
        else:
            sys.stderr.write(f"WARNING: {data.get('site_name','?')} guide '{g.get('title','?')}' missing image field\n")
            img_tag = f'<span style="font-size:24px;font-weight:bold;color:{g.get("cat_color", data["accent"])}">{g["title"][0]}</span>'
        cards.append(f'''<a href="{g["link"]}" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[160px]" style="border-color:#{border_hex}">
<div class="w-48 md:w-56 lg:w-64 flex-shrink-0 bg-bgPrimary flex items-center justify-center relative overflow-hidden p-4">
<div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 50% 50%, {g.get("cat_color", data["accent"])}, transparent);"></div>
{img_tag}
</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<span class="text-sm font-semibold px-2 py-1 rounded self-start" style="color:{g.get("cat_color", data["accent"])};background:{g.get("cat_color", data["accent"])}1a">{g["category"]}</span>
<h3 class="font-bold text-lg mt-2 mb-1 leading-snug group-hover:text-accent transition-colors">{g["title"]}</h3>
<time class="text-sm text-textSecondary mt-2 block">{g["date"]}</time>
</div>
</a>''')
    cols = min(len(guides), 2)
    return f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="mb-8"><h2 class="text-3xl font-black">{cat_name} Guides</h2><p class="text-textSecondary mt-2">In-depth {cat_name.lower()} coverage</p></div>
<div class="grid lg:grid-cols-{cols} gap-5">{"".join(cards)}</div></section>'''


def _render_full_characters_grid(data, chars, cat_name="Characters"):
    items = []
    for c in chars:
        detail_url = resolve_char_detail_url(data, c)
        if c.get("image"):
            img = f'<img src="/images/{c["image"]}" alt="{c["name"]}" title="{c["name"]}" class="w-full h-auto block" loading="eager">'
        else:
            fc = c["name"][0]
            cc = c.get("color", data["accent"])
            img = f'<div class="w-full min-h-[200px] flex items-center justify-center text-3xl font-black" style="color:{cc};background:{cc}15">{fc}</div>'
        items.append(f'''<div class="break-inside-avoid mb-4 relative group rounded-xl overflow-hidden">
<a href="{detail_url}" class="block relative overflow-hidden rounded-xl">
{img}
<div class="gradient-overlay absolute bottom-0 left-0 right-0 p-4 pt-12">
<h3 class="font-bold text-lg text-white text-shadow">{c["name"]}</h3>
</div>
</a>
</div>''')
    
    visible = items[:12]
    hidden = items[12:]
    
    extra = ""
    if hidden:
        hidden_items = "".join(hidden)
        extra = f'''<div id="moreGrid" style="display:none"><div class="masonry-grid">{hidden_items}</div></div>
<div class="show-more-wrap"><button class="show-more-btn" style="color:{data["accent"]};border-color:{data["accent"]}" onclick="var el=document.getElementById('moreGrid'),btn=this;el.style.display=el.style.display==='none'?'block':'none';btn.textContent=el.style.display==='none'?'Show All':'Show Less'">Show All ({len(hidden)} more)</button></div>'''
    
    return f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="mb-8"><h2 class="text-3xl font-black">All {cat_name}</h2></div>
<div class="masonry-grid">{"".join(visible)}</div>{extra}</section>'''


def _render_filtered_hot_topics(data, topics, cat_name):
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for t in topics:
        img_html = (f'<img src="/images/{t["image"]}" alt="{t["title"]}" title="{t["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" style="object-position:center top" loading="eager">'
                    if t.get("image") else
                    f'<div class="w-full h-full flex items-center justify-center text-3xl font-black" style="color:{t.get("color", data["accent"])};background:{t.get("color", data["accent"])}15">{t["title"][0]}</div>')
        items.append(f'''<a href="{t["link"]}" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[130px]" style="border-color:#{border_hex}">
<div class="w-32 md:w-40 lg:w-48 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img_html}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-lg group-hover:text-accent transition-colors">{t["title"]}</h3>
<p class="text-base text-textSecondary mt-1.5">{t["desc"]}</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">Read Guide</span>
</div>
</a>''')
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<div class="mb-6"><h2 class="text-2xl font-black">Hot Topics &mdash; {cat_name}</h2></div>
<div class="space-y-3">{"".join(items)}</div></section>'''


def _render_other_categories(data, other_cats):
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for cat in other_cats:
        img_html = (f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]}" class="w-full h-full object-cover" style="object-position:center top" loading="eager">'
                    if cat.get("character_img") else
                    f'<div class="w-full h-full flex items-center justify-center text-2xl font-black" style="color:{cat.get("color", data["accent"])};background:{cat.get("color", data["accent"])}15">{cat["name"][0]}</div>')
        items.append(f'''<a href="/guides/{cat["slug"]}/" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[120px]" style="border-color:#{border_hex}">
<div class="w-36 md:w-44 lg:w-52 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img_html}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-xl group-hover:text-accent transition-colors">{cat["name"]}</h3>
<p class="text-base text-textSecondary mt-1">{cat["name"]} &mdash; Complete Guide</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">{cat["count"]} guides</span>
</div>
</a>''')
    cols = min(len(other_cats), 3)
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<h2 class="text-2xl font-black mb-6">Other Categories</h2>
<div class="grid md:grid-cols-2 lg:grid-cols-{cols} gap-5">{"".join(items)}</div></section>'''


def render_anime_item_detail(data, item, atype):
    tc = theme_colors(data)
    site_name = data["site_name"]
    domain = data["domain"]
    accent = data["accent"]
    item_slug = slugify(item["name"])
    item_color = item.get("color", accent)

    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    copyright_note = render_copyright_note(data)

    title_tag = f"{item['name']} ({atype['singular']}) — {site_name}"
    meta_desc = (item.get("desc", "") or f"{item['name']} {atype['singular'].lower()} guide for {site_name}.")[:160]
    canonical = f"https://{domain}/guides/{atype['slug']}/{item_slug}.html"

    breadcrumb_html = render_breadcrumb(data, {"name": atype["name"], "slug": atype["slug"]}, item["name"])

    img_html = ""
    if item.get("image"):
        img_html = f'<img src="/images/{item["image"]}" alt="{item["name"]} — {atype["singular"]}" title="{item["name"]} — {atype["singular"]}" class="char-img w-full h-auto max-h-[800px] object-contain" loading="eager">'
    else:
        first_letter = item["name"][0]
        img_html = f'<div class="w-full h-full flex items-center justify-center text-6xl font-black" style="color:{item_color};background:{item_color}15">{first_letter}</div>'

    schema = schema_org_anime_item(data, item, atype["key"])

    item_detail_html = f'''<section class="max-w-7xl mx-auto px-4 py-12">
<!-- Sidebar ads -->
<div class="hidden xl:block fixed left-0 top-1/2 -translate-y-1/2 z-40 w-[160px] ml-4">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-3 py-6 text-center text-sm text-textSecondary/50 h-[600px] flex flex-col items-center justify-center" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>
<div class="hidden xl:block fixed right-0 top-1/2 -translate-y-1/2 z-40 w-[160px] mr-4">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-3 py-6 text-center text-sm text-textSecondary/50 h-[600px] flex flex-col items-center justify-center" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>

<div class="max-w-4xl mx-auto">
<div class="flex justify-center mb-6">
<div class="bg-bgPrimary rounded-2xl border flex items-center justify-center w-full max-w-[80%]" style="border-color:#{tc["borderHex"]}">
<div class="p-4 w-full flex items-center justify-center" style="max-height:600px">
{img_html}
</div>
</div>
</div>
<div class="text-center mb-6">
{breadcrumb_html}
<span class="inline-block text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-3" style="color:{item_color};background:{item_color}1a">{atype["singular"]}</span>
<h1 class="text-4xl md:text-5xl font-black mb-2">{item["name"]}</h1>
<p class="text-lg text-textSecondary mt-6 leading-relaxed max-w-3xl mx-auto">{item.get("desc", "")}</p>
<!-- Ad slot -->
<div class="my-8 max-w-3xl mx-auto">
<div class="bg-bgSecondary/30 rounded-xl border border-dashed px-4 py-8 text-center text-sm text-textSecondary/50" style="border-color:#{tc["borderHex"]}">
<span class="uppercase tracking-wider text-xs">Advertisement</span>
</div>
</div>
<p class="text-textSecondary mt-4">Category: <a href="/guides/{atype["slug"]}/" class="text-accent hover:underline">{atype["name"]}</a></p>
<div class="flex gap-3 mt-8 justify-center">
<a href="/guides/{atype["slug"]}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">All {atype["name"]}</a>
<a href="/" class="border border-textSecondary/30 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">Back to Home</a>
</div>
</div>
</div>
</section>'''

    return HTML_TEMPLATE.format(
        title_tag=title_tag,
        meta_desc=meta_desc,
        og_title=f"{item['name']} ({atype['singular']}) — {site_name}",
        canonical_url=canonical,
        schema_markup=schema,
        bgPrimary=tc["bgPrimary"],
        bgSecondary=tc["bgSecondary"],
        bgCard=tc["bgCard"],
        textPrimary=tc["textPrimary"],
        textSecondary=tc["textSecondary"],
        bodyBg=tc["bodyBg"],
        navBg=tc["navBg"],
        navBorder=tc["navBorder"],
        glow=tc["glow"].format(accent=accent),
        accent=accent,
        accent_dark=data.get("accent_dark", accent),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section="",
        breadcrumb_html="",
        category_cards_section="",
        guide_section="",
        hot_topics_section="",
        character_section="",
        category_index_section="",
        char_detail_section=item_detail_html,
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
        footer_links_title=footer_links_title,
        footer_blurb=footer_blurb,
        footerBorderHex=tc["borderHex"],
        site_name=site_name,
        copyright_note=copyright_note,
        search_js=SEARCH_JS,
    )


def render_anime_category_index(data, atype, items):
    tc = theme_colors(data)
    site_name = data["site_name"]
    domain = data["domain"]
    accent = data["accent"]
    cat_color = atype.get("color", accent)

    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    copyright_note = render_copyright_note(data)

    title_tag = f"All {atype['name']} — {site_name}"
    meta_desc = f"Complete {atype['name'].lower()} guide for {site_name}. {len(items)} in-depth guides covering every {atype['singular'].lower()}."
    canonical = f"https://{domain}/guides/{atype['slug']}/"

    border_hex = tc["borderHex"]

    grid_items = []
    for item in items:
        item_slug = slugify(item["name"])
        img = (f'<img src="/images/{item["image"]}" alt="{item["name"]}" title="{item["name"]}" class="w-full h-full object-cover" style="object-position:center top" loading="eager">'
               if item.get("image") else
               f'<div class="w-full h-full flex items-center justify-center text-2xl font-black" style="color:{item.get("color", data["accent"])};background:{item.get("color", data["accent"])}15">{item["name"][0]}</div>')
        grid_items.append(f'''<a href="/guides/{atype["slug"]}/{item_slug}.html" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[120px]" style="border-color:#{border_hex}">
<div class="w-36 md:w-44 lg:w-52 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-xl group-hover:text-accent transition-colors">{item["name"]}</h3>
<p class="text-sm text-textSecondary mt-1 line-clamp-2">{item.get("desc", "")}</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">View Details</span>
</div>
</a>''')

    cols = min(3, max(1, len(items) // 2))
    visible_items = grid_items[:12]
    hidden_items = grid_items[12:]

    extra = ""
    if hidden_items:
        hidden_joined = "".join(hidden_items)
        extra = f'''<div id="moreAnime" style="display:none"><div class="grid md:grid-cols-2 lg:grid-cols-{cols} gap-5">{hidden_joined}</div></div>
<div class="show-more-wrap"><button class="show-more-btn" style="color:{accent};border-color:{accent}" onclick="var el=document.getElementById('moreAnime'),btn=this;el.style.display=el.style.display==='none'?'block':'none';btn.textContent=el.style.display==='none'?'Show All':'Show Less'">Show All ({len(hidden_items)} more)</button></div>'''

    all_items_grid = f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="mb-8"><h2 class="text-3xl font-black">All {atype["name"]}</h2><p class="text-textSecondary mt-2">{len(items)} {atype["singular"].lower()} guides</p></div>
<div class="grid md:grid-cols-2 lg:grid-cols-{cols} gap-5">{"".join(visible_items)}</div>{extra}</section>'''

    cats_section = render_category_cards(data)

    return HTML_TEMPLATE.format(
        title_tag=title_tag,
        meta_desc=meta_desc,
        og_title=f"{atype['name']} — {site_name}",
        canonical_url=canonical,
        schema_markup="",
        bgPrimary=tc["bgPrimary"],
        bgSecondary=tc["bgSecondary"],
        bgCard=tc["bgCard"],
        textPrimary=tc["textPrimary"],
        textSecondary=tc["textSecondary"],
        bodyBg=tc["bodyBg"],
        navBg=tc["navBg"],
        navBorder=tc["navBorder"],
        glow=tc["glow"].format(accent=accent),
        accent=accent,
        accent_dark=data.get("accent_dark", accent),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section=render_category_hero(data, {"name": atype["name"], "slug": atype["slug"], "color": cat_color, "character_img": items[0].get("image", "") if items and items[0].get("image") and items[0]["image"] != "goku.png" else "", "count": f"{len(items)}+"}),
        breadcrumb_html="",
        category_cards_section="",
        guide_section="",
        hot_topics_section="",
        character_section="",
        category_index_section=cats_section + all_items_grid,
        char_detail_section="",
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
        footer_links_title=footer_links_title,
        footer_blurb=footer_blurb,
        footerBorderHex=tc["borderHex"],
        site_name=site_name,
        copyright_note=copyright_note,
        search_js=SEARCH_JS,
    )


def render_home_page(data):
    tc = theme_colors(data)
    accent = data["accent"]
    slides, dots = render_carousel(data)

    carousel_html = ""
    if slides.strip():
        carousel_html = f'''<!-- Hero Carousel -->
<section class="relative w-full h-[75vh] overflow-hidden carousel">
{slides}
<button id="carouselPrev" class="carousel-arrow left-4" aria-label="Previous slide">&#10094;</button>
<button id="carouselNext" class="carousel-arrow right-4" aria-label="Next slide">&#10095;</button>
<div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3 z-10">
{dots}
</div>
</section>'''
    else:
        carousel_html = ""

    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links, footer_links_title = render_footer(data)
    footer_blurb = render_footer_blurb(data)
    copyright_note = render_copyright_note(data)

    site_name = data["site_name"]
    domain = data["domain"]
    hero_subtitle = data.get("hero_subtitle", "")
    hero_title = data.get("hero_title", site_name)

    return HTML_TEMPLATE.format(
        title_tag=f'{site_name} — {data.get("tagline", "Game Guides & Wiki")}',
        meta_desc=hero_subtitle,
        og_title=f'{site_name} — Game Guides & Wiki',
        canonical_url=f"https://{domain}/",
        schema_markup="",
        bgPrimary=tc["bgPrimary"],
        bgSecondary=tc["bgSecondary"],
        bgCard=tc["bgCard"],
        textPrimary=tc["textPrimary"],
        textSecondary=tc["textSecondary"],
        bodyBg=tc["bodyBg"],
        navBg=tc["navBg"],
        navBorder=tc["navBorder"],
        glow=tc["glow"].format(accent=accent),
        accent=accent,
        accent_dark=data.get("accent_dark", accent),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section=carousel_html,
        breadcrumb_html="",
        category_cards_section=render_category_cards(data),
        guide_section=render_guide_section(data),
        hot_topics_section=render_hot_topics(data),
        character_section=render_character_section(data),
        category_index_section="",
        char_detail_section="",
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
        footer_links_title=footer_links_title,
        footer_blurb=footer_blurb,
        footerBorderHex=tc["borderHex"],
        site_name=site_name,
        copyright_note=copyright_note,
        search_js=SEARCH_JS,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: py shared/render_game_site.py <site_key> [--all] [--data <file>]")
        data_file_path = DATA_FILE
        all_data = json.loads(data_file_path.read_text(encoding="utf-8"))
        print("Available sites:", ", ".join(all_data.keys()))
        sys.exit(1)

    data_file = DATA_FILE
    args = sys.argv[1:]
    if "--data" in args:
        idx = args.index("--data")
        data_file = ROOT / "shared" / args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    all_data = json.loads(data_file.read_text(encoding="utf-8"))

    if args[0] == "--all":
        keys = list(all_data.keys())
    else:
        keys = [args[0]]

    for key in keys:
        if key not in all_data:
            print(f"Unknown site: {key}")
            continue
        data = all_data[key]
        data["_key"] = key
        site_dir = ROOT / f"{key}-site"
        if not site_dir.exists():
            site_dir.mkdir(parents=True)

        print(f"\n{'='*60}")
        print(f"Rendering: {key} ({data['site_name']})")
        print(f"{'='*60}")

        warnings = validate_prerender(data, site_dir)
        if warnings:
            print(f"  [WARNINGS] {len(warnings)} issue(s):")
            for w in warnings:
                print(f"    ! {w}")
        else:
            print("  [OK] Pre-render validation passed")

        home_html = render_home_page(data)
        out_path = site_dir / "index.html"
        out_path.write_text(home_html, encoding="utf-8")
        print(f"  Home: {out_path}")

        for cat in data.get("categories", []):
            cat_html = render_category_page(data, cat)
            cat_dir = site_dir / "guides" / cat["slug"]
            cat_dir.mkdir(parents=True, exist_ok=True)
            cat_page = cat_dir / "index.html"
            cat_page.write_text(cat_html, encoding="utf-8")
            print(f"  Category: {cat_page}")

        for char in data.get("characters", []):
            detail_html = render_char_detail_page(data, char)
            cat_slug = get_char_category_slug(data, char)
            char_slug = slugify(char["name"])
            char_dir = site_dir / "guides" / cat_slug
            char_dir.mkdir(parents=True, exist_ok=True)
            char_page = char_dir / f"{char_slug}.html"
            char_page.write_text(detail_html, encoding="utf-8")
            print(f"  Character: {char_page}")

        for atype in get_anime_item_types(data):
            items = data.get(atype["key"], [])
            if not items:
                continue
            index_html = render_anime_category_index(data, atype, items)
            idx_dir = site_dir / "guides" / atype["slug"]
            idx_dir.mkdir(parents=True, exist_ok=True)
            idx_page = idx_dir / "index.html"
            idx_page.write_text(index_html, encoding="utf-8")
            print(f"  {atype['name']} Index: {idx_page}")

            for item in items:
                detail_html = render_anime_item_detail(data, item, atype)
                item_slug = slugify(item["name"])
                item_dir = site_dir / "guides" / atype["slug"]
                item_dir.mkdir(parents=True, exist_ok=True)
                item_page = item_dir / f"{item_slug}.html"
                item_page.write_text(detail_html, encoding="utf-8")
                print(f"  {atype['singular']}: {item_page}")

        search_index = generate_search_index(data)
        idx_path = site_dir / "search-index.json"
        idx_path.write_text(json.dumps(search_index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"  Search index: {idx_path} ({len(search_index)} entries)")

        generate_robots_txt(data, site_dir)
        print(f"  robots.txt: {site_dir / 'robots.txt'}")

        generate_sitemap_xml(data, site_dir, key)
        print(f"  sitemap.xml: {site_dir / 'sitemap.xml'}")
        generate_sitemap_html(data, site_dir, key)

        generate_about_contact(data, site_dir)
        print(f"  about.html + contact.html")

    print(f"\nDone. Rendered {len(keys)} site(s).")


if __name__ == "__main__":
    main()
