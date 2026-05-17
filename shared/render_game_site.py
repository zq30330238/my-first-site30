"""Render a complete game guide site homepage from structured data.
Usage: py shared/render_game_site.py <game_key>
Example: py shared/render_game_site.py minecraft
         py shared/render_game_site.py --all
"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "shared" / "game_site_data.json"

GA4_ID = "G-GGNWR1X1GV"
ADSENSE_PUB = "ca-pub-XXXXXXXXXXXX"
AD_SLOTS = {
    "leaderboard": "LEADERBOARD1",
    "halfpage": "HALFPAGE",
    "billboard": "BILLBOARD2",
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site_name} — {tagline}</title>
<meta name="description" content="{hero_subtitle}">
<meta property="og:title" content="{site_name} — Game Guides & Wiki">
<meta property="og:description" content="{hero_subtitle}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://{domain}/">
<script src="https://cdn.tailwindcss.com"></script>
<script>tailwind.config={{theme:{{extend:{{colors:{{bgPrimary:'#0d1117',bgSecondary:'#161b22',bgCard:'#1a1f2e',textPrimary:'#e6edf3',textSecondary:'#8b949e',accent:'{accent}',accentDark:'{accent_dark}'}},fontFamily:{{sans:['Inter','Arial','sans-serif']}}}}}}}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={adsense_pub}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{ga_id}');</script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',Arial,sans-serif;background:#0d1117;color:#e6edf3;font-size:16px;line-height:1.6}}
ins.adsbygoogle{{display:block}}
.ad-label{{text-align:center;color:#6b7280;font-size:10px;text-transform:uppercase;letter-spacing:1px;padding:4px 0}}
.carousel-slide{{position:absolute;inset:0;opacity:0;transition:opacity .8s ease-in-out;pointer-events:none}}
.carousel-slide.active{{opacity:1;pointer-events:auto}}
.carousel-dot{{width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,.3);cursor:pointer;transition:background .3s}}
.carousel-dot.active{{background:{accent}}}
.card-hover:hover{{transform:translateY(-2px);box-shadow:0 8px 30px {accent}26;transition:all .3s ease}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-10px)}}}}
.float-anim{{animation:float 3s ease-in-out infinite}}
.char-img{{filter:drop-shadow(0 10px 30px rgba(0,0,0,.5))}}
</style>
</head>
<body>

<nav class="fixed top-0 w-full z-50 bg-bgPrimary/95 backdrop-blur-md border-b border-gray-800/50">
<div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
<a href="/" class="flex items-center gap-2.5">
{nav_logo}
<span class="text-xl font-bold tracking-tight">{nav_brand}</span>
</a>
<div class="hidden lg:flex items-center gap-6 text-sm font-medium">
<a href="https://games.jycsd.com" class="text-textSecondary hover:text-accent transition-colors">GameGuide</a>
{nav_links}
</div>
<button class="lg:hidden text-textSecondary text-2xl" id="menuBtn" aria-label="Menu">&#9776;</button>
</div>
</nav>

<!-- Hero Carousel -->
<section class="relative w-full overflow-hidden" style="height:520px">
{carousel_slides}
<div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2 z-10">
{carousel_dots}
</div>
</section>

<!-- Category Cards -->
<section class="max-w-7xl mx-auto px-4 -mt-6 relative z-20">
<div class="grid grid-cols-2 md:grid-cols-{cat_cols} gap-3">
{category_cards}
</div>
</section>

<!-- Ad: 728x90 -->
<div class="max-w-[728px] mx-auto px-4 mt-10"><div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px" data-ad-client="{adsense_pub}" data-ad-slot="{ad_leaderboard}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div>

<!-- Guide Cards -->
{guide_section}

<!-- Hot Topics + Sidebar -->
{hot_topics_section}

<!-- Ad: 970x250 -->
<div class="max-w-[970px] mx-auto px-4"><div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:inline-block;width:970px;height:250px" data-ad-client="{adsense_pub}" data-ad-slot="{ad_billboard}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div>

<!-- Character Spotlight -->
{character_section}

<!-- Category Index -->
{category_index_section}

<footer class="bg-bgSecondary border-t border-gray-800 py-16 px-4">
<div class="max-w-7xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
<div>
<div class="flex items-center gap-2.5 mb-4">
{footer_logo}
<span class="text-xl font-bold">{footer_brand}</span>
</div>
<p class="text-sm text-textSecondary leading-relaxed">Expert game guides. Part of the GameGuide Network.</p>
</div>
<div>
<h4 class="font-bold mb-4">Categories</h4>
<ul class="space-y-2 text-sm text-textSecondary">
{footer_categories}
</ul>
</div>
<div>
<h4 class="font-bold mb-4">More Game Guides</h4>
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
<div class="max-w-7xl mx-auto mt-12 pt-6 border-t border-gray-800 text-center text-sm text-textSecondary">
<p>&copy; 2026 {site_name} by <a href="https://www.jycsd.com" class="text-accent hover:underline">Myers Media</a>. All game trademarks belong to their respective owners.</p>
</div>
</footer>

<script>
(function(){{
var slides=document.querySelectorAll('.carousel-slide');
var dots=document.querySelectorAll('.carousel-dot');
var current=0;
function goTo(idx){{slides[current].classList.remove('active');dots[current].classList.remove('active');current=idx;slides[current].classList.add('active');dots[current].classList.add('active')}}
dots.forEach(function(dot){{dot.addEventListener('click',function(){{goTo(parseInt(this.dataset.slide))}})}});
setInterval(function(){{goTo((current+1)%slides.length)}},5000);
document.getElementById('menuBtn').addEventListener('click',function(){{document.getElementById('mobileMenu').classList.toggle('hidden')}});
}})();
</script>
</body>
</html>'''


def render_nav_logo(data):
    img = data["categories"][0].get("character_img", "")
    if img:
        return f'<img src="images/{img}" alt="{data["site_name"]}" class="w-9 h-9 object-contain">'
    first_char = data["site_name"][0]
    return f'<div class="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-accentDark flex items-center justify-center text-lg font-black text-white">{first_char}</div>'


def render_nav_brand(data):
    name = data["site_name"]
    return f'{name[:-5]}<span class="text-accent">{name[-5:]}</span>' if name.endswith("Guide") else f'{name.split()[0]} <span class="text-accent">{name.split()[1] if len(name.split())>1 else ""}</span>'


def render_nav_links(data):
    links = []
    for cat in data["categories"]:
        links.append(f'<a href="/guides/{cat["slug"]}/" class="text-textSecondary hover:text-accent transition-colors">{cat["name"]}</a>')
    return '\n'.join(links)


def render_carousel(data):
    chars = data.get("characters", [])
    if not chars:
        return '<div class="carousel-slide active"><div class="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-950 to-gray-900"></div><div class="relative max-w-7xl mx-auto px-4 h-full flex items-center"><div class="pt-10"><h1 class="text-4xl md:text-6xl font-black mb-4">{hero_title}</h1><p class="text-lg text-textSecondary mb-6 max-w-lg">{hero_subtitle}</p><div class="flex gap-3">{hero_buttons}</div></div></div></div>'.format(
            hero_title=data["hero_title"], hero_subtitle=data["hero_subtitle"],
            hero_buttons=f'<a href="/guides/{data["categories"][0]["slug"]}/" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">Browse Guides</a><a href="#" class="border border-gray-600 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">Learn More</a>'
        ), ""

    slides = []
    dots = []
    for i, char in enumerate(chars[:3]):
        active = " active" if i == 0 else ""
        bg_shade = "emerald" if data["accent"] == "#4ade80" else "purple" if data["accent"] == "#a78bfa" else "slate"
        slides.append(f'''<div class="carousel-slide{active}">
<div class="absolute inset-0 bg-gradient-to-br from-gray-900 via-{bg_shade}-950 to-gray-900"></div>
<div class="absolute inset-0 opacity-25" style="background:radial-gradient(ellipse at {30+i*35}% 50%, {char.get("color", data["accent"])}, transparent 60%);"></div>
<div class="relative max-w-7xl mx-auto px-4 h-full flex items-center">
<div class="grid md:grid-cols-2 gap-8 items-center w-full">
<div class="pt-10">
<span class="inline-block text-xs font-bold uppercase tracking-wider text-accent bg-accent/10 px-3 py-1 rounded-full mb-4">{"Trending Now" if i==0 else "Deep Dive" if i==1 else "Essential"}</span>
<h{"1" if i==0 else "2"} class="text-4xl md:text-5xl font-black leading-tight mb-4">{data["hero_title"] if i==0 else char["name"]+" Guide"}</h{"1" if i==0 else "2"}>
<p class="text-lg text-textSecondary mb-6 max-w-lg">{data["hero_subtitle"] if i==0 else char["desc"]}</p>
<div class="flex gap-3">
<a href="{char["link"]}" class="bg-accent text-gray-900 px-6 py-3 rounded-lg font-bold hover:opacity-90 transition-all">{char["name"]} Guides</a>
<a href="/guides/{data["categories"][0]["slug"]}/" class="border border-gray-600 px-6 py-3 rounded-lg font-medium hover:border-accent transition-all">All Guides</a>
</div>
</div>
<div class="hidden md:flex justify-center items-end">
<img src="images/{char["image"]}" alt="{char["name"]}" class="char-img float-anim h-96 w-auto object-contain"{' style="animation-delay:0.5s"' if i>0 else ""}>
</div>
</div></div></div>''')
        dots.append(f'<div class="carousel-dot{active}" data-slide="{i}"></div>')

    return '\n'.join(slides), '\n'.join(dots)


def render_category_cards(data):
    cards = []
    for cat in data["categories"]:
        img_html = f'<img src="images/{cat["character_img"]}" alt="{cat["name"]}" class="w-14 h-14 object-contain mx-auto mb-2 char-img group-hover:scale-110 transition-transform">' if cat.get("character_img") else f'<div class="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-2 text-2xl">&#9733;</div>'
        cards.append(f'<a href="/guides/{cat["slug"]}/" class="card-hover bg-bgCard rounded-xl p-4 text-center border border-gray-800 hover:border-accent/50 group">{img_html}<div class="text-xs font-semibold">{cat["name"]}</div></a>')
    return '\n'.join(cards)


def render_guide_section(data):
    cards_data = data.get("guide_cards", [])
    if not cards_data:
        return ""
    cards = []
    for g in cards_data:
        cards.append(f'''<article class="card-hover bg-bgCard rounded-xl overflow-hidden border border-gray-800">
<div class="h-44 bg-gradient-to-br {g.get("image_bg", "from-gray-900 to-gray-950")} flex items-center justify-center relative overflow-hidden">
<div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 50% 50%, {g.get("cat_color", data["accent"])}, transparent);"></div>
<img src="images/{g["image"]}" alt="{g["title"]}" class="relative h-36 w-auto object-contain char-img">
</div>
<div class="p-4">
<span class="text-xs font-semibold px-2 py-0.5 rounded" style="color:{g.get("cat_color", data["accent"])};background:{g.get("cat_color", data["accent"])}1a">{g["category"]}</span>
<h3 class="font-bold mt-2 mb-1 leading-snug"><a href="{g["link"]}" class="hover:text-accent transition-colors">{g["title"]}</a></h3>
<time class="text-xs text-textSecondary mt-3 block">{g["date"]}</time>
</div></article>''')
    cols = min(len(cards_data), 4)
    return f'''<section class="max-w-7xl mx-auto px-4 py-16">
<div class="flex items-end justify-between mb-8">
<div><p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Fresh Content</p><h2 class="text-3xl font-black">Latest Guides</h2></div>
<a href="/guides/{data["categories"][0]["slug"]}/" class="text-accent text-sm font-medium hover:underline hidden sm:block">View All</a>
</div>
<div class="grid md:grid-cols-2 lg:grid-cols-{cols} gap-5">
{''.join(cards)}
</div></section>'''


def render_hot_topics(data):
    topics = data.get("hot_topics", [])
    if not topics:
        return ""
    items = []
    for t in topics:
        img_tag = f'<img src="images/{t["image"]}" alt="{t["title"]}" class="w-14 h-14 object-contain flex-shrink-0 char-img">' if t.get("image") else ''
        items.append(f'''<a href="{t["link"]}" class="card-hover bg-bgCard rounded-xl p-5 flex gap-4 border border-gray-800 block">
{img_tag}
<div><h3 class="font-bold">{t["title"]}</h3><p class="text-sm text-textSecondary mt-1">{t["desc"]}</p><span class="text-xs text-accent mt-2 inline-block">Read Guide</span></div>
</a>''')
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<div class="grid lg:grid-cols-3 gap-8">
<div class="lg:col-span-2">
<p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Trending</p>
<h2 class="text-2xl font-black mb-6">Hot Topics This Month</h2>
<div class="space-y-3">{''.join(items)}</div>
</div>
<div class="hidden lg:block"><div class="sticky top-24"><ins class="adsbygoogle" style="display:inline-block;width:300px;height:600px" data-ad-client="{adsense_pub}" data-ad-slot="{ad_halfpage}"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}})</script></div></div>
</div></section>'''.format(adsense_pub=ADSENSE_PUB, ad_halfpage=AD_SLOTS["halfpage"])


def render_character_section(data):
    chars = data.get("characters", [])
    if not chars:
        return ""
    items = []
    for c in chars:
        items.append(f'''<div class="card-hover bg-bgCard rounded-xl overflow-hidden border border-gray-800 text-center p-6">
<img src="images/{c["image"]}" alt="{c["name"]}" class="char-img h-32 w-auto object-contain mx-auto mb-3">
<h3 class="font-bold text-lg">{c["name"]}</h3>
<p class="text-xs text-textSecondary">{c["desc"]}</p>
<a href="{c["link"]}" class="text-accent text-xs font-semibold mt-3 inline-block hover:underline">{c["name"]} Guides</a>
</div>''')
    cols = min(len(chars), 4)
    return f'''<section class="max-w-7xl mx-auto px-4 py-16">
<p class="text-accent text-sm font-semibold uppercase tracking-wider mb-1">Character Spotlight</p>
<h2 class="text-3xl font-black mb-8">Meet the <span class="text-accent">Characters</span></h2>
<div class="grid grid-cols-2 md:grid-cols-{cols} gap-5">
{''.join(items)}
</div></section>'''


def render_category_index(data):
    cats = data["categories"][:3]
    items = []
    for cat in cats:
        img_tag = f'<img src="images/{cat["character_img"]}" alt="{cat["name"]}" class="w-10 h-10 object-contain">' if cat.get("character_img") else ''
        items.append(f'''<div class="bg-bgCard rounded-xl p-6 border border-gray-800 hover:border-accent/30 transition-all">
<div class="flex items-center gap-3 mb-4">{img_tag}<h3 class="font-bold text-lg"><a href="/guides/{cat["slug"]}/" class="hover:text-accent transition-colors">{cat["name"]}</a></h3></div>
<ul class="space-y-2 text-sm text-textSecondary">
<li><a href="/guides/{cat["slug"]}/" class="hover:text-accent transition-colors">{cat["name"]} — Complete Guide</a></li>
</ul>
<a href="/guides/{cat["slug"]}/" class="text-accent text-xs font-semibold mt-3 inline-block hover:underline">{cat["count"]} guides</a>
</div>''')
    return f'''<section class="max-w-7xl mx-auto px-4 py-8">
<h2 class="text-3xl font-black mb-8">Every Guide Category</h2>
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
{''.join(items)}
</div></section>'''


def render_footer(data):
    cats = '\n'.join(f'<li><a href="/guides/{c["slug"]}/" class="hover:text-accent transition-colors">{c["name"]}</a></li>' for c in data["categories"][:4])
    links = '\n'.join(f'<li><a href="{l["url"]}" class="hover:text-accent transition-colors">{l["text"]}</a></li>' for l in data.get("footer_links", []))
    return cats, links


def render_game_site(data):
    slides, dots = render_carousel(data)
    nav_logo = render_nav_logo(data)
    nav_brand = render_nav_brand(data)
    footer_logo = nav_logo
    footer_brand = nav_brand
    footer_cats, footer_links = render_footer(data)

    return HTML_TEMPLATE.format(
        site_name=data["site_name"],
        tagline=data.get("tagline", ""),
        domain=data["domain"],
        hero_subtitle=data.get("hero_subtitle", ""),
        hero_title=data.get("hero_title", ""),
        accent=data["accent"],
        accent_dark=data.get("accent_dark", data["accent"]),
        adsense_pub=ADSENSE_PUB,
        ga_id=GA4_ID,
        ad_leaderboard=AD_SLOTS["leaderboard"],
        ad_halfpage=AD_SLOTS["halfpage"],
        ad_billboard=AD_SLOTS["billboard"],
        nav_logo=nav_logo,
        nav_brand=nav_brand,
        nav_links=render_nav_links(data),
        carousel_slides=slides,
        carousel_dots=dots,
        cat_cols=min(len(data["categories"]), 6),
        category_cards=render_category_cards(data),
        guide_section=render_guide_section(data),
        hot_topics_section=render_hot_topics(data),
        character_section=render_character_section(data),
        category_index_section=render_category_index(data),
        footer_logo=footer_logo,
        footer_brand=footer_brand,
        footer_categories=footer_cats,
        footer_links=footer_links,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: py shared/render_game_site.py <game_key> [--all]")
        print("Available games:", ", ".join(json.loads(DATA_FILE.read_text(encoding="utf-8")).keys()))
        sys.exit(1)

    all_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    if sys.argv[1] == "--all":
        keys = list(all_data.keys())
    else:
        keys = [sys.argv[1]]

    for key in keys:
        if key not in all_data:
            print(f"Unknown game: {key}")
            continue
        data = all_data[key]
        site_dir = ROOT / f"{key}-site"
        if not site_dir.exists():
            site_dir.mkdir(parents=True)

        html = render_game_site(data)
        out_path = site_dir / "index.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"  Rendered: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
