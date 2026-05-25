#!/usr/bin/env python3
"""Generate sub-moto (MotoPulse) site from sub-auto (AutoPulse) templates."""

import os, re, shutil

SRC = "d:/AI网站文件夹/sub-auto"
DST = "d:/AI网站文件夹/sub-moto"
os.makedirs(DST, exist_ok=True)

# Brand colors: red -> orange
COLOR_MAP = {
    '#fef2f2': '#fff7ed',
    '#fee2e2': '#ffedd5',
    '#fecaca': '#fed7aa',
    '#f87171': '#fb923c',
    '#ef4444': '#f97316',
    '#dc2626': '#ea580c',
    '#b91c1c': '#c2410c',
    '#991b1b': '#9a3412',
}

def fix_colors(text):
    for old, new in COLOR_MAP.items():
        text = text.replace(old, new)
    return text

def fix_brand_text(text):
    text = text.replace('AutoPulse', 'MotoPulse')
    text = text.replace('auto.jycsd.com', 'moto.jycsd.com')
    text = text.replace('Auto<span', 'Moto<span')
    return text

def fix_gradient_classes(text):
    """Fix gradient utility classes: red -> orange"""
    text = text.replace('from-red-50', 'from-orange-50')
    text = text.replace('to-orange-100', 'to-amber-50')
    text = text.replace('bg-red-50', 'bg-orange-50')
    text = text.replace('bg-red-100', 'bg-orange-100')
    text = text.replace('bg-red-200', 'bg-orange-200')
    text = text.replace('via-red-800', 'via-orange-800')
    text = text.replace('to-red-700', 'to-orange-700')
    text = text.replace('via-red-600', 'via-orange-600')
    text = text.replace('to-red-600', 'to-orange-600')
    text = text.replace('from-red-100', 'from-orange-100')
    text = text.replace('via-red-500', 'via-orange-500')
    return text

def fix_og_text(text):
    """Fix OG tags and meta descriptions for motorcycle context"""
    text = text.replace(
        'car reviews, EV &amp; hybrid coverage, buying guides, and performance insights',
        'motorcycle reviews, EV bike coverage, buying guides, and motorsport insights'
    )
    text = text.replace(
        'car reviews, EV & hybrid coverage, buying guides, and performance insights',
        'motorcycle reviews, EV bike coverage, buying guides, and motorsport insights'
    )
    return text

def fix_description_meta(text):
    """Update meta descriptions"""
    text = text.replace(
        'AutoPulse delivers honest car reviews, EV & hybrid coverage, buying guides, and performance insights. Your pulse on the automotive world.',
        'MotoPulse delivers honest motorcycle reviews, EV bike coverage, buying guides, and motorsport insights.'
    )
    text = text.replace(
        'Your pulse on the automotive world. Honest reviews, EV coverage, and buying guides.',
        'Your pulse on the motorcycle world. Honest reviews, EV coverage, and riding guides.'
    )
    text = text.replace(
        'AutoPulse — Car Reviews, EV Guides & Automotive Insights',
        'MotoPulse — Motorcycle Reviews, EV Bikes & Riding Guides'
    )
    return text

def fix_card_arrows(text):
    """Fix arrow button colors"""
    text = text.replace('bg-brand-700 hover:bg-brand-800 text-white font-semibold px-8 py-3 rounded-full',
                        'bg-brand-600 hover:bg-brand-700 text-white font-semibold px-8 py-3 rounded-full')
    return text

def fix_nav_auto(text):
    """Fix nav: AutoPulse-specific navigation items"""
    # In the dark nav (index/articles), replace "EV & Hybrid" with "EV Bikes"
    text = text.replace('EV &amp; Hybrid', 'EV Bikes')
    # In white nav (other pages), same
    text = text.replace('EV &amp; Hybrid', 'EV Bikes')
    # Performance -> Sport & Racing
    text = text.replace('Performance', 'Sport &amp; Racing')
    # category-performance.html -> category-sport.html
    text = text.replace('category-performance.html', 'category-sport.html')
    return text

