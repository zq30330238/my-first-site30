import os
import re
import json
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r'd:\AI网站文件夹')
CONFIG_PATH = ROOT / 'shared' / 'site_config.json'
EXCLUDE_DIRS = {'images', 'assets', 'css', 'js'}


def load_config():
    with open(CONFIG_PATH, encoding='utf-8') as f:
        return json.load(f)


def get_site_info(config, site_dir):
    site_path = ROOT / site_dir
    if not site_path.is_dir():
        return None, None
    for s in config['sites']:
        if s['dir'] == site_dir:
            return site_path, s['domain']
    return None, None


def scan_html_files(site_path):
    for root, dirs, files in os.walk(site_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith('.html'):
                full = Path(root) / f
                rel = str(full.relative_to(site_path)).replace('\\', '/')
                yield rel, full


def determine_priority(rel_path):
    name = rel_path.rsplit('/', 1)[-1]
    is_root = '/' not in rel_path

    if name == 'index.html':
        return ('1.0', 'daily') if is_root else ('0.9', 'weekly')
    if name.startswith('article-'):
        return '0.8', 'weekly'
    if name in ('about.html', 'contact.html', 'privacy-policy.html', 'terms.html', 'cookie-policy.html'):
        return '0.5', 'monthly'
    if name == 'sitemap.html':
        return '0.3', 'monthly'
    return '0.7', 'monthly'


def rel_path_to_url(rel_path):
    if rel_path.endswith('index.html'):
        return rel_path[:-len('index.html')]
    return rel_path[:-len('.html')]


def generate_url_xml(rel_path, lastmod, domain):
    priority, changefreq = determine_priority(rel_path)
    url_path = rel_path_to_url(rel_path)
    loc = f'https://{domain}/{url_path}'
    return f'''  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>'''


def parse_existing_urls(sitemap_path):
    if not sitemap_path.exists():
        return set()
    content = sitemap_path.read_text(encoding='utf-8')
    return set(re.findall(r'<loc>([^<]+)</loc>', content))


def compare_and_print(old_urls, new_urls, title):
    added = sorted(new_urls - old_urls)
    removed = sorted(old_urls - new_urls)
    print(f'\n  {title}:')
    print(f'    Old: {len(old_urls)} | New: {len(new_urls)} | Diff: {len(new_urls) - len(old_urls):+d}')
    if added:
        print(f'    Added ({len(added)}):')
        for u in added:
            print(f'      + {u}')
    if removed:
        print(f'    Removed ({len(removed)}):')
        for u in removed:
            print(f'      - {u}')
    if not added and not removed:
        print('    No changes.')
    return not added and not removed


def write_sitemap(site_path, domain, url_entries, dry_run=False):
    sitemap_path = site_path / 'sitemap.xml'
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml_parts.extend(url_entries)
    xml_parts.append('</urlset>')
    xml = '\n'.join(xml_parts) + '\n'

    if dry_run:
        return

    if sitemap_path.exists():
        shutil.copy2(sitemap_path, sitemap_path.with_suffix('.xml.bak'))

    sitemap_path.write_text(xml, encoding='utf-8')
    print(f'\n  Written: {sitemap_path}')


def update_robots(site_path, domain, dry_run=False):
    robots_path = site_path / 'robots.txt'
    sitemap_url = f'https://{domain}/sitemap.xml'
    sitemap_line = f'Sitemap: {sitemap_url}'

    if not robots_path.exists():
        if not dry_run:
            robots_path.write_text(
                f'User-agent: *\nAllow: /\nDisallow: /cdn-cgi/\n{sitemap_line}\n',
                encoding='utf-8'
            )
            print(f'\n  Created robots.txt with Sitemap reference')
        else:
            print(f'\n  robots.txt missing, would create with Sitemap: {sitemap_url}')
        return

    content = robots_path.read_text(encoding='utf-8')
    if sitemap_line in content:
        print(f'\n  robots.txt Sitemap OK')
        return

    if re.search(r'^Sitemap:', content, re.MULTILINE):
        new_content = re.sub(
            r'^Sitemap:.*$', sitemap_line,
            content, count=1, flags=re.MULTILINE
        )
        if not dry_run:
            robots_path.write_text(new_content, encoding='utf-8')
            print(f'\n  Updated robots.txt Sitemap -> {sitemap_url}')
        else:
            print(f'\n  Would update robots.txt Sitemap -> {sitemap_url}')
    else:
        if not content.endswith('\n'):
            content += '\n'
        content += sitemap_line + '\n'
        if not dry_run:
            robots_path.write_text(content, encoding='utf-8')
            print(f'\n  Appended Sitemap to robots.txt -> {sitemap_url}')
        else:
            print(f'\n  Would append Sitemap to robots.txt -> {sitemap_url}')


def process_site(site_dir, dry_run=False):
    config = load_config()
    site_path, domain = get_site_info(config, site_dir)
    if site_path is None:
        print(f'ERROR: Directory not found for "{site_dir}"')
        return False
    if domain is None:
        print(f'ERROR: Domain not found for "{site_dir}" in site_config.json')
        return False

    print(f'\n{"=" * 60}')
    print(f'Site: {site_dir} -> {domain}')
    print(f'Path: {site_path}')
    print(f'{"=" * 60}')

    html_files = sorted(scan_html_files(site_path), key=lambda x: x[0])
    print(f'\n  Found {len(html_files)} HTML files')

    url_entries = []
    new_urls = set()

    for rel_path, full_path in html_files:
        mtime = os.path.getmtime(full_path)
        lastmod = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime('%Y-%m-%d')
        entry = generate_url_xml(rel_path, lastmod, domain)
        url_entries.append(entry)
        url_path = rel_path_to_url(rel_path)
        new_urls.add(f'https://{domain}/{url_path}')

    sitemap_path = site_path / 'sitemap.xml'
    old_urls = parse_existing_urls(sitemap_path)

    unchanged = compare_and_print(old_urls, new_urls, 'Sitemap Comparison')

    if dry_run:
        print(f'\n  [DRY RUN] No files written.')
        return unchanged

    write_sitemap(site_path, domain, url_entries)
    update_robots(site_path, domain)

    return unchanged


def main():
    parser = argparse.ArgumentParser(
        description='Regenerate sitemap.xml from actual HTML files on disk.'
    )
    parser.add_argument('site_dir', nargs='?',
                        help='Site directory name (e.g. sub-healthy, aot-site)')
    parser.add_argument('--all', action='store_true',
                        help='Process all sites in site_config.json')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show diff only, do not write files')

    args = parser.parse_args()

    if args.all:
        config = load_config()
        results = {}
        for s in config['sites']:
            try:
                ok = process_site(s['dir'], dry_run=args.dry_run)
                results[s['dir']] = 'OK' if ok else 'CHANGED'
            except Exception as e:
                print(f'\n  ERROR processing {s["dir"]}: {e}')
                results[s['dir']] = f'ERROR'

        print(f'\n{"=" * 60}')
        print('SUMMARY')
        print(f'{"=" * 60}')
        for site, status in results.items():
            print(f'  {site}: {status}')
        ok_count = sum(1 for v in results.values() if v == 'OK')
        print(f'\n  {ok_count}/{len(results)} sites unchanged')

    elif args.site_dir:
        process_site(args.site_dir, dry_run=args.dry_run)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
