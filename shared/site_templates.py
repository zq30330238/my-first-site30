"""Site template engine — load templates, inject variables, wrap AI-generated content.

Global values centralized here. Change once, apply everywhere.
"""

import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "shared" / "templates"

# Global values used across all sites
GLOBALS = {
    "email": "contact@jycsd.com",
    "ga4_id": "G-GGNWR1X1GV",
    "adsense_pub": "ca-pub-2595917642864488",
    "year": str(datetime.now().year),
}

SITE_CONFIG = {
    "sub-pets": {
        "brand": "PetCareHub",
        "domain": "pets.jycsd.com",
        "category": "Pet Care",
        "brandColor": "orange-600",
        "brandHex": "#ea580c",
        "tailwindColors": """brand: {50: '#fff7ed', 100: '#ffedd5', 200: '#fed7aa', 400: '#fb923c', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#f97316",
        "blockquoteBg": "#fff7ed",
        "related_articles": [
            ("article-11.html", "Pet Emergencies: What Every Owner Must Know Before Disaster Strikes"),
            ("article-27.html", "Pet First Aid Kit: Essential Supplies Every Owner Needs"),
            ("article-3.html", "How to Care for a New Puppy: First Month Checklist"),
        ],
    },
    "sub-healthy": {
        "brand": "HealthyEats",
        "domain": "healthy.jycsd.com",
        "category": "Healthy Eating",
        "brandColor": "green-600",
        "brandHex": "#16a34a",
        "tailwindColors": """brand: {50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#22c55e",
        "blockquoteBg": "#f0fdf4",
        "related_articles": [
            ("article-1.html", "10 Superfoods You Should Eat Every Day for Optimal Health"),
            ("article-2.html", "Beginner's Guide to Weekly Meal Prepping: Save Time and Eat Better"),
            ("article-3.html", "How to Build a Balanced Plate at Every Meal Without Counting Calories"),
        ],
    },
    "sub-home": {
        "brand": "HomeNest",
        "domain": "home.jycsd.com",
        "category": "Home & Garden",
        "brandColor": "emerald-700",
        "brandHex": "#047857",
        "tailwindColors": """brand: {50: '#ecfdf5', 100: '#d1fae5', 200: '#a7f3d0', 400: '#34d399', 500: '#10b981', 600: '#059669', 700: '#047857', 800: '#065f46'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#10b981",
        "blockquoteBg": "#ecfdf5",
        "related_articles": [
            ("article-1.html", "15 DIY Home Improvement Projects Under $100"),
            ("article-2.html", "Beginner's Guide to Indoor Plant Care"),
            ("article-3.html", "How to Declutter Your Home: Room-by-Room Guide"),
        ],
    },
    "sub-finance": {
        "brand": "MoneyWise",
        "domain": "finance.jycsd.com",
        "category": "Personal Finance",
        "brandColor": "blue-700",
        "brandHex": "#1d4ed8",
        "tailwindColors": """brand: {50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#3b82f6",
        "blockquoteBg": "#eff6ff",
        "related_articles": [
            ("article-1.html", "How to Start Investing with $100: A Complete Beginner's Guide"),
            ("article-2.html", "Best High-Yield Savings Accounts: 2026 Comparison Guide"),
            ("article-3.html", "Credit Score Explained: How to Improve Yours Fast"),
        ],
    },
    "sub-tech": {
        "brand": "TechPulse",
        "domain": "tech.jycsd.com",
        "category": "Technology",
        "brandColor": "slate-700",
        "brandHex": "#334155",
        "tailwindColors": """brand: {50: '#f8fafc', 100: '#f1f5f9', 200: '#e2e8f0', 400: '#94a3b8', 500: '#64748b', 600: '#475569', 700: '#334155', 800: '#1e293b'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#64748b",
        "blockquoteBg": "#f8fafc",
        "related_articles": [
            ("article-1.html", "Best Budget Smartphones Under $300 (2026)"),
            ("article-2.html", "How to Build a Home Office Setup for Productivity"),
            ("article-3.html", "AI Tools That Will Change Your Daily Workflow"),
        ],
    },
    "sub-travel": {
        "brand": "TravelScope",
        "domain": "travel.jycsd.com",
        "category": "Travel",
        "brandColor": "cyan-700",
        "brandHex": "#0e7490",
        "tailwindColors": """brand: {50: '#ecfeff', 100: '#cffafe', 200: '#a5f3fc', 400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2', 700: '#0e7490', 800: '#155e75'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#06b6d4",
        "blockquoteBg": "#ecfeff",
        "related_articles": [
            ("article-1.html", "10 Budget Travel Destinations for 2026"),
            ("article-2.html", "How to Find Cheap Flights: Expert Hacks"),
            ("article-3.html", "Solo Travel Guide: Safety Tips & Best Destinations"),
        ],
    },
    "sub-auto": {
        "brand": "AutoPulse",
        "domain": "auto.jycsd.com",
        "category": "Automotive",
        "brandColor": "red-600",
        "brandHex": "#dc2626",
        "tailwindColors": """brand: {50: '#fef2f2', 100: '#fee2e2', 200: '#fecaca', 400: '#f87171', 500: '#ef4444', 600: '#dc2626', 700: '#b91c1c', 800: '#991b1b'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#ef4444",
        "blockquoteBg": "#fef2f2",
        "related_articles": [
            ("article-1.html", "Best Sports Cars Under $50,000 in 2026"),
            ("article-2.html", "EV vs Hybrid vs Plug-in Hybrid: Which Is Right for You?"),
            ("article-3.html", "How to Negotiate a Car Price: 7 Dealer Tactics Exposed"),
        ],
        "predefined_topics": [
            {"title": "BYD Dolphin: The Affordable Electric Hatchback Reshaping Urban Mobility", "category": "ev", "angle": "urban EV review", "key_points": ["Compact design optimized for city driving and parking", "Affordable price point under $25,000 in most markets", "Interior space utilization and tech features", "Real-world range and charging convenience for daily commuters"]},
            {"title": "Huawei AITO M9 Review: The Tech Giant's Flagship EV SUV with HarmonyOS Smart Cockpit", "category": "ev", "angle": "technology showcase review", "key_points": ["HarmonyOS smart cockpit experience and voice control", "Huawei ADS 2.0 autonomous driving capabilities", "Premium interior materials and zero-gravity seats", "Range, performance, and charging specs"]},
            {"title": "Avatr 12: Huawei and Changan's Premium Electric Sedan with 700km Range", "category": "ev", "angle": "premium EV review", "key_points": ["Striking design by Nader Faghihzadeh (ex-BMW)", "Huawei-powered interior and driver assistance tech", "CATL battery and 700km+ range performance", "Positioning against NIO ET7 and Mercedes EQE"]},
        ],
    },
    "rightsdaily": {
        "brand": "RightsDaily",
        "domain": "rightsdaily.com",
        "category": "Legal Rights",
        "brandColor": "blue-800",
        "brandHex": "#1e40af",
        "tailwindColors": """brand: {50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#3b82f6",
        "blockquoteBg": "#eff6ff",
        "related_articles": [
            ("article-1.html", "Know Your Rights: A Complete Guide to Consumer Protection Laws"),
            ("article-2.html", "Landlord-Tenant Disputes: Legal Options and Tenant Rights"),
            ("article-3.html", "Divorce Process Simplified: What You Need to Know Before Filing"),
        ],
    },
    "dailymedadvice": {
        "brand": "DailyMedAdvice",
        "domain": "dailymedadvice.com",
        "category": "Health & Medical",
        "brandColor": "green-700",
        "brandHex": "#15803d",
        "tailwindColors": """brand: {50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d', 800: '#166534'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#22c55e",
        "blockquoteBg": "#f0fdf4",
        "related_articles": [
            ("article-1.html", "Understanding Common Cold vs Flu: Symptoms, Treatment, and When to See a Doctor"),
            ("article-2.html", "Blood Pressure 101: What Your Numbers Mean and How to Manage Them"),
            ("article-3.html", "Complete Guide to Vitamin D: Benefits, Sources, and Deficiency Symptoms"),
        ],
    },
    "entertainment": {
        "brand": "EntertainmentBuzz",
        "domain": "entertainment.jycsd.com",
        "category": "Entertainment",
        "brandColor": "purple-600",
        "brandHex": "#9333ea",
        "tailwindColors": """brand: {50: '#faf5ff', 100: '#f3e8ff', 200: '#e9d5ff', 400: '#c084fc', 500: '#a855f7', 600: '#9333ea', 700: '#7e22ce', 800: '#6b21a8'}""",
        "fontHeading": "'Georgia', 'Times New Roman', 'serif'",
        "blockquoteColor": "#a855f7",
        "blockquoteBg": "#faf5ff",
        "related_articles": [
            ("article-1.html", "Celebrity News Roundup: Biggest Stories This Week You Missed"),
            ("article-2.html", "Top 10 Must-Watch TV Shows Premiering This Month"),
            ("article-3.html", "Hollywood Gossip: Behind-the-Scenes Secrets From Your Favorite Movies"),
        ],
    },
}

# HTML template skeleton with placeholders
TEMPLATE_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{adsense_pub}}" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={{ga4_id}}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '{{ga4_id}}');
</script>
<meta charset="UTF-8">
<meta name="google-adsense-account" content="{{adsense_pub}}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{{meta_tags}}
<meta name="robots" content="index, follow">
<meta property="og:site_name" content="{{brand}}">
<meta property="og:locale" content="en_US">
{{og_tags}}
<title>{{title}}</title>
<link rel="canonical" href="{{article_url}}">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
    theme: {
        extend: {
            colors: {
                {{tailwind_colors}}
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                heading: [{{font_heading}}],
            }
        }
    }
}
</script>
<style>
.ad-unit {
    background: #f9fafb;
    border-radius: 8px;
    text-align: center;
    margin: 2.5rem 0;
    padding: 0.5rem 0 1.5rem 0;
    overflow: hidden;
}
.ad-label {
    display: block;
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.article-content h2 { font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; }
.article-content h3 { font-size: 1.35rem; font-weight: 600; color: #1f2937; margin-top: 2rem; margin-bottom: 0.75rem; }
.article-content p { margin-bottom: 1.25rem; line-height: 1.8; font-size: 1.1rem; color: #374151; }
.article-content ul, .article-content ol { margin-bottom: 1.25rem; padding-left: 1.5rem; }
.article-content li { margin-bottom: 0.5rem; line-height: 1.7; font-size: 1.05rem; color: #374151; }
.article-content blockquote {
    border-left: 4px solid {{blockquote_color}};
    padding: 1rem 1.5rem;
    margin: 2rem 0;
    background: {{blockquote_bg}};
    border-radius: 0 8px 8px 0;
    font-style: italic;
    color: #374151;
}
</style>
</head>
<body class="bg-white font-sans antialiased flex flex-col min-h-screen">
<header class="bg-white border-b border-gray-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <a href="index.html" class="text-2xl font-bold text-{{brand_color}} font-heading">{{brand}}</a>
            <nav class="hidden md:flex space-x-8 text-sm font-medium">
                <a href="index.html" class="text-gray-700 hover:text-{{brand_color}} transition">Home</a>
                <a href="category-reviews.html" class="text-gray-700 hover:text-{{brand_color}} transition">Reviews</a>
                <a href="category-ev.html" class="text-gray-700 hover:text-{{brand_color}} transition">EV &amp; Hybrid</a>
                <a href="category-buying.html" class="text-gray-700 hover:text-{{brand_color}} transition">Buying</a>
                <a href="category-performance.html" class="text-gray-700 hover:text-{{brand_color}} transition">Performance</a>
                <a href="category-chinese-brands.html" class="text-gray-700 hover:text-{{brand_color}} transition">Chinese Brands</a>
                <a href="about.html" class="text-gray-700 hover:text-{{brand_color}} transition">About</a>
                <a href="contact.html" class="text-gray-700 hover:text-{{brand_color}} transition">Contact</a>
            </nav>
        </div>
    </div>
</header>
<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1">
    <nav class="text-sm text-gray-400 mb-8" aria-label="Breadcrumb">
        <a href="index.html" class="hover:text-{{brand_color}} transition">Home</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{{breadcrumb}}</span>
    </nav>
    <article>
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-heading font-bold text-gray-900 leading-tight mb-4">{{h1_title}}</h1>
            <div class="flex items-center text-sm text-gray-400 space-x-4">
                <time datetime="{{date_iso}}">{{date_display}}</time>
                <span>{{read_time}} min read</span>
            </div>
        </header>
        {{cover_img_html}}
        <div class="article-content">
            {{article_body}}
        </div>
        <div class="mt-10 flex flex-wrap gap-2">
            {{tag_spans}}
        </div>
    </article>
    <aside class="mt-16 bg-gray-50 rounded-2xl p-8">
        <h3 class="text-lg font-bold text-gray-900 mb-6">Related Articles</h3>
        <div class="grid md:grid-cols-3 gap-6">
            <a href="{{related_1_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_1_title}}</p></a>
            <a href="{{related_2_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_2_title}}</p></a>
            <a href="{{related_3_url}}" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-{{brand_color}}/30 transition"><span class="text-sm text-{{brand_color}} font-medium">Related</span><p class="text-gray-700 text-sm mt-1">{{related_3_title}}</p></a>
        </div>
    </aside>
</main>
<footer class="bg-gray-900 text-gray-400 py-12">
    <div class="max-w-6xl mx-auto px-4">
        <div class="grid md:grid-cols-4 gap-8 mb-10">
            <div>
                <h3 class="text-white text-lg font-black mb-3">{{brand}}</h3>
                <p class="text-sm leading-relaxed">{{brand_description}}</p>
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
                <h4 class="text-white font-semibold mb-3">Our Network</h4>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 mb-3 border border-gray-700 focus:outline-none focus:border-{{brand_color}} cursor-pointer">
                    <option value="">-- Network --</option>
                    <option value="https://www.jycsd.com">Main Site</option>
                    <option value="https://games.jycsd.com">Game Guides</option>
                    <option value="https://anime.jycsd.com">Anime &amp; Manga</option>
                </select>
                <select onchange="if(this.value)window.location.href=this.value" class="w-full bg-gray-800 text-gray-300 text-sm rounded px-3 py-2 border border-gray-700 focus:outline-none focus:border-{{brand_color}} cursor-pointer">
                    <option value="">-- More Sites --</option>
                    <option value="https://healthy.jycsd.com">HealthyEats</option>
                    <option value="https://pets.jycsd.com">PetCare Hub</option>
                    <option value="https://home.jycsd.com">HomeJoy</option>
                    <option value="https://finance.jycsd.com">MoneyWise</option>
                    <option value="https://tech.jycsd.com">TechNest</option>
                    <option value="https://travel.jycsd.com">TripRoute</option>
                    <option value="https://auto.jycsd.com">AutoPulse</option>
                    <option value="https://rightsdaily.com">RightsDaily</option>
                    <option value="https://dailymedadvice.com">DailyMedAdvice</option>
                </select>
            </div>
            <div>
                <h4 class="text-white font-semibold mb-3">Contact</h4>
                <ul class="space-y-2 text-sm">
                    <li><a href="mailto:{{email}}" class="hover:text-white transition-colors">{{email}}</a></li>
                </ul>
            </div>
        </div>
        <div class="border-t border-gray-800 pt-6 text-center text-sm">
            <p>&copy; {{year}} {{brand}}. All rights reserved.</p>
        </div>
    </div>
</footer>
<script type="application/ld+json">
{{json_ld}}
</script>
</body>
</html>"""


def get_content_generation_prompt(site_dir, article_num, topic=None):
    """Returns just the content-relevant info for DeepSeek to generate the article body."""
    cfg = SITE_CONFIG[site_dir]
    domain = cfg["domain"]
    url = f"https://{domain}/article-{article_num}.html"
    today = datetime.now().strftime("%Y-%m-%d")
    result = {
        "brand": cfg["brand"],
        "category": cfg["category"],
        "domain": domain,
        "article_url": url,
        "article_num": article_num,
        "date": today,
        "brand_color": cfg["brandColor"],
        "brand_hex": cfg["brandHex"],
    }

    if topic:
        result["topic_title"] = topic["title"]
        result["topic_category"] = topic["category"]

    return result


def render_article_html(site_dir, ai_output):
    """Inject AI-generated content into the site template. ai_output is a dict with keys:
    title, description, keywords, og_title, og_description,
    h1_title, breadcrumb, cover_img_html, article_body_html,
    tag_spans, json_ld, read_time, date_iso, date_display
    """
    cfg = SITE_CONFIG[site_dir]
    vars_dict = {**GLOBALS, **cfg}

    # Generate meta tags server-side (AI never includes these — don't rely on it)
    description = ai_output.get("description", ai_output["h1_title"])
    desc_clean = description.replace('"', "&quot;").replace("\n", " ")
    article_url = ai_output.get("article_url", f"https://{cfg['domain']}/article-N.html")
    og_title = ai_output.get("og_title", ai_output["title"])
    og_title_clean = og_title.replace('"', "&quot;")
    vars_dict["meta_tags"] = f'<meta name="description" content="{desc_clean}">'
    vars_dict["og_tags"] = (
        f'<meta property="og:description" content="{desc_clean}">\n'
        f'    <meta property="og:title" content="{og_title_clean}">\n'
        f'    <meta property="og:url" content="{article_url}">\n'
        f'    <meta property="og:type" content="article">'
    )
    # Avoid brand duplication: if AI title already includes brand name, don't append it
    title = ai_output["title"]
    brand_name = cfg.get("brand", "")
    if brand_name and brand_name not in title:
        title = f"{title} - {brand_name}"
    vars_dict["title"] = title
    vars_dict["article_url"] = article_url
    vars_dict["h1_title"] = ai_output["h1_title"]
    vars_dict["breadcrumb"] = ai_output.get("breadcrumb", ai_output["h1_title"])
    vars_dict["article_body"] = ai_output["article_body_html"]
    vars_dict["tag_spans"] = ai_output.get("tag_spans", "")
    vars_dict["json_ld"] = ai_output["json_ld"]
    vars_dict["read_time"] = ai_output.get("read_time", "7")
    vars_dict["date_iso"] = ai_output["date_iso"]
    vars_dict["date_display"] = ai_output["date_display"]
    # Cover image (optional, generated by Seedream pipeline)
    image_url = ai_output.get("cover_img_url", "")
    if image_url:
        vars_dict["cover_img_html"] = f'<img src="{image_url}" alt="{ai_output.get("h1_title", "")}" class="w-full rounded-2xl mb-10" loading="lazy">'
        og_image_url = f"https://{cfg['domain']}/{image_url}"
    else:
        vars_dict["cover_img_html"] = ""
        # Default OG image fallback
        og_image_url = f"https://{cfg['domain']}/images/default-og.jpg"
    vars_dict["og_tags"] += f'\n    <meta property="og:image" content="{og_image_url}">'
    vars_dict["brand_color"] = cfg["brandColor"]
    vars_dict["tailwind_colors"] = cfg["tailwindColors"]
    vars_dict["font_heading"] = cfg["fontHeading"]
    vars_dict["blockquote_color"] = cfg["blockquoteColor"]
    vars_dict["blockquote_bg"] = cfg["blockquoteBg"]
    vars_dict["brand_description"] = cfg.get("brand_description", f"{cfg['brand']} provides practical information for everyday life.")

    # Network section — single link back to hub only (no PBN cross-linking)
    vars_dict["network_section"] = """<div class="text-center mb-6">
                <p class="text-sm text-gray-400">Part of the <a href="https://www.jycsd.com" class="text-{{brand_color}} hover:underline transition">Myers Media</a> network.</p>
            </div>"""

    # Related articles
    related = cfg["related_articles"]
    vars_dict["related_1_url"] = related[0][0]
    vars_dict["related_1_title"] = related[0][1]
    vars_dict["related_2_url"] = related[1][0]
    vars_dict["related_2_title"] = related[1][1]
    vars_dict["related_3_url"] = related[2][0]
    vars_dict["related_3_title"] = related[2][1]

    html = TEMPLATE_SKELETON
    for key, value in vars_dict.items():
        html = html.replace("{{" + key + "}}", str(value))

    return html, vars_dict


def quick_validate(html, site_dir):
    """Fast validation of rendered HTML."""
    issues = []
    if not html.startswith("<!DOCTYPE html>"):
        issues.append("Missing DOCTYPE")
    if "source.unsplash.com" in html:
        issues.append("Dead source.unsplash.com URL")
    if "30330238@qq.com" in html:
        issues.append("QQ email leaked through")
    if GLOBALS["ga4_id"] not in html:
        issues.append("Missing GA4 tag")
    if GLOBALS["adsense_pub"] not in html:
        issues.append("Missing AdSense pub ID")
    if SITE_CONFIG[site_dir]["domain"] not in html:
        issues.append("Wrong domain")
    return issues