def process_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    content = fix_brand_text(content)
    content = fix_colors(content)
    content = fix_gradient_classes(content)
    content = fix_og_text(content)
    content = fix_description_meta(content)
    content = fix_card_arrows(content)
    content = fix_nav_auto(content)

    # Fix carousel dot active color
    content = content.replace('.carousel-dot.active{background:#dc2626}', '.carousel-dot.active{background:#f97316}')
    content = content.replace('.carousel-dot.active{background:#ea580c}', '.carousel-dot.active{background:#f97316}')

    # Fix footer description
    content = content.replace(
        'In-depth car reviews, EV &amp; hybrid coverage, buying guides, and performance insights.',
        'In-depth motorcycle reviews, EV bike coverage, buying guides, and motorsport insights.'
    )

    return content

# ============================================================
# 1. index.html - Special handling with rebuilt carousel
# ============================================================
print("Creating index.html...")
with open(f"{SRC}/index.html", 'r', encoding='utf-8') as f:
    index_html = f.read()

# Build new carousel slides for motorcycle site
new_slides = '''    <div class="carousel-slide active">
    <div class="absolute inset-0 bg-gray-950"></div>
    <img src="images/banner/banner-1.jpg" alt="Motorcycle Reviews" class="absolute inset-0 w-full h-full object-cover" loading="eager">
    <div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
    <div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-6xl mx-auto px-6">
    <h2 class="text-4xl md:text-5xl font-black text-white mb-2" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Expert Motorcycle Reviews</h2>
    <p class="text-lg text-gray-300 max-w-xl" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Honest, data-driven bike reviews from real riders</p>
    <a href="category-reviews.html" class="inline-block mt-4 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-all">Browse Reviews</a>
    </div>
    </div>
    <div class="carousel-slide">
    <div class="absolute inset-0 bg-gray-950"></div>
    <img src="images/banner/banner-2.jpg" alt="Electric Motorcycles" class="absolute inset-0 w-full h-full object-cover" loading="lazy">
    <div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
    <div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-6xl mx-auto px-6">
    <h2 class="text-4xl md:text-5xl font-black text-white mb-2" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">The Electric Revolution</h2>
    <p class="text-lg text-gray-300 max-w-xl" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Electric motorcycle coverage for real riders</p>
    <a href="category-ev.html" class="inline-block mt-4 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-all">Explore EVs</a>
    </div>
    </div>
    <div class="carousel-slide">
    <div class="absolute inset-0 bg-gray-950"></div>
    <img src="images/banner/banner-3.jpg" alt="Buying Guides" class="absolute inset-0 w-full h-full object-cover" loading="lazy">
    <div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
    <div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-6xl mx-auto px-6">
    <h2 class="text-4xl md:text-5xl font-black text-white mb-2" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Ride Smarter</h2>
    <p class="text-lg text-gray-300 max-w-xl" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Expert buying guides to save you thousands</p>
    <a href="category-buying.html" class="inline-block mt-4 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-all">Buying Guides</a>
    </div>
    </div>
    <div class="carousel-slide">
    <div class="absolute inset-0 bg-gray-950"></div>
    <img src="images/banner/banner-4.jpg" alt="Sport & Racing" class="absolute inset-0 w-full h-full object-cover" loading="lazy">
    <div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
    <div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-6xl mx-auto px-6">
    <h2 class="text-4xl md:text-5xl font-black text-white mb-2" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Racing & Track Days</h2>
    <p class="text-lg text-gray-300 max-w-xl" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">From MotoGP to your first track day</p>
    <a href="category-sport.html" class="inline-block mt-4 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-all">Sport &amp; Racing</a>
    </div>
    </div>
    <div class="carousel-slide">
    <div class="absolute inset-0 bg-gray-950"></div>
    <img src="images/banner/banner-5.jpg" alt="Chinese Motorcycle Brands" class="absolute inset-0 w-full h-full object-cover" loading="lazy">
    <div class="absolute inset-0" style="pointer-events:none;background:linear-gradient(to top,rgba(0,0,0,.85) 0%,rgba(0,0,0,.3) 50%,transparent 80%)"></div>
    <div class="absolute bottom-16 md:bottom-20 left-0 right-0 z-10 max-w-6xl mx-auto px-6">
    <h2 class="text-4xl md:text-5xl font-black text-white mb-2" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">Chinese Brands Rising</h2>
    <p class="text-lg text-gray-300 max-w-xl" style="text-shadow:0 2px 8px rgba(0,0,0,0.6)">CFMoto, Zongshen, and the new global players</p>
    <a href="category-chinese-brands.html" class="inline-block mt-4 bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-all">Chinese Brands</a>
    </div>
    </div>'''

