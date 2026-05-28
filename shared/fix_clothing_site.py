"""
Fix all clothing-site audit FAILs.
Usage: python shared/fix_clothing_site.py
"""
import os
import re

BASE = r"d:\AI网站文件夹\clothing-site"

CONTENT_SITES_OPTIONS = """                    <option value="">— Content Sites —</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://auto.jycsd.com">AutoPulse</option>
                    <option value="https://moto.jycsd.com">MotoPulse</option>
                    <option value="https://food.jycsd.com">FlavorFusion</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                    <option value="https://entertainment.jycsd.com">PopCulture HQ</option>"""

# The Content Sites select block - old pattern (with the 5-option Content Sites dropdown)
# We need to match the exact pattern: from <select onchange=... to </select>\n            </div>
# The key: the select starts with <select onchange="if(this.value) window.location.href=this.value"
# and has the 5 content site options, then </select>\n            </div>
OLD_CONTENT_SITES_RE = re.compile(
    r'(<h3 class="text-white font-semibold mb-3">Content Sites</h3>\s*'
    r'<select onchange="if\(this\.value\) window\.location\.href=this\.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">)'
    r'(.*?)'
    r'(</select>\s*</div>)',
    re.DOTALL
)

def fix_content_sites(filepath):
    """Replace the Content Sites dropdown with the full 12-option version."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = OLD_CONTENT_SITES_RE.sub(
        r'\1\n' + CONTENT_SITES_OPTIONS + r'\n\3',
        content
    )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def add_og_url(filepath, url):
    """Add og:url meta if missing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if f'og:url' in content:
        return False

    # Insert after <meta property="og:site_name" ...> or <meta name="twitter:card" ...>
    og_url_tag = f'    <meta property="og:url" content="{url}">'

    # Try inserting after twitter:card (which should be right before google-adsense)
    replacement = lambda m: m.group(0) + '\n' + og_url_tag
    new_content = re.sub(
        r'(<meta name="twitter:card" content="summary_large_image">)',
        replacement,
        content,
        count=1
    )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def fix_emoji(filepath):
    """Replace emoji in classic-pieces/index.html with placeholder divs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace emoji spans with text labels
    emoji_map = {
        '👖': 'Jeans',
        '👗': 'LBD',
        '👔': 'Shirt',
        '🧥': 'Coat',
        '🎩': 'Blazer',
        '👡': 'Flats',
        '🧶': 'Cashmere',
    }

    new_content = content
    for emoji, text in emoji_map.items():
        # Replace <span class="text-6xl">EMOJI</span> with a styled div
        new_content = new_content.replace(
            f'<span class="text-6xl">{emoji}</span>',
            f'<span class="text-4xl font-bold text-gray-400">{text}</span>'
        )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def fix_missing_images(filepath):
    """Replace broken ethnic group image references with Unsplash placeholders."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    unsplash = 'https://images.unsplash.com/photo-1607082349566-187342175e2f?w=400&h=400&fit=crop'

    images_to_fix = ['miao', 'tibetan', 'zhuang', 'yi', 'uyghur', 'mongolian']

    new_content = content
    for img_name in images_to_fix:
        old = f'src="/images/{img_name}.jpg"'
        new = f'src="{unsplash}"'
        new_content = new_content.replace(old, new)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def create_topics_index():
    """Create chinese/topics/index.html."""
    filepath = os.path.join(BASE, 'chinese', 'topics', 'index.html')
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    html = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chinese Traditional Clothing Topics — Myers Fashion</title>
    <meta name="description" content="Explore in-depth topics on Chinese traditional clothing — qipao history, dragon and phoenix symbolism, zhongshan suit, tang suit, and more.">
    <meta property="og:title" content="Chinese Traditional Clothing Topics — Myers Fashion">
    <meta property="og:description" content="Explore in-depth topics on Chinese traditional clothing — qipao history, dragon and phoenix symbolism, zhongshan suit, tang suit, and more.">
    <meta property="og:image" content="https://clothing.jycsd.com/images/default-og.jpg">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="en_US">
    <meta property="og:url" content="https://clothing.jycsd.com/chinese/topics/">
    <meta property="og:site_name" content="Myers Fashion">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="google-adsense-account" content="ca-pub-2595917642864488">
    <link rel="canonical" href="https://clothing.jycsd.com/chinese/topics/">
    <script src="https://cdn.tailwindcss.com"></script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin></script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-GGNWR1X1GV');
    </script>
    <style>
        :root { --accent: #c41e3a; --accent-light: #fef2f2; }
        body { font-family: 'Segoe UI', Roboto, Arial, sans-serif; }
        .accent-text { color: var(--accent); }
        .accent-bg { background-color: var(--accent); }
        .accent-border { border-color: var(--accent); }
        .hover-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
        .content h2 { color: var(--accent); margin-top: 2rem; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700; }
        .content p { margin-bottom: 1rem; line-height: 1.8; color: #374151; }
        .content blockquote { border-left: 4px solid var(--accent); background: var(--accent-light); padding: 1.25rem 1.5rem; margin: 1.5rem 0; border-radius: 0 0.5rem 0.5rem 0; font-style: italic; color: #4b5563; }
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
        <span class="text-gray-900">Special Topics</span>
    </div>
</nav>

<!-- Hero -->
<section class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white">
    <div class="max-w-7xl mx-auto px-4 py-16 md:py-20">
        <div class="max-w-3xl">
            <p class="text-sm uppercase tracking-widest text-red-300 mb-3">Chinese Clothing</p>
            <h1 class="text-3xl md:text-4xl font-bold leading-tight mb-4">Special Topics in Chinese Traditional Clothing</h1>
            <p class="text-lg text-gray-300 leading-relaxed">Deep dives into the stories, symbolism, and craftsmanship behind China's most iconic garments — from the elegant qipao to the symbolic dragon and phoenix motifs.</p>
        </div>
    </div>
</section>

<!-- Blockquote -->
<section class="bg-gray-50 py-10">
    <div class="max-w-3xl mx-auto px-4">
        <blockquote class="text-lg italic text-gray-600 leading-relaxed border-l-4 border-[#c41e3a] pl-6">
            "Every traditional Chinese garment carries a story — of dynasties risen and fallen, of cultural exchange along ancient trade routes, of artisans whose skills were passed down through generations. These are the stories behind the stitches."
        </blockquote>
    </div>
</section>

<!-- Article Cards -->
<section class="max-w-7xl mx-auto px-4 py-12">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <a href="/chinese/topics/qipao-history.html" class="bg-white border border-gray-200 rounded-xl overflow-hidden hover-card transition-all duration-200 block">
            <div class="p-6">
                <h2 class="text-xl font-bold mb-3 accent-text">The Qipao: From Manchu Roots to Global Icon</h2>
                <p class="text-gray-600 text-sm leading-relaxed mb-3">Explore the fascinating journey of the qipao (cheongsam) — from its origins as a loose-fitting Manchu dynasty garment to its glamorous Shanghai transformation in the 1920s and its enduring status as a symbol of Chinese elegance worldwide.</p>
                <span class="text-xs uppercase tracking-wider text-gray-400">Read more →</span>
            </div>
        </a>
        <a href="/chinese/topics/dragon-phoenix.html" class="bg-white border border-gray-200 rounded-xl overflow-hidden hover-card transition-all duration-200 block">
            <div class="p-6">
                <h2 class="text-xl font-bold mb-3 accent-text">Dragon and Phoenix: Symbols in Chinese Dress</h2>
                <p class="text-gray-600 text-sm leading-relaxed mb-3">The dragon and phoenix are the most powerful symbols in Chinese culture. Discover how these mythical creatures have been woven, embroidered, and painted onto imperial robes, wedding dresses, and ceremonial garments for centuries.</p>
                <span class="text-xs uppercase tracking-wider text-gray-400">Read more →</span>
            </div>
        </a>
        <a href="/chinese/topics/zhongshan-suit.html" class="bg-white border border-gray-200 rounded-xl overflow-hidden hover-card transition-all duration-200 block">
            <div class="p-6">
                <h2 class="text-xl font-bold mb-3 accent-text">The Zhongshan Suit: China's Modern Classic</h2>
                <p class="text-gray-600 text-sm leading-relaxed mb-3">Also known as the Mao suit, the Zhongshan suit represents a pivotal moment in Chinese fashion history. Learn about its design origins, political significance, and its place in modern Chinese identity.</p>
                <span class="text-xs uppercase tracking-wider text-gray-400">Read more →</span>
            </div>
        </a>
        <a href="/chinese/topics/tang-suit.html" class="bg-white border border-gray-200 rounded-xl overflow-hidden hover-card transition-all duration-200 block">
            <div class="p-6">
                <h2 class="text-xl font-bold mb-3 accent-text">The Tang Suit: Tradition Meets Modern Style</h2>
                <p class="text-gray-600 text-sm leading-relaxed mb-3">Despite its name, the Tang suit (tangzhuang) draws from Qing dynasty Manchu influences. Learn how this jacket became a symbol of Chinese cultural pride and a popular choice for formal occasions worldwide.</p>
                <span class="text-xs uppercase tracking-wider text-gray-400">Read more →</span>
            </div>
        </a>
    </div>
</section>

<!-- Footer -->
<footer class="bg-gray-900 text-gray-400 py-12">
    <div class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
                <h3 class="text-white font-bold text-lg mb-3">Myers Fashion</h3>
                <p class="text-sm leading-relaxed">Your comprehensive guide to traditional Chinese clothing and global fashion trends.</p>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Network</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
                    <option value="">— Network Sites —</option>
                    <option value="https://www.jycsd.com">Myers Media</option>
                    <option value="https://healthy.jycsd.com">Healthy Living</option>
                    <option value="https://pets.jycsd.com">Pet Care</option>
                    <option value="https://home.jycsd.com">Home & Garden</option>
                    <option value="https://finance.jycsd.com">Personal Finance</option>
                    <option value="https://tech.jycsd.com">Tech & Digital</option>
                    <option value="https://travel.jycsd.com">Travel Guide</option>
                </select>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Content Sites</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
''' + CONTENT_SITES_OPTIONS + '''                </select>
            </div>
            <div>
                <h3 class="text-white font-semibold mb-3">Game & Anime Wikis</h3>
                <select onchange="if(this.value) window.location.href=this.value" class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-gray-500">
                    <option value="">— Game & Anime —</option>
                    <option value="https://games.jycsd.com">Games Hub</option>
                    <option value="https://anime.jycsd.com">Anime Hub</option>
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

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Chinese Traditional Clothing Topics",
  "url": "https://clothing.jycsd.com/chinese/topics/",
  "description": "In-depth topics on Chinese traditional clothing including qipao history, dragon and phoenix symbolism, zhongshan suit, and tang suit",
  "publisher": { "@type": "Organization", "name": "Myers Media" }
}
</script>
</body>
</html>'''

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


def verify_all_fixes():
    """Print verification summary."""
    print("=" * 60)
    print("FIX SUMMARY")
    print("=" * 60)

    # Check og:url on index pages
    og_urls = [
        (os.path.join(BASE, 'index.html'), 'https://clothing.jycsd.com/'),
        (os.path.join(BASE, 'chinese', '56-ethnic-groups', 'index.html'), 'https://clothing.jycsd.com/chinese/56-ethnic-groups/'),
        (os.path.join(BASE, 'chinese', 'dynasty-evolution', 'index.html'), 'https://clothing.jycsd.com/chinese/dynasty-evolution/'),
        (os.path.join(BASE, 'chinese', 'index.html'), 'https://clothing.jycsd.com/chinese/'),
        (os.path.join(BASE, 'western', 'index.html'), 'https://clothing.jycsd.com/western/'),
        (os.path.join(BASE, 'western', 'fashion-week-trends', 'index.html'), 'https://clothing.jycsd.com/western/fashion-week-trends/'),
        (os.path.join(BASE, 'western', 'classic-pieces', 'index.html'), 'https://clothing.jycsd.com/western/classic-pieces/'),
        (os.path.join(BASE, 'compare', 'index.html'), 'https://clothing.jycsd.com/compare/'),
    ]

    og_missing = []
    for fp, url in og_urls:
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                c = f.read()
            if f'og:url' not in c or url not in c:
                og_missing.append((fp, url))
        else:
            og_missing.append((fp, url))

    if og_missing:
        print(f"[CHECK] og:url still missing in {len(og_missing)} files")
        for fp, url in og_missing:
            print(f"  MISSING: {os.path.relpath(fp, BASE)} -> {url}")
    else:
        print("[OK] All og:url present")

    # Check chinese/topics/index.html exists
    topics_idx = os.path.join(BASE, 'chinese', 'topics', 'index.html')
    if os.path.exists(topics_idx):
        print("[OK] chinese/topics/index.html created")
    else:
        print("[FAIL] chinese/topics/index.html NOT created")

    # Check emoji in classic-pieces
    classic_file = os.path.join(BASE, 'western', 'classic-pieces', 'index.html')
    if os.path.exists(classic_file):
        with open(classic_file, 'r', encoding='utf-8') as f:
            c = f.read()
        emojis_found = sum(1 for ch in c if ord(ch) > 0x1F600 and ord(ch) < 0x1FA00)
        if emojis_found > 0:
            print(f"[WARN] {emojis_found} emoji chars may remain in classic-pieces/index.html")
        else:
            print("[OK] No emoji in classic-pieces/index.html")

    # Check images in index files
    for idx_path in [os.path.join(BASE, 'index.html'), os.path.join(BASE, 'chinese', 'index.html')]:
        if os.path.exists(idx_path):
            with open(idx_path, 'r', encoding='utf-8') as f:
                c = f.read()
            broken = ['/images/miao.jpg', '/images/tibetan.jpg', '/images/zhuang.jpg',
                      '/images/yi.jpg', '/images/uyghur.jpg', '/images/mongolian.jpg']
            found = [b for b in broken if b in c]
            if found:
                print(f"[FAIL] {os.path.relpath(idx_path, BASE)} still has {len(found)} broken image refs: {found}")
            else:
                print(f"[OK] {os.path.relpath(idx_path, BASE)}: broken images fixed")

    # Check Content Sites dropdown has all 12 sites
    content_sites_files = [
        'about.html', 'contact.html', 'cookie-policy.html', 'privacy-policy.html', 'terms.html',
        'chinese/index.html', 'chinese/56-ethnic-groups/index.html', 'chinese/dynasty-evolution/index.html',
        'western/index.html', 'western/fashion-week-trends/index.html', 'western/classic-pieces/index.html',
        'compare/index.html',
    ]

    required_sites = ['HealthyEats', 'PetCare Hub', 'HomeJoy', 'MoneyWise', 'TechNest',
                      'TripRoute', 'AutoPulse', 'MotoPulse', 'FlavorFusion', 'RightsDaily',
                      'DailyMedAdvice', 'PopCulture HQ']

    for relp in content_sites_files:
        fp = os.path.join(BASE, relp)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8') as f:
                c = f.read()
            missing = [s for s in required_sites if s not in c]
            if missing:
                print(f"[FAIL] {relp}: missing {missing}")
            else:
                print(f"[OK] {relp}: Content Sites OK")
        else:
            print(f"[SKIP] {relp}: file not found")

    print("=" * 60)
    print("Verification complete!")


if __name__ == '__main__':
    # Fix 1: Create chinese/topics/index.html
    create_topics_index()
    print("[FIX 1/5] Created chinese/topics/index.html")

    # Fix 2: Fix Content Sites dropdown in 12 files
    content_sites_files = [
        'about.html', 'contact.html', 'cookie-policy.html', 'privacy-policy.html', 'terms.html',
        'chinese/index.html', 'chinese/56-ethnic-groups/index.html', 'chinese/dynasty-evolution/index.html',
        'western/index.html', 'western/fashion-week-trends/index.html', 'western/classic-pieces/index.html',
        'compare/index.html',
    ]

    cs_fixed = 0
    for relp in content_sites_files:
        fp = os.path.join(BASE, relp)
        if os.path.exists(fp):
            if fix_content_sites(fp):
                print(f"  Fixed: {relp}")
                cs_fixed += 1
        else:
            print(f"  SKIP: {relp} not found")
    print(f"[FIX 2/5] Fixed Content Sites dropdown in {cs_fixed} files")

    # Fix 3: Add og:url meta
    og_fixes = [
        ('index.html', 'https://clothing.jycsd.com/'),
        ('chinese/56-ethnic-groups/index.html', 'https://clothing.jycsd.com/chinese/56-ethnic-groups/'),
        ('chinese/dynasty-evolution/index.html', 'https://clothing.jycsd.com/chinese/dynasty-evolution/'),
        ('chinese/index.html', 'https://clothing.jycsd.com/chinese/'),
        ('western/index.html', 'https://clothing.jycsd.com/western/'),
        ('western/fashion-week-trends/index.html', 'https://clothing.jycsd.com/western/fashion-week-trends/'),
        ('western/classic-pieces/index.html', 'https://clothing.jycsd.com/western/classic-pieces/'),
        ('compare/index.html', 'https://clothing.jycsd.com/compare/'),
    ]

    og_fixed = 0
    for relp, url in og_fixes:
        fp = os.path.join(BASE, relp)
        if os.path.exists(fp):
            if add_og_url(fp, url):
                print(f"  Added og:url to {relp}")
                og_fixed += 1
    print(f"[FIX 3/5] Added og:url to {og_fixed} files")

    # Fix 4: Fix emoji in classic-pieces/index.html
    classic_file = os.path.join(BASE, 'western', 'classic-pieces', 'index.html')
    if os.path.exists(classic_file) and fix_emoji(classic_file):
        print("[FIX 4/5] Fixed emoji in classic-pieces/index.html")
    else:
        print("[FIX 4/5] No emoji fix needed in classic-pieces/index.html")

    # Fix 5: Fix missing images
    img_fixed = 0
    for idx_rel in ['index.html', 'chinese/index.html']:
        fp = os.path.join(BASE, idx_rel)
        if os.path.exists(fp) and fix_missing_images(fp):
            print(f"  Fixed images in {idx_rel}")
            img_fixed += 1
    print(f"[FIX 5/5] Fixed missing images in {img_fixed} files")

    print()
    verify_all_fixes()
