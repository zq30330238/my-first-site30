"""Batch article generator — uses DeepSeek API to generate SEO-optimized HTML articles.
Usage: py shared/batch_articles.py <site> <start-num> <topic-file>
Example: py shared/batch_articles.py sub-healthy 16 topics_healthy.txt
"""
import sys, os, json, re, time
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
API_KEY = os.environ.get('ANTHROPIC_AUTH_TOKEN') or os.environ.get('DEEPSEEK_API_KEY', '')
BASE_URL = 'https://api.deepseek.com/anthropic'
MODEL = os.environ.get('ANTHROPIC_MODEL', 'deepseek-v4-pro')

SITE_CONFIG = {
    'sub-healthy': {
        'domain': 'healthy.jycsd.com',
        'site_name': 'HealthyEats',
        'brand_color': '#22c55e',
        'brand_bg': '#f0fdf4',
        'primary': '22c55e', 'p50': 'f0fdf4', 'p100': 'dcfce7', 'p200': 'bbf7d0',
        'p400': '4ade80', 'p500': '22c55e', 'p600': '16a34a', 'p700': '15803d', 'p800': '166534',
        'category': 'Health & Nutrition',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'healthy food nutrition cooking ingredients',
    },
    'sub-pets': {
        'domain': 'pets.jycsd.com',
        'site_name': 'PetCareHub',
        'brand_color': '#f97316',
        'brand_bg': '#fff7ed',
        'primary': 'f97316', 'p50': 'fff7ed', 'p100': 'ffedd5', 'p200': 'fed7aa',
        'p400': 'fb923c', 'p500': 'f97316', 'p600': 'ea580c', 'p700': 'c2410c', 'p800': '9a3412',
        'category': 'Pet Care',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'pets dogs cats animals',
    },
    'sub-home': {
        'domain': 'home.jycsd.com',
        'site_name': 'HomeJoy',
        'brand_color': '#84cc16',
        'brand_bg': '#f7fee7',
        'primary': '84cc16', 'p50': 'f7fee7', 'p100': 'ecfccb', 'p200': 'd9f99d',
        'p400': 'a3e635', 'p500': '84cc16', 'p600': '65a30d', 'p700': '4d7c0f', 'p800': '3f6212',
        'category': 'Home & Garden',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'home interior garden plants DIY',
    },
    'sub-finance': {
        'domain': 'finance.jycsd.com',
        'site_name': 'MoneyWise',
        'brand_color': '#3b82f6',
        'brand_bg': '#eff6ff',
        'primary': '3b82f6', 'p50': 'eff6ff', 'p100': 'dbeafe', 'p200': 'bfdbfe',
        'p400': '60a5fa', 'p500': '3b82f6', 'p600': '2563eb', 'p700': '1d4ed8', 'p800': '1e40af',
        'category': 'Personal Finance',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'money finance business savings investment',
    },
    'sub-tech': {
        'domain': 'tech.jycsd.com',
        'site_name': 'TechSift',
        'brand_color': '#6366f1',
        'brand_bg': '#eef2ff',
        'primary': '6366f1', 'p50': 'eef2ff', 'p100': 'e0e7ff', 'p200': 'c7d2fe',
        'p400': '818cf8', 'p500': '6366f1', 'p600': '4f46e5', 'p700': '4338ca', 'p800': '3730a3',
        'category': 'Technology',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'technology gadgets computer smartphone',
    },
    'sub-travel': {
        'domain': 'travel.jycsd.com',
        'site_name': 'TripRoute',
        'brand_color': '#06b6d4',
        'brand_bg': '#ecfeff',
        'primary': '06b6d4', 'p50': 'ecfeff', 'p100': 'cffafe', 'p200': 'a5f3fc',
        'p400': '22d3ee', 'p500': '06b6d4', 'p600': '0891b2', 'p700': '0e7490', 'p800': '155e75',
        'category': 'Travel',
        'footer_links': ['about.html', 'contact.html', 'privacy-policy.html', 'terms.html'],
        'unsplash_terms': 'travel destination adventure nature',
    },
}