# Extract old slides region (from first carousel-slide to the closing </section> of carousel)
import re as regex
old_carousel_match = regex.search(
    r'<div class="carousel-slide active">.*?</div>\s*</section>',
    index_html, regex.DOTALL
)
if old_carousel_match:
    # Find where the carousel section starts
    start_marker = '<div class="carousel-slide active">'
    end_marker = '</section>'
    start_pos = index_html.find(start_marker)
    # Find the </section> that ends the carousel by counting sections
    count = 0
    end_pos = start_pos
    for i, ch in enumerate(index_html[start_pos:], start_pos):
        if index_html[start_pos:].startswith('<section'):
            count += 1
        if ch == '>':
            pass
    # Simpler approach: just find the first </section> after the slides
    # The carousel section starts with <section class="relative w-full h-[70vh]...
    carousel_start = index_html.find('<section class="relative w-full h-[70vh]')
    # Find which </section> closes this
    section_count = 1
    pos = carousel_start
    while section_count > 0 and pos < len(index_html):
        pos += 1
        next_open = index_html.find('<section', pos)
        next_close = index_html.find('</section>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            section_count += 1
            pos = next_open + 8
        else:
            section_count -= 1
            pos = next_close + 10
            carousel_end = pos - 10

    # Replace everything from carousel start to carousel end
    old_carousel = index_html[carousel_start:carousel_end]

    new_carousel = '''<section class="relative w-full h-[70vh] overflow-hidden carousel">
''' + new_slides + '''
    <button id="carouselPrev" class="carousel-arrow left-4" aria-label="Previous slide">&#10094;</button>
    <button id="carouselNext" class="carousel-arrow right-4" aria-label="Next slide">&#10095;</button>
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3 z-10">
    <div class="carousel-dot active" data-slide="0"></div>
    <div class="carousel-dot" data-slide="1"></div>
    <div class="carousel-dot" data-slide="2"></div>
    <div class="carousel-dot" data-slide="3"></div>
    <div class="carousel-dot" data-slide="4"></div>
    </div>
    </section>'''

    index_html = index_html.replace(old_carousel, new_carousel)

# Replace the Trending Now section with motorcycle-themed content
trending_start = index_html.find('<section class="max-w-6xl mx-auto px-4 py-8">')
trending_end = index_html.find('</section>', trending_start) + len('</section>')

motorcycle_trending = '''<section class="max-w-6xl mx-auto px-4 py-8">
        <h2 class="text-2xl font-black text-gray-900 mb-6">Trending Now</h2>
        <div class="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory -mx-4 px-4">
            <a href="category-reviews.html" class="flex-none w-72 snap-start block">
                <div class="bg-cover bg-center rounded-xl h-44 flex items-end p-5 relative" style="background-image:url(images/article-1.jpg)">
                    <div class="absolute inset-0 bg-black/50 rounded-xl"></div>
                    <div class="relative z-10">
                        <span class="text-xs font-semibold bg-brand-50 text-brand-700 px-3 py-1 rounded-full mb-2 inline-block">Reviews</span>
                        <h3 class="text-white font-bold text-sm leading-snug">2026 Kawasaki Ninja ZX-6R Review: The Middleweight King Returns</h3>
                        <p class="text-gray-400 text-xs mt-2">May 22, 2026</p>
                    </div>
                </div>
            </a>
            <a href="category-ev.html" class="flex-none w-72 snap-start block">
                <div class="bg-cover bg-center rounded-xl h-44 flex items-end p-5 relative" style="background-image:url(images/article-2.jpg)">
                    <div class="absolute inset-0 bg-black/50 rounded-xl"></div>
                    <div class="relative z-10">
                        <span class="text-xs font-semibold bg-brand-50 text-brand-700 px-3 py-1 rounded-full mb-2 inline-block">EV</span>
                        <h3 class="text-white font-bold text-sm leading-snug">Livewire S2 Mulholland Review: Harley's Electric Future</h3>
                        <p class="text-gray-400 text-xs mt-2">May 20, 2026</p>
                    </div>
                </div>
            </a>
            <a href="category-buying.html" class="flex-none w-72 snap-start block">
                <div class="bg-cover bg-center rounded-xl h-44 flex items-end p-5 relative" style="background-image:url(images/article-3.jpg)">
                    <div class="absolute inset-0 bg-black/50 rounded-xl"></div>
                    <div class="relative z-10">
                        <span class="text-xs font-semibold bg-brand-50 text-brand-700 px-3 py-1 rounded-full mb-2 inline-block">Buying</span>
                        <h3 class="text-white font-bold text-sm leading-snug">Best Beginner Motorcycles in 2026: From 300cc to 650cc</h3>
                        <p class="text-gray-400 text-xs mt-2">May 18, 2026</p>
                    </div>
                </div>
            </a>
            <a href="category-chinese-brands.html" class="flex-none w-72 snap-start block">
                <div class="bg-cover bg-center rounded-xl h-44 flex items-end p-5 relative" style="background-image:url(images/article-4.jpg)">
                    <div class="absolute inset-0 bg-black/50 rounded-xl"></div>
                    <div class="relative z-10">
                        <span class="text-xs font-semibold bg-brand-50 text-brand-700 px-3 py-1 rounded-full mb-2 inline-block">Chinese</span>
                        <h3 class="text-white font-bold text-sm leading-snug">CFMoto 800NK Review: The Chinese Naked Bike That's Winning Everywhere</h3>
                        <p class="text-gray-400 text-xs mt-2">May 23, 2026</p>
                    </div>
                </div>
            </a>
        </div>
    </section>'''

index_html = index_html.replace(index_html[trending_start:trending_end], motorcycle_trending)

# Replace the "Latest Reviews & Guides" section to show motorcycle-themed articles
latest_start = index_html.find('<section class="max-w-6xl mx-auto px-4 py-12">')
latest_end = index_html.find('<section class="bg-white py-16')  # Subscribe section starts here
# Find the start of the subscribe section more precisely
subscribe_start = index_html.find('<section class="bg-white py-16 border-t border-gray-100">')

motorcycle_latest = '''<section class="max-w-6xl mx-auto px-4 py-12">
        <h2 class="text-2xl font-black text-gray-900 mb-8">Latest Reviews &amp; Guides</h2>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <a href="article-1.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-1.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">2026 Yamaha YZF-R1 Review: The Ultimate Supersport Machine</h3>
                    <p class="text-gray-500 text-sm">In-depth review of the 2026 Yamaha YZF-R1, covering crossplane engine performance, track handling, electronics package, and how it stacks up against the competition.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 15, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-2.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-2.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">Livewire S2 Mulholland: Harley's Electric Future Takes Shape</h3>
                    <p class="text-gray-500 text-sm">First ride review of the Livewire S2 Mulholland electric motorcycle. Range, charging, real-world performance, and whether it lives up to the Harley legacy.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 10, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-3.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-3.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">Best Beginner Motorcycles 2026: From 300cc to 650cc</h3>
                    <p class="text-gray-500 text-sm">Comprehensive guide to the best beginner motorcycles in 2026. We test Ninja 400, CFMoto 450NK, Yamaha R3, and more to help new riders choose wisely.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 8, 2026</span><span>&middot;</span><span>10 min read</span>
                    </div>
                </div>
            </a>
<a href="article-4.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-4.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">2026 BMW S1000RR Track Test: Is It Still the King of Superbikes?</h3>
                    <p class="text-gray-500 text-sm">We take the 2026 BMW S1000RR to the track to test its updated engine, aerodynamics, and electronics. Lap times, data logs, and rider impressions inside.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 5, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-5.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-5.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">CFMoto 800NK vs Kawasaki Z900: Chinese Naked Bike Face-Off</h3>
                    <p class="text-gray-500 text-sm">Head-to-head comparison of the CFMoto 800NK and Kawasaki Z900. We test power, handling, features, and value to see if the Chinese contender can beat the Japanese icon.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 3, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-6.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-6.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">Essential Motorcycle Maintenance Guide for New Riders</h3>
                    <p class="text-gray-500 text-sm">Learn motorcycle maintenance basics: chain adjustment, oil changes, tire pressure, brake checks, and seasonal storage tips to keep your bike running strong.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>May 1, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-7.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-7.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">MotoGP 2026 Season Preview: Riders, Teams, and Predictions</h3>
                    <p class="text-gray-500 text-sm">Complete preview of the 2026 MotoGP season. Rider transfers, factory team updates, Ducati dominance, and our championship predictions.</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>April 28, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
<a href="article-8.html" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(images/article-8.jpg)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">Zero SR/F vs Livewire S2: Electric Motorcycle Comparison</h3>
                    <p class="text-gray-500 text-sm">We compare the Zero SR/F and Livewire S2 head-to-head: range, charging speed, performance, and daily usability. Which electric bike wins?</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>April 25, 2026</span><span>&middot;</span><span>8 min read</span>
                    </div>
                </div>
            </a>
</div>
        <div class="text-center mt-10">
            <a href="articles.html" class="inline-block bg-brand-600 hover:bg-brand-700 text-white font-semibold px-8 py-3 rounded-full text-lg transition-colors">
                View All Articles →
            </a>
        </div>
    </section>'''

index_html = index_html.replace(index_html[latest_start:subscribe_start], motorcycle_latest)

# Subscribe section - change text
index_html = index_html.replace(
    'Stay in the driver\'s seat.',
    'Stay in the rider\'s seat.'
)
index_html = index_html.replace(
    'Get our latest reviews and guides delivered to your inbox.',
    'Get the latest motorcycle reviews and guides delivered to your inbox.'
)

# Apply standard transformations
index_html = fix_brand_text(index_html)
index_html = fix_colors(index_html)
index_html = fix_gradient_classes(index_html)
index_html = fix_og_text(index_html)
index_html = fix_description_meta(index_html)
index_html = fix_nav_auto(index_html)
index_html = index_html.replace('.carousel-dot.active{background:#dc2626}', '.carousel-dot.active{background:#f97316}')
index_html = index_html.replace('.carousel-dot.active{background:#ea580c}', '.carousel-dot.active{background:#f97316}')

with open(f"{DST}/index.html", 'w', encoding='utf-8') as f:
    f.write(index_html)
print("  Done")

# ============================================================
# 2. about.html
# ============================================================
print("Creating about.html...")
about_html = process_html(f"{SRC}/about.html")

# Replace gradient
about_html = about_html.replace(
    'from-red-50 to-orange-100',
    'from-orange-50 to-amber-50'
)
about_html = about_html.replace(
    'from-red-50 to-orange-100',
    'from-orange-50 to-amber-100'
)

# About page specific content
about_html = about_html.replace(
    'Your go-to source for honest car reviews, EV & hybrid insights, and practical automotive advice',
    'Your go-to source for honest motorcycle reviews, EV bike coverage, riding guides, and motorsport insights'
)

about_html = about_html.replace(
    '{"R","Car Reviews","Honest, behind-the-wheel reviews of the latest cars, SUVs, and trucks. We test real-world performance so you know what to expect."}',
    '{"R","Bike Reviews","Honest, real-world reviews of the latest motorcycles, scooters, and adventure bikes. We test performance, handling, and daily livability."}'
)

about_html = about_html.replace(
    '{"E","EV & Hybrid","Comprehensive coverage of electric and hybrid vehicles, including range tests, charging infrastructure guides, and cost comparisons."}',
    '{"E","EV Bikes","Comprehensive coverage of electric motorcycles, including range tests, charging guides, and cost comparisons against gas bikes."}'
)

about_html = about_html.replace(
    '{"B","Buying Guides","Step-by-step guides to help you research, compare, and negotiate the best deal on your next vehicle, new or used."}',
    '{"B","Buying Guides","Step-by-step guides to help you research, compare, and find the perfect motorcycle for your riding style and budget."}'
)

# Fix the editorial team
about_html = about_html.replace('Marcus Park', 'Marco Rossi')
about_html = about_html.replace('Senior Editor & Road Test Specialist', 'Senior Editor & Motorcycle Test Rider')
about_html = about_html.replace(
    'Over 10 years of automotive journalism experience. Former test driver and automotive engineer.',
    'Over 12 years of motorcycle journalism. Former track day instructor and motocross racer.'
)
about_html = about_html.replace('Elena Liu', 'Sam Torres')
about_html = about_html.replace('EV & Technology Editor', 'EV & Motorsport Editor')
about_html = about_html.replace(
    'Specializes in electric vehicles, hybrid technology, and Chinese automotive brands expanding into global markets.',
    'Specializes in electric motorcycles, motorsport coverage, and Chinese motorcycle brands going global.'
)

# Fix the values section
about_html = about_html.replace(
    'We never accept payment for positive reviews. Our recommendations are based on real-world testing, not sponsorships or advertising dollars.',
    'We never accept payment for positive reviews. Every bike we test is ridden hard and reviewed honestly.'
)
about_html = about_html.replace(
    'We focus on what matters to real drivers. No spec-sheet wars — just useful information that helps you decide.',
    'We focus on what matters to real riders. No spec-sheet wars - just useful info that helps you choose your next bike.'
)
about_html = about_html.replace(
    'Our team combines decades of automotive experience with deep expertise in emerging technologies like EVs, hybrids, and autonomous driving.',
    'Our team combines decades of riding experience with deep expertise in motorcycle technology, EV powertrains, and racing dynamics.'
)
about_html = about_html.replace(
    'The auto industry is changing fast. We keep you informed about Chinese brands going global, new electric platforms, and the future of mobility.',
    'The motorcycle world is changing fast. We track Chinese brands, electric innovation, and the future of two-wheeled mobility.'
)

# Fix the contact CTA
about_html = about_html.replace(
    'Have a question, suggestion, or a vehicle you would like us to review? We would love to hear from you.',
    'Have a question, suggestion, or a bike you would like us to review? We would love to hear from you.'
)

with open(f"{DST}/about.html", 'w', encoding='utf-8') as f:
    f.write(about_html)
print("  Done")

# ============================================================
# 3. contact.html
# ============================================================
print("Creating contact.html...")
contact_html = process_html(f"{SRC}/contact.html")
contact_html = contact_html.replace(
    'from-red-50 to-orange-100',
    'from-orange-50 to-amber-50'
)
contact_html = contact_html.replace(
    'AutoPulse delivers honest car reviews, in-depth EV coverage, and practical buying guides to help you navigate the automotive world with confidence.',
    'MotoPulse delivers honest motorcycle reviews, in-depth EV bike coverage, and practical buying guides to help you navigate the two-wheeled world with confidence.'
)
with open(f"{DST}/contact.html", 'w', encoding='utf-8') as f:
    f.write(contact_html)
print("  Done")

# ============================================================
# 4. privacy-policy.html
# ============================================================
print("Creating privacy-policy.html...")
priv_html = process_html(f"{SRC}/privacy-policy.html")
priv_html = priv_html.replace(
    'accessible from auto.jycsd.com',
    'accessible from moto.jycsd.com'
)
with open(f"{DST}/privacy-policy.html", 'w', encoding='utf-8') as f:
    f.write(priv_html)
print("  Done")

# ============================================================
# 5. terms.html
# ============================================================
print("Creating terms.html...")
terms_html = process_html(f"{SRC}/terms.html")
with open(f"{DST}/terms.html", 'w', encoding='utf-8') as f:
    f.write(terms_html)
print("  Done")

# ============================================================
# 6. cookie-policy.html
# ============================================================
print("Creating cookie-policy.html...")
cookie_html = process_html(f"{SRC}/cookie-policy.html")
with open(f"{DST}/cookie-policy.html", 'w', encoding='utf-8') as f:
    f.write(cookie_html)
print("  Done")

# ============================================================
# 7. robots.txt
# ============================================================
print("Creating robots.txt...")
with open(f"{DST}/robots.txt", 'w', encoding='utf-8') as f:
    f.write("""User-agent: *
Allow: /
Sitemap: https://moto.jycsd.com/sitemap.xml
""")
print("  Done")

# ============================================================
# 8. sitemap.xml
# ============================================================
print("Creating sitemap.xml...")
with open(f"{SRC}/sitemap.xml", 'r', encoding='utf-8') as f:
    sitemap = f.read()
sitemap = sitemap.replace('auto.jycsd.com', 'moto.jycsd.com')
sitemap = sitemap.replace('category-performance.html', 'category-sport.html')
with open(f"{DST}/sitemap.xml", 'w', encoding='utf-8') as f:
    f.write(sitemap)
print("  Done")

# ============================================================
# 9. ads.txt
# ============================================================
print("Creating ads.txt...")
with open(f"{DST}/ads.txt", 'w', encoding='utf-8') as f:
    f.write("google.com, pub-2595917642864488, DIRECT, f08c47fec0942fa0\n")
print("  Done")

# ============================================================
# 10. articles.html
# ============================================================
print("Creating articles.html...")
articles_html = process_html(f"{SRC}/articles.html")

# Replace article titles/lines in the list with motorcycle-themed placeholders
# Clear the article list and put generic motorcycle placeholders
articles_html = re.sub(
    r'<a href="article-\d+\.html" class="flex items-center justify-between py-3 px-4 hover:bg-gray-50 border-b border-gray-100 transition">\s*<span class="text-gray-900 font-medium truncate pr-4">.*?</span>\s*<div class="flex items-center gap-6 text-sm text-gray-400 shrink-0">\s*<span>.*?</span>\s*<span class="w-16 text-right">.*?</span>\s*</div>\s*</a>',
    '', articles_html
)

# Update the "All Articles" h1 text is fine already

with open(f"{DST}/articles.html", 'w', encoding='utf-8') as f:
    f.write(articles_html)
print("  Done")

# ============================================================
# 11. Category pages
# ============================================================
category_map = {
    'category-reviews.html': ('category-reviews.html', 'Bike Reviews', 'Honest, in-depth reviews of the latest motorcycles, scooters, and adventure bikes.'),
    'category-ev.html': ('category-ev.html', 'EV Bikes', 'Everything you need to know about electric motorcycles.'),
    'category-buying.html': ('category-buying.html', 'Buying Guides', 'Smart advice for buying your next motorcycle, new or used.'),
    'category-sport.html': ('category-performance.html', 'Sport & Racing', 'Built for speed. Tested on track. Reviewed for you.'),
    'category-chinese-brands.html': ('category-chinese-brands.html', 'Chinese Motorcycle Brands', 'Tracking Chinese motorcycle brands as they go global.'),
    'category-maintenance.html': ('category-maintenance.html', 'Maintenance & Care', 'Practical tips to keep your bike on the road longer.'),
}

for cat_file, (src_cat, cat_title, cat_desc) in category_map.items():
    print(f"Creating {cat_file}...")
    src_path = f"{SRC}/{src_cat}"
    if os.path.exists(src_path):
        cat_html = process_html(src_path)
        # Fix category-specific content
        cat_html = cat_html.replace(
            'Performance & Racing',
            'Sport &amp; Racing'
        )
        cat_html = cat_html.replace('category-performance.html', 'category-sport.html')
        cat_html = cat_html.replace('category-ev.html', 'category-ev.html')

        # Update URL references in the file
        cat_html = cat_html.replace(cat_title, cat_title)
    else:
        print(f"  WARNING: {src_path} not found, using template")
        # Create from scratch with index.html structure
        with open(f"{SRC}/index.html", 'r', encoding='utf-8') as f:
            cat_html = f.read()
        cat_html = process_html(cat_html)

    with open(f"{DST}/{cat_file}", 'w', encoding='utf-8') as f:
        f.write(cat_html)
    print("  Done")

# ============================================================
# 12. Fix footer network dropdown in all HTML files - add moto.jycsd.com
# ============================================================
print("Fixing footer network dropdowns...")
for fname in os.listdir(DST):
    if fname.endswith('.html'):
        fpath = f"{DST}/{fname}"
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        # Add MotoPulse to the content sites dropdown
        html = html.replace(
            '<option value="https://auto.jycsd.com">AutoPulse</option>',
            '<option value="https://auto.jycsd.com">AutoPulse</option>\n                    <option value="https://moto.jycsd.com">MotoPulse</option>'
        )
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
print("  Done")

# ============================================================
# Validation
# ============================================================
print("\n" + "="*50)
print("VALIDATION")
print("="*50)
files = sorted(os.listdir(DST))
print(f"Files created ({len(files)}):")
for f in files:
    fsize = os.path.getsize(f"{DST}/{f}")
    print(f"  {f:40s} {fsize:>7,} bytes")

# Check expected files
expected = [
    'index.html', 'about.html', 'contact.html',
    'privacy-policy.html', 'terms.html', 'cookie-policy.html',
    'robots.txt', 'sitemap.xml', 'ads.txt', 'articles.html',
    'category-reviews.html', 'category-sport.html', 'category-buying.html',
    'category-ev.html', 'category-maintenance.html', 'category-chinese-brands.html',
]
print(f"\nExpected: {len(expected)}")
print(f"Created: {len(files)}")
missing = [f for f in expected if f not in files]
if missing:
    print(f"MISSING: {missing}")
else:
    print("All expected files present!")

# Check key replacements
print("\nKey replacements check:")
with open(f"{DST}/index.html", 'r', encoding='utf-8') as f:
    idx = f.read()
print(f"  MotoPulse in index.html: {'MotoPulse' in idx}")
print(f"  moto.jycsd.com in index.html: {'moto.jycsd.com' in idx}")
print(f"  #f97316 in index.html (brand-500): {'#f97316' in idx}")
print(f"  #ea580c in index.html (brand-600): {'#ea580c' in idx}")
print(f"  No AutoPulse in index.html: {'AutoPulse' not in idx}")
print(f"  No auto.jycsd.com in index.html: {'auto.jycsd.com' not in idx}")
print(f"  No #dc2626 in index.html: {'#dc2626' not in idx}")

print("\nAll done!")
