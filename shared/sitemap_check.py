"""Sitemap validator — check all pages are listed in sitemap.xml"""
import re
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

def check():
    issues = []
    for d in DIRS:
        sitemap = ROOT / d / 'sitemap.xml'
        if not sitemap.exists():
            issues.append(f'{d}: Missing sitemap.xml')
            continue
        content = sitemap.read_text(encoding='utf-8')
        urls = re.findall(r'<loc>([^<]+)</loc>', content)
        html_files = sorted([f.name for f in (ROOT / d).glob('*.html')])

        for hf in html_files:
            found = False
            for u in urls:
                if hf in u:
                    found = True
                    break
                if hf == 'index.html' and u.rstrip('/').endswith('.com'):
                    found = True
                    break
            if not found:
                issues.append(f'{d}: {hf} not in sitemap')

        for url in urls:
            name = url.rstrip('/').rsplit('/', 1)[-1]
            if name and not name.endswith('.html'):
                name += '.html'
            if name and name not in html_files and '.html' in url:
                pass  # URL might use clean URLs without .html

        count_urls = len([u for u in urls if '.html' in u or any(h in u for h in html_files)])
        print(f'{d}: {len(html_files)} html files, {count_urls} in sitemap')

    if issues:
        print(f'\n{len(issues)} sitemap issues:')
        for i in issues:
            print(f'  - {i}')
    else:
        print('\nAll sitemaps are complete.')

if __name__ == '__main__':
    check()