SITE_TOPICS = {
    'sub-healthy': [
        "Best Anti-Inflammatory Foods to Add to Your Diet",
        "How to Stop Emotional Eating for Good",
        "Probiotics vs Prebiotics: What's the Difference",
        "The Mediterranean Diet for Beginners: Full Guide",
        "How Sleep Affects Your Metabolism and Weight",
        "Healthy Snacks That Keep You Full Between Meals",
        "How to Eat Healthy on a Tight Budget",
        "Kidney Health: Best and Worst Foods for Your Kidneys",
        "How to Reduce Bloating with Simple Diet Changes",
        "Are Smoothie Bowls Actually Healthy? The Real Answer",
        "Bone Health: Calcium-Rich Foods Beyond Dairy",
        "How to Break a Sugar Addiction Step by Step",
        "Detox Diets Debunked: What Science Actually Says",
        "Best Foods for Brain Health and Mental Clarity",
        "How to Read Food Expiration Dates the Right Way",
    ],
    'sub-pets': [
        "Best Cat Breeds for First-Time Pet Owners",
        "How to Litter Train a Kitten in One Week",
        "Dog Separation Anxiety: Causes and Solutions",
        "Best Pet Cameras for Monitoring Pets While Away",
        "How to Choose the Right Dog Walker or Pet Sitter",
        "Pet Food Labels Explained: What to Look For",
        "How to Bathe a Cat Without Getting Scratched",
        "Raw Food Diet for Dogs: Pros and Cons",
        "Pet Obesity: How to Help Your Pet Lose Weight",
        "Best Interactive Toys to Keep Your Dog Mentally Sharp",
        "How to Care for a Senior Cat: Health and Comfort",
        "Pet First Aid Kit: Essentials Every Owner Needs",
        "Bird Care Guide: What First-Time Owners Must Know",
        "Cat Scratching Solutions That Save Your Furniture",
        "How to Introduce a New Dog to Your Resident Cat",
    ],
    'sub-home': [
        "How to Choose the Right Paint Finish for Each Room",
        "DIY Raised Garden Beds: Build One in a Weekend",
        "How to Fix Common Toilet Problems Without a Plumber",
        "Best Indoor Lighting Ideas to Brighten Dark Rooms",
        "How to Start a Worm Composting Bin at Home",
        "Seasonal Decor Storage Tips That Save Space",
        "How to Clean and Maintain Wood Furniture Properly",
        "Best Low-Light Houseplants That Are Hard to Kill",
        "How to Childproof Your Home Room by Room",
        "DIY Backsplash Installation for Complete Beginners",
        "How to Reduce Home Energy Costs Year Round",
        "Closet Organization Ideas for Maximum Storage",
        "How to Restore Old Hardware Instead of Replacing",
        "Best Humidifiers for Every Room Size in 2026",
        "How to Create a Cozy Outdoor Living Space on a Budget",
    ],
    'sub-finance': [
        "How to Start a 529 College Savings Plan",
        "Roth IRA vs Traditional IRA: Making the Right Choice",
        "How to Build a CD Ladder for Guaranteed Returns",
        "Financial Planning for Newlyweds: First Year Guide",
        "How to Dispute Errors on Your Credit Report",
        "Rent vs Buy Calculator: Making the Smart Choice",
        "How to Save for a House Down Payment Faster",
        "Best Budgeting Methods Beyond the 50-30-20 Rule",
        "How to Calculate Your Net Worth and Track Growth",
        "Identity Theft Protection: Steps to Stay Safe",
        "How to Read a Pay Stub and Understand Deductions",
        "Recession-Proof Your Finances: Practical Steps",
        "Best Money Management Apps for Couples in 2026",
        "How to Plan a Wedding Without Going Into Debt",
        "Retirement Account Rollover: Complete Guide",
    ],
    'sub-tech': [
        "Best Password Managers to Secure Your Accounts",
        "How to Clean Up Your Digital Footprint Online",
        "Beginner's Guide to Smart Home Automation",
        "Best E-Readers for Every Budget in 2026",
        "How to Troubleshoot Common Wi-Fi Problems at Home",
        "No-Code Tools That Anyone Can Use to Build Apps",
        "How to Choose the Right Tablet for Work and Play",
        "Best Standing Desks and Ergonomic Office Gear",
        "How to Organize Your Digital Photos and Files",
        "Bluetooth vs Wi-Fi Speakers: Which to Choose",
        "Best Budget Monitors for Home Office Use",
        "How to Protect Your Privacy on Social Media",
        "Smartwatch Buying Guide: Features That Matter",
        "How to Set Up Parental Controls on Any Device",
        "Best Free Online Courses to Learn Tech Skills",
    ],
    'sub-travel': [
        "How to Survive Long-Haul Flights Comfortably",
        "Best Travel Backpacks for Every Type of Trip",
        "How to Plan an Affordable Family Vacation",
        "Best Destinations for Winter Sun in 2026",
        "How to Use Public Transport in Any Foreign City",
        "Travel Photography Tips for Better Trip Photos",
        "How to Book Multi-City Flights and Save Money",
        "Best Hiking Destinations for Beginners Worldwide",
        "How to Handle Currency Exchange Without Getting Ripped Off",
        "Solo Female Travel: Safety Tips and Top Destinations",
        "How to Plan a Road Trip With an Electric Vehicle",
        "Best Language Learning Apps for Travelers",
        "How to Find Authentic Local Food While Traveling",
        "National Park Guide: Best Times to Visit Each",
        "How to Get Travel Visas Without the Headache",
    ],
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2595917642864488" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GGNWR1X1GV"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', 'G-GGNWR1X1GV');
</script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="index, follow">
    <meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{og_url}">
    <meta property="og:site_name" content="{site_name}">
    <meta property="og:locale" content="en_US">
    <title>{title}</title>
    <link rel="canonical" href="{canonical_url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        brand: {{
                            50: '#{p50}',
                            100: '#{p100}',
                            200: '#{p200}',
                            400: '#{p400}',
                            500: '#{p500}',
                            600: '#{p600}',
                            700: '#{p700}',
                            800: '#{p800}',
                        }}
                    }},
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                        heading: ['Georgia', 'Times New Roman', 'serif'],
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .ad-container {{
            background: #f9fafb;
            border: 2px dashed #e5e7eb;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #9ca3af;
            font-size: 14px;
            min-height: 90px;
        }}
        .article-content h2 {{ font-size: 1.75rem; font-weight: 700; color: #111827; margin-top: 2.5rem; margin-bottom: 1rem; }}
        .article-content h3 {{ font-size: 1.35rem; font-weight: 600; color: #1f2937; margin-top: 2rem; margin-bottom: 0.75rem; }}
        .article-content p {{ margin-bottom: 1.25rem; line-height: 1.8; font-size: 1.1rem; color: #374151; }}
        .article-content ul, .article-content ol {{ margin-bottom: 1.25rem; padding-left: 1.5rem; }}
        .article-content li {{ margin-bottom: 0.5rem; line-height: 1.7; font-size: 1.05rem; color: #374151; }}
        .article-content blockquote {{
            border-left: 4px solid {brand_color};
            padding: 1rem 1.5rem;
            margin: 2rem 0;
            background: {brand_bg};
            border-radius: 0 8px 8px 0;
            font-style: italic;
            color: #374151;
        }}
    </style>
</head>
<body class="bg-white font-sans antialiased">
<header class="bg-white border-b border-gray-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
            <a href="index.html" class="text-2xl font-bold text-brand-600 font-heading">{site_name}</a>
            <nav class="hidden md:flex space-x-8 text-sm font-medium">
                <a href="index.html" class="text-gray-700 hover:text-brand-600 transition">Home</a>
                <a href="about.html" class="text-gray-700 hover:text-brand-600 transition">About</a>
                <a href="contact.html" class="text-gray-700 hover:text-brand-600 transition">Contact</a>
            </nav>
        </div>
    </div>
</header>
<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <nav class="text-sm text-gray-400 mb-8" aria-label="Breadcrumb">
        <a href="index.html" class="hover:text-brand-600 transition">Home</a>
        <span class="mx-2">/</span>
        <span class="text-gray-600">{title_short}</span>
    </nav>
    <article>
        <header class="mb-10">
            <h1 class="text-4xl md:text-5xl font-heading font-bold text-gray-900 leading-tight mb-4">{title_short}</h1>
            <div class="flex items-center text-sm text-gray-400 space-x-4">
                <time datetime="{date}">{date_formatted}</time>
                <span>{read_time} min read</span>
            </div>
        </header>
        <div class="article-content">
            {article_body}
        </div>
        <div class="mt-10 flex flex-wrap gap-2">
            {tag_pills}
        </div>
    </article>
    <aside class="mt-16 bg-gray-50 rounded-2xl p-8">
        <h3 class="text-lg font-bold text-gray-900 mb-6">Related Articles</h3>
        <div class="grid md:grid-cols-3 gap-6">
            {related_articles}
        </div>
    </aside>
    <div class="ad-container my-12" style="min-height:120px">
        <span>Advertisement</span>
    </div>
</main>
<footer class="bg-gray-100 border-t border-gray-200 mt-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div class="flex flex-wrap justify-between items-center">
            <p class="text-sm text-gray-500">&copy; {year} {site_name}. All rights reserved.</p>
            <div class="flex space-x-6 text-sm">
                {footer_links}
            </div>
        </div>
    </div>
</footer>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{title_short}",
  "description": "{og_desc}",
  "author": {{"@type": "Person", "name": "Editorial Team"}},
  "datePublished": "{date}",
  "dateModified": "{date}",
  "publisher": {{"@type": "Organization", "name": "{site_name}"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "{canonical_url}"}}
}}
</script>
</body>
</html>'''


def build_prompt(site, topic, num, existing_articles_html):
    cfg = SITE_CONFIG[site]
    return f"""You are a professional content writer for {cfg['site_name']} ({cfg['category']} site).
Write a complete HTML article about: "{topic}"

Requirements:
- 1000-1500 words of body content (in the article_content div)
- 4-6 H2 sections with practical, original advice
- Use active voice, 2nd person ("you"), vary sentence length
- Include 1-2 specific stats/numbers per section
- Avoid AI-sounding words: no "delve", "embrace", "elevate", "unlock", "game-changer"
- Use contractions naturally (don't, you'll, it's)
- No emoji, no markdown

Structure each H2 section as: core claim → supporting detail → practical takeaway

The article body should be placed where {{article_body}} appears. Use proper HTML paragraph and heading tags.
Also provide:
- meta_desc: 120-155 chars, include primary keyword, actionable
- keywords: 5-7 keywords/phrases, comma separated
- tags: 4-6 tag words/phrases for the tag pills section
- read_time: estimated minutes (1 min per 200 words)

The site has these existing articles (do NOT duplicate topics):
{existing_articles_html}

Article filename will be: article-{num}.html

Use a relevant Unsplash hero image in the article body (first element after h1):
<img src="https://images.unsplash.com/photo-(relevant)?w=1200&h=630&fit=crop" alt="descriptive alt text" class="rounded-2xl mb-10 w-full">

Pick a relevant Unsplash image URL that matches the topic. Use real, working Unsplash photo URLs with the format:
https://images.unsplash.com/photo-XXXXX?w=1200&h=630&fit=crop

Respond in this exact JSON format:
{{
  "title_short": "Article Title Without Site Name",
  "meta_desc": "120-155 char meta description",
  "keywords": "keyword1, keyword2, keyword3, keyword4, keyword5",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"],
  "read_time": 7,
  "article_body": "<h2>Section One Title</h2><p>Paragraph text...</p>...",
  "unsplash_url": "https://images.unsplash.com/photo-XXXXX?w=1200&h=630&fit=crop",
  "unsplash_alt": "descriptive alt text"
}}

Write only valid JSON, no other text."""


def build_html(site, topic_num, topic, data):
    cfg = SITE_CONFIG[site]
    from datetime import date
    today = date.today()
    date_str = today.isoformat()
    date_fmt = today.strftime('%B %d, %Y')

    # Build tag pills
    tags = data.get('tags', [topic])
    tag_html = '\n            '.join(
        f'<span class="px-3 py-1 bg-brand-50 text-brand-700 text-sm rounded-full">{t}</span>'
        for t in tags
    )

    # Simple related articles (link to first few)
    related = '\n            '.join(
        f'<a href="article-{i}.html" class="block p-4 bg-white rounded-xl border border-gray-200 hover:border-brand-300 transition"><span class="text-sm text-brand-600 font-medium">Related</span><p class="text-gray-700 text-sm mt-1">Article {i}</p></a>'
        for i in range(1, 4)
    )

    footer_html = '\n                '.join(
        f'<a href="{l}" class="text-gray-500 hover:text-brand-600 transition">{"About" if "about" in l else "Contact" if "contact" in l else "Privacy Policy" if "privacy" in l else "Terms" if "terms" in l else l}</a>'
        for l in cfg['footer_links']
    )

    # Build OG fields
    og_title = f"{data['title_short']} - {cfg['site_name']}"
    og_desc = data['meta_desc'][:155]
    file_name = f"article-{topic_num}.html"
    url = f"https://{cfg['domain']}/{file_name}"
    title_full = f"{data['title_short']} - {cfg['site_name']}"

    # Insert Unsplash image
    img_html = f'<img src="{data.get("unsplash_url", "")}" alt="{data.get("unsplash_alt", topic)}" class="rounded-2xl mb-10 w-full">'
    body = data['article_body']
    # Insert image after first H2 or at beginning
    if '<h2>' in body:
        first_h2 = body.index('<h2>')
        body = body[:first_h2] + img_html + '\n' + body[first_h2:]
    else:
        body = img_html + '\n' + body

    html = HTML_TEMPLATE.format(
        meta_desc=data['meta_desc'],
        keywords=data['keywords'],
        og_title=og_title,
        og_desc=og_desc,
        og_url=url,
        site_name=cfg['site_name'],
        title=title_full,
        canonical_url=url,
        p50=cfg['p50'], p100=cfg['p100'], p200=cfg['p200'],
        p400=cfg['p400'], p500=cfg['p500'], p600=cfg['p600'],
        p700=cfg['p700'], p800=cfg['p800'],
        brand_color=cfg['brand_color'],
        brand_bg=cfg['brand_bg'],
        title_short=data['title_short'],
        date=date_str,
        date_formatted=date_fmt,
        read_time=data.get('read_time', 7),
        article_body=body,
        tag_pills=tag_html,
        related_articles=related,
        footer_links=footer_html,
        year=today.year,
    )
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: py shared/batch_articles.py <site> [start_num] [count]")
        for s in SITE_CONFIG:
            print(f"  {s}")
        sys.exit(1)

    site = sys.argv[1]
    start_num = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if site not in SITE_CONFIG:
        print(f"Unknown site: {site}")
        sys.exit(1)

    topics = SITE_TOPICS.get(site, [])
    cfg = SITE_CONFIG[site]
    site_dir = ROOT / site

    # Get existing article titles for dedup
    existing = []
    for f in sorted(site_dir.glob('article-*.html')):
        import re
        html = f.read_text(encoding='utf-8')
        m = re.search(r'<title>([^<]+)</title>', html)
        if m:
            existing.append(m.group(1))

    print(f"Site: {site} ({cfg['site_name']})")
    print(f"Existing articles: {len(existing)}")
    print(f"Topics available: {len(topics)}")
    print(f"Generating {count} articles starting at #{start_num}")
    print("---")

    from anthropic import Anthropic
    client = Anthropic(api_key=API_KEY, base_url=BASE_URL)

    failed = []
    for i, topic in enumerate(topics[:count]):
        num = start_num + i
        file_name = f"article-{num}.html"
        file_path = site_dir / file_name

        if file_path.exists():
            print(f"  [{num}] SKIP — already exists")
            continue

        success = False
        for attempt in range(3):
            if attempt > 0:
                wait = 10 * attempt
                print(f"  [{num}] Retry {attempt+1}/3 (waiting {wait}s)...", end=' ', flush=True)
                time.sleep(wait)
            else:
                print(f"  [{num}] {topic[:55]}...", end=' ', flush=True)

            try:
                prompt = build_prompt(site, topic, num, '\n'.join(existing[-10:]))
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=6000,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}],
                )
                text_parts = []
                for block in resp.content:
                    if hasattr(block, 'text'):
                        text_parts.append(block.text)
                text = ''.join(text_parts).strip()

                if not text:
                    print("EMPTY", end='', flush=True)
                    continue

                # Extract JSON with balanced brace approach
                data = None
                json_start = text.find('{')
                if json_start >= 0:
                    depth = 0
                    for j, ch in enumerate(text[json_start:], json_start):
                        if ch == '{': depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                try:
                                    data = json.loads(text[json_start:j + 1])
                                except json.JSONDecodeError:
                                    pass
                                break

                if data:
                    html = build_html(site, num, topic, data)
                    file_path.write_text(html, encoding='utf-8')
                    existing.append(data.get('title_short', topic))
                    print(f"OK ({len(data.get('article_body',''))} chars)", flush=True)
                    success = True
                    break
                else:
                    print(f"JSON_FAIL({len(text)}c)", end='', flush=True)
            except Exception as e:
                print(f"ERR:{type(e).__name__}", end='', flush=True)

        if not success:
            failed.append((num, topic))
            print(f" -> FAILED after 3 attempts")

        time.sleep(4)  # Rate limit between articles

    if failed:
        print(f"\nFAILED ({len(failed)}): {[f[0] for f in failed]}")

    print("---")
    print("Done.")


if __name__ == '__main__':
    main()
