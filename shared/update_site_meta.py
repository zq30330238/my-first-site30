"""Update sitemap.xml, index.html article grid, and robots.txt for all sub-sites."""
import re, sys
from pathlib import Path
from datetime import date

ROOT = Path(r'd:\AI网站文件夹')
SITES = ['sub-healthy', 'sub-pets', 'sub-home', 'sub-finance', 'sub-tech', 'sub-travel']

SITE_INFO = {
    'sub-healthy': {'domain': 'healthy.jycsd.com', 'name': 'HealthyEats'},
    'sub-pets': {'domain': 'pets.jycsd.com', 'name': 'PetCareHub'},
    'sub-home': {'domain': 'home.jycsd.com', 'name': 'HomeJoy'},
    'sub-finance': {'domain': 'finance.jycsd.com', 'name': 'MoneyWise'},
    'sub-tech': {'domain': 'tech.jycsd.com', 'name': 'TechSift'},
    'sub-travel': {'domain': 'travel.jycsd.com', 'name': 'TripRoute'},
}

def extract_article_info(filepath):
    html = filepath.read_text(encoding='utf-8', errors='ignore')
    title_m = re.search(r'<title>([^<]+)</title>', html)
    desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
    h1_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    word_count = len(re.sub(r'<[^>]+>', ' ', html).split())
    read_time = max(1, word_count // 200)

    title = title_m.group(1) if title_m else filepath.stem
    desc = (desc_m.group(1) if desc_m else '')[:120]
    h1 = h1_m.group(1) if h1_m else title

    return {
        'filename': filepath.name,
        'title_full': title,
        'h1': h1,
        'desc': desc,
        'read_time': read_time,
    }


def update_sitemap(site_dir, info, articles):
    today = date.today().isoformat()
    urls = []
    static_pages = [
        ('index.html', '1.0'),
        ('about.html', '0.6'),
        ('contact.html', '0.6'),
        ('privacy-policy.html', '0.4'),
        ('terms.html', '0.4'),
        ('terms-of-service.html', '0.4'),
        ('cookie-policy.html', '0.4'),
    ]
    for page, prio in static_pages:
        if (site_dir / page).exists():
            urls.append(f'''  <url>
    <loc>https://{info['domain']}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{prio}</priority>
  </url>''')

    for art in articles:
        urls.append(f'''  <url>
    <loc>https://{info['domain']}/{art['filename']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''
    (site_dir / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    return len(urls)


def make_article_card(art):
    return f'''            <a href="{art['filename']}" class="article-card block bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100">
                <div class="h-48 bg-cover bg-center" style="background-image:url(https://images.unsplash.com/photo-{abs(hash(art['h1']))%9999}?w=400&h=250&fit=crop)"></div>
                <div class="p-5">
                    <h3 class="text-lg font-bold text-gray-900 mt-1 mb-2">{art['h1'][:75]}</h3>
                    <p class="text-gray-500 text-sm">{art['desc'][:100]}</p>
                    <div class="flex items-center gap-2 mt-4 text-xs text-gray-400">
                        <span>{date.today().strftime('%b %d, %Y')}</span><span>&middot;</span><span>{art['read_time']} min read</span>
                    </div>
                </div>
            </a>'''


def update_index(site_dir, articles):
    index_path = site_dir / 'index.html'
    if not index_path.exists():
        return
    html = index_path.read_text(encoding='utf-8', errors='ignore')

    # Find the article grid section: between <!-- Featured Articles --> and the next </div> after grid
    # Use a simpler approach: find the grid div and replace its content
    pattern = r'(<div class="grid[^"]*md:grid-cols-2 lg:grid-cols-3 gap-8">)\s*\n(.*?)(\s*\n\s*</div>\s*\n\s*</section>)'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        # Show latest 12 articles
        latest = articles[-12:] if len(articles) > 12 else articles
        cards = '\n\n'.join(make_article_card(a) for a in reversed(latest))
        new_grid = match.group(1) + '\n' + cards + match.group(3)
        new_html = html[:match.start()] + new_grid + html[match.end():]
        index_path.write_text(new_html, encoding='utf-8')
        return len(latest)
    return 0


def main():
    dry = '--dry-run' in sys.argv
    total_articles = 0

    for site in SITES:
        site_dir = ROOT / site
        info = SITE_INFO[site]
        arts = []
        for f in sorted(site_dir.glob('article-*.html'), key=lambda x: int(re.search(r'(\d+)', x.name).group(1))):
            arts.append(extract_article_info(f))

        print(f"\n{site}: {len(arts)} articles")

        if not dry:
            url_count = update_sitemap(site_dir, info, arts)
            card_count = update_index(site_dir, arts)
            print(f"  sitemap: {url_count} URLs")
            print(f"  index: {card_count} cards shown")
        else:
            print(f"  [DRY] would update sitemap + index")
        total_articles += len(arts)

    print(f"\nTotal: {total_articles} articles across {len(SITES)} sites")
    if dry:
        print("Dry run — remove --dry-run to apply changes")


if __name__ == '__main__':
    main()
