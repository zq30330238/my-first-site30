"""Link checker — find dead internal links across all pages"""
import re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

def find_links(html):
    """Extract all href links"""
    return re.findall(r'href="([^"]+)"', html)

def is_internal(href):
    return href.endswith('.html') or href.endswith('/') or '.jycsd.com' in href

def check():
    all_pages = set()
    for d in DIRS:
        for f in (ROOT / d).glob('*.html'):
            all_pages.add(f'{d}/{f.name}')

    dead_links = []
    orphan_candidates = defaultdict(int)

    for d in DIRS:
        for f in (ROOT / d).glob('*.html'):
            html = f.read_text(encoding='utf-8')
            links = find_links(html)
            for href in links:
                if href.startswith('http') or href.startswith('#'):
                    continue
                target = Path(d) / href
                target_str = str(target.resolve()) if target.is_absolute() else str(target)
                if not (ROOT / d / href).exists() and href.endswith('.html'):
                    dead_links.append(f'  {d}/{f.name} -> {href} (dead)')
                if href.endswith('.html'):
                    orphan_candidates[f'{d}/{href}'] += 1

    if dead_links:
        print(f'Dead links ({len(dead_links)}):')
        for dl in dead_links:
            print(dl)
    else:
        print('No dead links found.')

    for d in DIRS:
        articles = list((ROOT / d).glob('article-*.html'))
        for a in articles:
            key = f'{d}/{a.name}'
            if orphan_candidates[key] == 0:
                print(f'  ORPHAN: {key} (no other page links to it)')

    print(f'\nTotal pages: {len(all_pages)}')

if __name__ == '__main__':
    check()
