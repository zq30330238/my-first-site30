"""Update index.html and sitemap.xml for all sub-sites after article generation.
Reads existing articles, generates updated index pages and sitemaps.
"""
import re, sys
from pathlib import Path
from datetime import date

ROOT = Path(r'd:\AI网站文件夹')
SITES = ['sub-healthy', 'sub-pets', 'sub-home', 'sub-finance', 'sub-tech', 'sub-travel']

SITE_INFO = {
    'sub-healthy': {'domain': 'healthy.jycsd.com', 'name': 'HealthyEats', 'desc': 'Evidence-based healthy eating advice'},
    'sub-pets': {'domain': 'pets.jycsd.com', 'name': 'PetCareHub', 'desc': 'Expert pet care tips and guides'},
    'sub-home': {'domain': 'home.jycsd.com', 'name': 'HomeJoy', 'desc': 'DIY home improvement and gardening'},
    'sub-finance': {'domain': 'finance.jycsd.com', 'name': 'MoneyWise', 'desc': 'Personal finance made simple'},
    'sub-tech': {'domain': 'tech.jycsd.com', 'name': 'TechSift', 'desc': 'Tech reviews and digital guides'},
    'sub-travel': {'domain': 'travel.jycsd.com', 'name': 'TripRoute', 'desc': 'Budget travel tips and destination guides'},
}


def get_articles(site_dir):
    articles = []
    for f in sorted(site_dir.glob('article-*.html'), key=lambda x: int(re.search(r'(\d+)', x.name).group(1))):
        html = f.read_text(encoding='utf-8', errors='ignore')
        title_m = re.search(r'<title>([^<]+)</title>', html)
        desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
        title = title_m.group(1).strip() if title_m else f.name
        desc = desc_m.group(1)[:120] if desc_m else ''
        articles.append((f.name, title, desc))
    return articles


def update_sitemap(site_dir, info, articles):
    """Generate sitemap.xml for a site"""
    today = date.today().isoformat()
    urls = []
    # Static pages
    for page in ['index.html', 'about.html', 'contact.html', 'privacy-policy.html', 'terms.html']:
        urls.append(f'''  <url>
    <loc>https://{info['domain']}/{page}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{'1.0' if page == 'index.html' else '0.5'}</priority>
  </url>''')

    # Article pages
    for fname, title, desc in articles:
        urls.append(f'''  <url>
    <loc>https://{info['domain']}/{fname}</loc>
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


def main():
    dry = '--dry-run' in sys.argv
    for site in SITES:
        site_dir = ROOT / site
        info = SITE_INFO[site]
        articles = get_articles(site_dir)
        print(f"{site}: {len(articles)} articles")

        url_count = update_sitemap(site_dir, info, articles)
        if not dry:
            print(f"  sitemap.xml updated ({url_count} URLs)")
        else:
            print(f"  [DRY] sitemap.xml would have {url_count} URLs")

    if dry:
        print("\nDry run — use without --dry-run to apply changes")


if __name__ == '__main__':
    main()
