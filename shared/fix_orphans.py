"""Fix orphan articles: update sidebar Recent Posts in all pages to include all articles."""
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

def get_article_list(site_dir):
    """Return sorted list of (filename, title) for all article-*.html in site."""
    articles = []
    for f in sorted(site_dir.glob('article-*.html'), key=lambda x: int(re.search(r'article-(\d+)', x.name).group(1)), reverse=True):
        html = f.read_text(encoding='utf-8')
        title_m = re.search(r'<title>([^<]+)</title>', html)
        title = title_m.group(1).strip() if title_m else f.name
        # Strip site suffix from title (e.g., " - PetCare Hub")
        title = re.sub(r'\s*[-–|]\s*[^-–|]+$', '', title).strip()
        articles.append((f.name, title))
    return articles

def rebuild_sidebar(articles, max_items=12):
    """Build the Recent Posts sidebar HTML."""
    items = []
    for filename, title in articles[:max_items]:
        items.append(f'<li><a href="{filename}" class="text-sm text-stone-600 hover:text-brand-600">{title}</a></li>')
    return '\n'.join(items)

def fix_sidebar_in_page(html, new_sidebar_items):
    """Replace the Recent Posts <ul> content with the new list."""
    # The sidebar Recent Posts is a <ul class="space-y-3"> inside <aside>
    # Pattern: <ul class="space-y-3"> ... </ul> within the aside
    pattern = r'(<aside[^>]*>.*?<ul class="space-y-3">)(.*?)(</ul>)'
    def replacer(m):
        return m.group(1) + '\n' + new_sidebar_items + '\n' + m.group(3)
    return re.sub(pattern, replacer, html, count=1, flags=re.DOTALL)

def main():
    fixed = 0
    for d in DIRS:
        site_dir = ROOT / d
        if not site_dir.exists():
            continue

        articles = get_article_list(site_dir)
        if not articles:
            continue

        new_items = rebuild_sidebar(articles)
        print(f'{d}: {len(articles)} articles')

        # Fix all HTML files with sidebars
        for f in site_dir.glob('*.html'):
            html = f.read_text(encoding='utf-8')
            if '<aside' not in html or 'Recent Posts' not in html:
                continue
            new_html = fix_sidebar_in_page(html, new_items)
            if new_html != html:
                f.write_text(new_html, encoding='utf-8')
                fixed += 1
                print(f'  Updated {f.name}')

    print(f'\nFixed {fixed} pages across all sites.')

if __name__ == '__main__':
    main()
