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
AD_SLOTS = {
    "leaderboard": "9112825459",
    "halfpage": "4397738132",
    "billboard": "9739511410",
}

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
            cats.append({
                "name": atype["name"],
                "slug": atype["slug"],
                "color": data.get("accent", "#888"),
                "character_img": "",
                "count": str(len(data[atype["key"]])) + "+",
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
Sitemap: https://{domain}/sitemap.xml
"""
    (site_dir / "robots.txt").write_text(body.strip() + "\n", encoding="utf-8")


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


def schema_org_person(data, char):
    domain = data.get("domain", "example.com")
    url = resolve_char_detail_url(data, char)
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "{char['name']}",
  "description": "{char.get('desc', char.get('role', ''))}",
  "url": "https://{domain}{url}",
  "image": "https://{domain}/images/{char.get('image', '')}",
  "jobTitle": "{char.get('role', '')}",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "https://{domain}{url}"
  }}
}}
</script>'''


def schema_org_creative_work(data, char):
    domain = data.get("domain", "example.com")
    url = resolve_char_detail_url(data, char)
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{char['name']} Guide — {data['site_name']}",
  "description": "In-depth guide for {char['name']} — {char.get('desc', '')}",
  "url": "https://{domain}{url}",
  "about": {{
    "@type": "Person",
    "name": "{char['name']}",
    "description": "{char.get('role', '')}"
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
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "CreativeWork",
  "name": "{item['name']} — {data['site_name']}",
  "description": "{item.get('desc', '')[:200]}",
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
{schema_markup}
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{theme:{{extend:{{colors:{{bgPrimary:'{bgPrimary}',bgSecondary:'{bgSecondary}',bgCard:'{bgCard}',textPrimary:'{textPrimary}',textSecondary:'{textSecondary}',accent:'{accent}',accentDark:'{accent_dark}'}},fontFamily:{{sans:['Inter','Arial','sans-serif']}}}}}}}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_pub}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{ga_id}');</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',Arial,sans-serif;background:{bodyBg};color:{textPrimary};font-size:16px;line-height:1.6}}
ins.adsbygoogle{{display:block}}
.ad-label{{text-align:center;color:#9ca3af;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:4px 0}}
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

<!-- Ad: 728x90 -->
<div class="max-w-[728px] mx-auto px-4 mt-10"><div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px" data-ad-client="{adsense_pub}" data-ad-slot="{ad_leaderboard}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div>

{guide_section}
{hot_topics_section}
{character_section}

<!-- Ad: 970x250 -->
<div class="max-w-[970px] mx-auto px-4"><div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:inline-block;width:970px;height:250px" data-ad-client="{adsense_pub}" data-ad-slot="{ad_billboard}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div>

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
<ul class="space-y-2 text-sm text-textSecondary">
{footer_links}
</ul>
</div>
<div>
<h4 class="font-bold mb-4">About</h4>
<ul class="space-y-2 text-sm text-textSecondary">
<li><a href="/about.html" class="hover:text-accent transition-colors">About</a></li>
<li><a href="/contact.html" class="hover:text-accent transition-colors">Contact</a></li>
<li><a href="/sitemap.xml" class="hover:text-accent transition-colors">Sitemap</a></li>
</ul>
</div>
</div>
<div class="max-w-7xl mx-auto mt-12 pt-6 border-t text-center text-sm text-textSecondary" style="border-color:#{footerBorderHex}">
<p>&copy; 2026 {site_name} by <a href="https://www.jycsd.com" class="text-accent hover:underline">Myers Media</a>. {copyright_note}</p>
</div>
</footer>

<script>
(function(){{
var slides=document.querySelectorAll('.carousel-slide');
var dots=document.querySelectorAll('.carousel-dot');
var current=0;
function goTo(idx){{if(!slides.length)return;slides[current].classList.remove('active');dots[current].classList.remove('active');current=idx;slides[current].classList.add('active');dots[current].classList.add('active')}}
dots.forEach(function(dot){{dot.addEventListener('click',function(){{goTo(parseInt(this.dataset.slide))}})}});
if(slides.length>1)setInterval(function(){{goTo((current+1)%slides.length)}},5000);
document.getElementById('menuBtn').addEventListener('click',function(){{document.getElementById('mobileMenu').classList.toggle('hidden')}});
{search_js}
}})();
</script>
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
if(si){si.addEventListener('input',function(){{filter(this.value,dd)}});si.addEventListener('keydown',function(e){{if(e.key==='ArrowDown'){e.preventDefault();navigate(dd,1)}else if(e.key==='ArrowUp'){e.preventDefault();navigate(dd,-1)}else if(e.key==='Enter'){e.preventDefault();selectFocused(dd)}else if(e.key==='Escape'){dd.classList.remove('active')}}});si.addEventListener('focus',function(){{if(this.value.length>=2)filter(this.value,dd)}});si.addEventListener('blur',function(){{setTimeout(function(){{dd.classList.remove('active')}},200)}})}
if(sim){sim.addEventListener('input',function(){{filter(this.value,ddm)}});sim.addEventListener('keydown',function(e){{if(e.key==='ArrowDown'){e.preventDefault();navigate(ddm,1)}else if(e.key==='ArrowUp'){e.preventDefault();navigate(ddm,-1)}else if(e.key==='Enter'){e.preventDefault();selectFocused(ddm)}else if(e.key==='Escape'){ddm.classList.remove('active')}}});sim.addEventListener('focus',function(){{if(this.value.length>=2)filter(this.value,ddm)}});sim.addEventListener('blur',function(){{setTimeout(function(){{ddm.classList.remove('active')}},200)}})}
loadIdx();
})();
'''


def render_nav_logo(data):
    img = data["categories"][0].get("character_img", "")
    if img:
        return f'<img src="/images/{img}" alt="{data["site_name"]}" class="w-10 h-10 object-cover rounded-lg">'
    first_char = data["site_name"][0]
    return f'<div class="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-accentDark flex items-center justify-center text-lg font-black text-white">{first_char}</div>'


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
        btn1_slug = cats[0]["slug"]
        btn2_slug = cats[1]["slug"] if len(cats) > 1 else cats[0]["slug"]
        slide = f'''<div class="carousel-slide active">
<div class="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-950 to-gray-900"></div>
<div class="relative max-w-7xl mx-auto px-4 h-full flex items-center">
<div class="pt-10">
<h1 class="text-4xl md:text-6xl font-black mb-4">{hero_title}</h1>
<p class="text-lg text-textSecondary mb-6 max-w-lg">{hero_subtitle}</p>
<div class="flex gap-3">
<a href="/guides/{btn1_slug}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">Browse {cats[0]["name"]}</a>
<a href="/guides/{btn2_slug}/" class="border border-textSecondary/30 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">Explore {cats[1]["name"] if len(cats)>1 else cats[0]["name"]}</a>
</div>
</div></div></div>'''
        return slide, ''

    count = min(len(chars), 8)
    if count < 5:
        count = len(chars)
    selected = chars[:count]
    slides = []
    dots = []

    labels = ["Featured", "Trending Now", "Deep Dive", "Essential", "Popular", "Hot Pick", "Must Read", "Top Guide"]

    for i, char in enumerate(selected):
        active = " active" if i == 0 else ""
        btn_a_slug = cats[i % len(cats)]["slug"]
        btn_a_name = cats[i % len(cats)]["name"]
        btn_b_slug = cats[(i + 1) % len(cats)]["slug"]
        btn_b_name = cats[(i + 1) % len(cats)]["name"]

        if btn_a_slug == btn_b_slug:
            btn_b_slug = cats[(i + 2) % len(cats)]["slug"]
            btn_b_name = cats[(i + 2) % len(cats)]["name"]

        label = labels[i % len(labels)]
        slide_title = hero_title if i == 0 else f"{char['name']} Guide"
        slide_desc = hero_subtitle if i == 0 else char.get("desc", "")
        heading_tag = "1" if i == 0 else "2"
        heading_class = "text-4xl md:text-5xl" if i == 0 else "text-3xl md:text-4xl"

        rad_x = 30 + (i * 7) % 40
        char_color = char.get("color", accent)
        char_detail_url = resolve_char_detail_url(data, char)

        slides.append(f'''<div class="carousel-slide{active}">
<div class="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-950 to-gray-900"></div>
<div class="absolute inset-0 opacity-25" style="background:radial-gradient(ellipse at {rad_x}% 50%, {char_color}, transparent 60%);"></div>
<div class="relative max-w-7xl mx-auto px-4 h-full flex items-center">
<div class="grid md:grid-cols-2 gap-8 items-center w-full">
<div class="pt-10">
<span class="inline-block text-xs font-bold uppercase tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full mb-4">{label}</span>
<h{heading_tag} class="{heading_class} font-black leading-tight mb-4">{slide_title}</h{heading_tag}>
<p class="text-lg text-textSecondary mb-6 max-w-lg">{slide_desc}</p>
<div class="flex gap-3">
<a href="/guides/{btn_a_slug}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">{btn_a_name} Guides</a>
<a href="/guides/{btn_b_slug}/" class="border border-textSecondary/30 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">{btn_b_name} Guides</a>
</div>
</div>
<div class="hidden md:flex justify-center items-end">
<a href="{char_detail_url}" class="block"><img src="/images/{char["image"]}" alt="{char["name"]} — {char.get("role", "")}" title="{char["name"]} — {char.get("role", "")}" class="char-img float-anim h-[450px] max-h-[450px] w-auto object-contain cursor-pointer hover:scale-105 transition-transform"{' style="animation-delay:0.5s"' if i>0 else ""} loading="eager"></a>
</div>
</div></div></div>''')
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
        image_html = f'<img src="/images/{cat_img}" alt="{cat_name} — category overview" title="{cat_name} category" class="char-img h-[380px] max-h-[380px] w-auto object-contain" loading="lazy">'

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
        img_html = (f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]} category" class="w-full h-full object-cover char-img group-hover:scale-110 transition-transform" loading="lazy">'
                    if cat.get("character_img") else
                    f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-3xl" style="color:{cat.get("color", data["accent"])}">&#9670;</div>')
        cards.append(f'''<a href="/guides/{cat["slug"]}/" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex items-center p-5 gap-5" style="border-color:#{border_hex}">
<div class="w-24 h-24 md:w-28 md:h-28 flex-shrink-0 flex items-center justify-center bg-bgPrimary rounded-xl overflow-hidden">{img_html}</div>
<div class="flex-1 min-w-0">
<div class="font-bold text-lg md:text-xl">{cat["name"]}</div>
<div class="text-sm text-textSecondary mt-1">{cat["count"]} guides</div>
</div>
</a>''')
    return '\n'.join(cards)


def render_guide_section(data):
    cards_data = data.get("guide_cards", [])
    if not cards_data:
        return ""
    cards = []
    border_hex = theme_colors(data)["borderHex"]
    for g in cards_data:
        img_tag = (f'<img src="/images/{g["image"]}" alt="{g["title"]}" title="{g["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" loading="lazy">'
                   if g.get("image") else
                   f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-3xl">&#128214;</div>')
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
        img_html = (f'<img src="/images/{t["image"]}" alt="{t["title"]}" title="{t["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" loading="lazy">'
                    if t.get("image") else
                    f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-3xl">&#128293;</div>')
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
<div class="grid lg:grid-cols-3 gap-8">
<div class="lg:col-span-2"><div class="space-y-3">{"".join(items)}</div></div>
<div class="hidden lg:block"><div class="sticky top-24"><ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px" data-ad-client="{ADSENSE_PUB}" data-ad-slot="{AD_SLOTS["halfpage"]}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div></div>
</div></section>'''


def render_character_section(data):
    chars = data.get("characters", [])
    if not chars:
        return ""
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for c in chars:
        detail_url = resolve_char_detail_url(data, c)
        img = (f'<img src="/images/{c["image"]}" alt="{c["name"]} — {c.get("role", "")}" title="{c["name"]} — {c.get("role", "")}" class="w-full h-full object-cover" loading="lazy">'
               if c.get("image") else
               f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl" style="color:{c.get("color", data["accent"])}">&#9733;</div>')
        items.append(f'''<div class="card-hover bg-bgCard rounded-xl overflow-hidden border text-center p-6" style="border-color:#{border_hex}">
<a href="{detail_url}" class="block mb-3"><div class="w-36 h-36 mx-auto rounded-xl overflow-hidden bg-bgPrimary flex items-center justify-center">{img}</div></a>
<h3 class="font-bold text-lg">{c["name"]}</h3>
<p class="text-xs text-textSecondary mt-1">{c.get("desc", c.get("role", ""))}</p>
<a href="{detail_url}" class="text-accent text-xs font-semibold mt-3 inline-block hover:underline">{c["name"]} Guides</a>
</div>''')
    cols = min(len(chars), 4)
    first_cat = data["categories"][0]["slug"]
    return f'''<section class="max-w-7xl mx-auto px-4 py-16">
<div class="flex items-end justify-between mb-8">
<div><p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Character Spotlight</p><h2 class="text-3xl font-black">Meet the <span class="text-accent">Characters</span></h2></div>
<a href="/guides/{first_cat}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All &rarr;</a>
</div>
<div class="grid grid-cols-2 md:grid-cols-{cols} gap-5">
{"".join(items)}
</div></section>'''


def render_category_index(data):
    cats = data["categories"]
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for cat in cats:
        img_html = (f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]}" class="w-full h-full object-cover" loading="lazy">'
                    if cat.get("character_img") else
                    f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl" style="color:{cat.get("color", data["accent"])}">&#9670;</div>')
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
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
{"".join(items)}
</div></section>'''


def render_footer(data):
    all_cats = get_all_categories(data)
    cats = '\n'.join(
        f'<li><a href="/guides/{c["slug"]}/" class="hover:text-accent transition-colors">{c["name"]}</a></li>'
        for c in all_cats[:5]
    )
    f_links = data.get("footer_links", [])
    if not f_links:
        f_links = [{"text": c["name"], "url": f'/guides/{c["slug"]}/'} for c in all_cats[:4]]
    links = '\n'.join(
        f'<li><a href="{l["url"]}" class="hover:text-accent transition-colors">{l["text"]}</a></li>'
        for l in f_links
    )
    links_title = "More Anime Wikis" if data.get("site_type") == "anime" else "More Game Guides"
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
        img_html = f'<img src="/images/{char["image"]}" alt="{char["name"]} — {char.get("role", "")}" title="{char["name"]} — {char.get("role", "")}" class="char-img w-full max-h-[500px] w-auto object-contain" loading="eager">'

    role_html = ""
    if char.get("role"):
        role_html = f'<span class="inline-block text-sm font-bold px-3 py-1 rounded-full mt-3" style="color:{char_color};background:{char_color}1a">{char["role"]}</span>'

    facts_html = ""
    char_facts = char.get("facts", {})
    if char_facts:
        facts_rows = "".join(
            f'<div class="flex justify-between py-2 border-b" style="border-color:#{tc["borderHex"]}"><span class="text-textSecondary font-medium">{k}</span><span>{v}</span></div>'
            for k, v in char_facts.items()
        )
        facts_html = f'<div class="bg-bgSecondary rounded-xl p-6 mt-8"><h3 class="font-bold text-lg mb-3">Quick Facts</h3>{facts_rows}</div>'

    related_html = _render_related_characters(data, char)

    schema = schema_org_person(data, char)

    char_detail_html = f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="grid lg:grid-cols-5 gap-10">
<div class="lg:col-span-2">
<div class="bg-bgPrimary rounded-2xl border p-8 flex items-center justify-center" style="border-color:#{tc["borderHex"]};min-height:400px">
{img_html}
</div>
</div>
<div class="lg:col-span-3">
{breadcrumb_html}
<h1 class="text-4xl md:text-5xl font-black mb-2">{char["name"]}</h1>
{role_html}
<p class="text-lg text-textSecondary mt-6 leading-relaxed">{char.get("desc", "")}</p>
<p class="text-textSecondary mt-4">Category: <a href="/guides/{cat_slug}/" class="text-accent hover:underline">{cat_name}</a></p>
{facts_html}
<div class="flex gap-3 mt-8">
<a href="/guides/{cat_slug}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">All {cat_name} Guides</a>
<a href="/" class="border border-textSecondary/30 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">Back to Home</a>
</div>
</div>
</div>
{related_html}
</section>'''

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
        ad_leaderboard=AD_SLOTS["leaderboard"],
        ad_halfpage=AD_SLOTS["halfpage"],
        ad_billboard=AD_SLOTS["billboard"],
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
    related = others[:4]

    items = []
    border_hex = theme_colors(data)["borderHex"]
    for c in related:
        detail_url = resolve_char_detail_url(data, c)
        img = (f'<img src="/images/{c["image"]}" alt="{c["name"]} — {c.get("role", "")}" title="{c["name"]}" class="w-full h-full object-cover" loading="lazy">'
               if c.get("image") else
               f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl" style="color:{c.get("color", data["accent"])}">&#9733;</div>')
        items.append(f'''<a href="{detail_url}" class="card-hover bg-bgCard rounded-xl overflow-hidden border text-center p-5" style="border-color:#{border_hex}">
<div class="w-28 h-28 mx-auto rounded-xl overflow-hidden bg-bgPrimary flex items-center justify-center mb-3">{img}</div>
<h4 class="font-bold text-base">{c["name"]}</h4>
<p class="text-xs text-textSecondary mt-1">{c.get("role", "")}</p>
</a>''')

    return f'''<div class="max-w-7xl mx-auto px-4 pb-12">
<div class="border-t pt-10" style="border-color:#{theme_colors(data)["borderHex"]}">
<h2 class="text-2xl font-black mb-6">Related Characters</h2>
<div class="grid grid-cols-2 sm:grid-cols-4 gap-5">
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
    cat_color = category.get("color", accent)
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

    hero = render_category_hero(data, category)

    filtered_guides = [g for g in data.get("guide_cards", []) if g.get("category", "").lower() == cat_name.lower()]
    guide_html = ""
    if filtered_guides:
        guide_html = _render_filtered_guides(data, filtered_guides, cat_name)

    char_html = ""
    chars = data.get("characters", [])
    if chars:
        filtered_chars = [c for c in chars if get_char_category_slug(data, c) == cat_slug]
        if filtered_chars:
            char_html = _render_full_characters_grid(data, filtered_chars, cat_name)

    hot_html = ""
    filtered_hot = [t for t in data.get("hot_topics", []) if cat_slug in t.get("link", "")]
    if filtered_hot:
        hot_html = _render_filtered_hot_topics(data, filtered_hot, cat_name)

    cats_html = ""
    other_cats = [c for c in data["categories"] if c["slug"] != cat_slug]
    if other_cats:
        cats_html = _render_other_categories(data, other_cats)

    ad_leaderboard = AD_SLOTS["leaderboard"]
    ad_halfpage = AD_SLOTS["halfpage"]
    ad_billboard = AD_SLOTS["billboard"]

    cats_section = render_category_cards(data)

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
        ad_leaderboard=ad_leaderboard,
        ad_halfpage=ad_halfpage,
        ad_billboard=ad_billboard,
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section=hero,
        breadcrumb_html="",
        category_cards_section=cats_section,
        guide_section=guide_html,
        hot_topics_section=f'{hot_html}<div class="max-w-7xl mx-auto px-4"><div class="hidden lg:block"><ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px" data-ad-client="{ADSENSE_PUB}" data-ad-slot="{AD_SLOTS["halfpage"]}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div></div>' if hot_html else "",
        character_section=char_html,
        category_index_section=cats_html,
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
        img_tag = (f'<img src="/images/{g["image"]}" alt="{g["title"]}" title="{g["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" loading="lazy">'
                   if g.get("image") else
                   f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-3xl">&#128214;</div>')
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
    border_hex = theme_colors(data)["borderHex"]
    for c in chars:
        detail_url = resolve_char_detail_url(data, c)
        img = (f'<img src="/images/{c["image"]}" alt="{c["name"]} — {c.get("role", "")}" title="{c["name"]}" class="w-full h-full object-cover" loading="lazy">'
               if c.get("image") else
               f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl" style="color:{c.get("color", data["accent"])}">&#9733;</div>')
        items.append(f'''<div class="card-hover bg-bgCard rounded-xl overflow-hidden border text-center p-6" style="border-color:#{border_hex}">
<a href="{detail_url}" class="block mb-3"><div class="w-36 h-36 mx-auto rounded-xl overflow-hidden bg-bgPrimary flex items-center justify-center">{img}</div></a>
<h3 class="font-bold text-lg">{c["name"]}</h3>
<p class="text-xs text-textSecondary mt-1">{c.get("desc", c.get("role", ""))}</p>
<a href="{detail_url}" class="text-accent text-xs font-semibold mt-3 inline-block hover:underline">{c["name"]} Detail</a>
</div>''')
    cols = min(5, max(3, len(chars) // 2))
    return f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="mb-8"><h2 class="text-3xl font-black">All {cat_name}</h2><p class="text-textSecondary mt-2">Complete {cat_name.lower()} roster</p></div>
<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-{cols} gap-5">{"".join(items)}</div></section>'''


def _render_filtered_hot_topics(data, topics, cat_name):
    items = []
    border_hex = theme_colors(data)["borderHex"]
    for t in topics:
        img_html = (f'<img src="/images/{t["image"]}" alt="{t["title"]}" title="{t["title"]}" class="w-full h-full object-cover char-img group-hover:scale-105 transition-transform" loading="lazy">'
                    if t.get("image") else
                    f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-3xl">&#128293;</div>')
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
        img_html = (f'<img src="/images/{cat["character_img"]}" alt="{cat["name"]} — {cat["count"]} guides" title="{cat["name"]}" class="w-full h-full object-cover" loading="lazy">'
                    if cat.get("character_img") else
                    f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl" style="color:{cat.get("color", data["accent"])}">&#9670;</div>')
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
        img_html = f'<img src="/images/{item["image"]}" alt="{item["name"]} — {atype["singular"]}" title="{item["name"]} — {atype["singular"]}" class="char-img w-full max-h-[500px] w-auto object-contain" loading="eager">'

    schema = schema_org_anime_item(data, item, atype["key"])

    item_detail_html = f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="grid lg:grid-cols-5 gap-10">
<div class="lg:col-span-2">
<div class="bg-bgPrimary rounded-2xl border p-8 flex items-center justify-center" style="border-color:#{tc["borderHex"]};min-height:400px">
{img_html}
</div>
</div>
<div class="lg:col-span-3">
{breadcrumb_html}
<span class="inline-block text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-3" style="color:{item_color};background:{item_color}1a">{atype["singular"]}</span>
<h1 class="text-4xl md:text-5xl font-black mb-2">{item["name"]}</h1>
<p class="text-lg text-textSecondary mt-6 leading-relaxed">{item.get("desc", "")}</p>
<p class="text-textSecondary mt-4">Category: <a href="/guides/{atype["slug"]}/" class="text-accent hover:underline">{atype["name"]}</a></p>
<div class="flex gap-3 mt-8">
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
        ad_leaderboard=AD_SLOTS["leaderboard"],
        ad_halfpage=AD_SLOTS["halfpage"],
        ad_billboard=AD_SLOTS["billboard"],
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
        img = (f'<img src="/images/{item["image"]}" alt="{item["name"]}" title="{item["name"]}" class="w-full h-full object-cover" loading="lazy">'
               if item.get("image") else
               f'<div class="w-full h-full rounded-xl bg-accent/10 flex items-center justify-center text-2xl">&#9670;</div>')
        grid_items.append(f'''<a href="/guides/{atype["slug"]}/{item_slug}.html" class="card-hover bg-bgCard rounded-xl overflow-hidden border group flex min-h-[120px]" style="border-color:#{border_hex}">
<div class="w-36 md:w-44 lg:w-52 flex-shrink-0 bg-bgPrimary flex items-center justify-center p-4 overflow-hidden">{img}</div>
<div class="flex-1 p-5 min-w-0 flex flex-col justify-center">
<h3 class="font-bold text-xl group-hover:text-accent transition-colors">{item["name"]}</h3>
<p class="text-sm text-textSecondary mt-1 line-clamp-2">{item.get("desc", "")}</p>
<span class="text-sm text-accent mt-2 inline-block font-semibold">View Details</span>
</div>
</a>''')

    cols = min(3, max(1, len(items) // 2))

    all_items_grid = f'''<section class="max-w-7xl mx-auto px-4 py-12">
<div class="mb-8"><h2 class="text-3xl font-black">All {atype["name"]}</h2><p class="text-textSecondary mt-2">{len(items)} {atype["singular"].lower()} guides</p></div>
<div class="grid md:grid-cols-2 lg:grid-cols-{cols} gap-5">{"".join(grid_items)}</div></section>'''

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
        ad_leaderboard=AD_SLOTS["leaderboard"],
        ad_halfpage=AD_SLOTS["halfpage"],
        ad_billboard=AD_SLOTS["billboard"],
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        mobile_nav_links=render_mobile_nav_links(data),
        site_hub_label=get_nav_label(data),
        site_hub_url=get_nav_url(data),
        hero_section=render_category_hero(data, {"name": atype["name"], "slug": atype["slug"], "color": cat_color, "character_img": items[0].get("image", "") if items else "", "count": f"{len(items)}+"}),
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
<section class="relative w-full overflow-hidden pt-16" style="height:520px">
{slides}
<div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2 z-10">
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
        ad_leaderboard=AD_SLOTS["leaderboard"],
        ad_halfpage=AD_SLOTS["halfpage"],
        ad_billboard=AD_SLOTS["billboard"],
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
        category_index_section=render_category_index(data),
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

    print(f"\nDone. Rendered {len(keys)} site(s).")


if __name__ == "__main__":
    main()
