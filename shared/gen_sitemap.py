"""Generate sitemap.xml with clean URLs (no .html extension).
Reads site directories from shared/site_config.json.
Usage: python shared/gen_sitemap.py [site_dir1 site_dir2 ...]
  No args = all sites in site_config.json.
"""
import os, json, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gen_sitemap(site_dir, domain):
    full_dir = os.path.join(ROOT, site_dir)
    if not os.path.isdir(full_dir):
        return f'{site_dir}: directory not found', 0

    base = f'https://{domain}/'
    urls = []
    for root, dirs, files in os.walk(full_dir):
        for f in files:
            if not f.endswith('.html'):
                continue
            rel = os.path.relpath(os.path.join(root, f), full_dir).replace('\\', '/')
            if rel == 'index.html':
                urls.append(base)
            elif rel.endswith('/index.html'):
                urls.append(base + rel[:-11] + '/')
            else:
                urls.append(base + rel[:-5])

    urls = sorted(set(urls))
    if not urls:
        return f'{site_dir}: 0 HTML files', 0

    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f'  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>')
    lines.append('</urlset>')

    sitemap_path = os.path.join(full_dir, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as fw:
        fw.write('\n'.join(lines))
    return None, len(urls)


if __name__ == '__main__':
    config_path = os.path.join(ROOT, 'shared', 'site_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    target = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    total_urls = 0
    for site in config['sites']:
        d, domain = site['dir'], site['domain']
        if target and d not in target:
            continue
        err, n = gen_sitemap(d, domain)
        if err:
            print(err)
        else:
            print(f'{d}/sitemap.xml: {n} URLs')
            total_urls += n
    print(f'\nTotal: {total_urls} URLs across all sites')
