"""Unified site health check — SEO + links + content + sitemap in one pass"""
import re, sys, json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def count_words(text):
    return len(strip_html(text).split())

def check_seo(html):
    issues = []
    title_m = re.search(r'<title>([^<]+)</title>', html)
    title = title_m.group(1).strip() if title_m else ''
    desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
    desc = desc_m.group(1) if desc_m else ''
    canonical = 'rel="canonical"' in html
    og_title = 'og:title' in html
    og_desc = 'og:description' in html
    schema = 'application/ld+json' in html

    if not title: issues.append('Missing title')
    elif len(title) < 50: issues.append(f'Title too short ({len(title)} chars)')
    elif len(title) > 60: issues.append(f'Title too long ({len(title)} chars)')
    if not desc: issues.append('Missing meta description')
    elif len(desc) < 120: issues.append(f'Desc too short ({len(desc)} chars)')
    elif len(desc) > 155: issues.append(f'Desc too long ({len(desc)} chars)')
    if not canonical: issues.append('Missing canonical')
    if not og_title: issues.append('Missing og:title')
    if not og_desc: issues.append('Missing og:description')
    if not schema: issues.append('Missing JSON-LD Schema')
    return issues

def check_content(html):
    issues = []
    text = strip_html(html)
    words = len(text.split())
    h2s = len(re.findall(r'<h2[^>]*>', html))
    adsense = 'adsbygoogle' in html
    if words < 800: issues.append(f'Too short: {words} words')
    if h2s < 2: issues.append(f'Only {h2s} H2 headings')
    if not adsense: issues.append('No AdSense units')
    return issues

def check_links():
    dead = []
    all_pages = set()
    for d in DIRS:
        for f in (ROOT / d).glob('*.html'):
            all_pages.add(f'{d}/{f.name}')
    orphan_refs = defaultdict(int)
    for d in DIRS:
        for f in (ROOT / d).glob('*.html'):
            html = f.read_text(encoding='utf-8')
            for href in re.findall(r'href="([^"]+)"', html):
                if href.startswith('http') or href.startswith('#'):
                    continue
                if not href.endswith('.html'):
                    continue
                if not (ROOT / d / href).exists():
                    dead.append(f'{d}/{f.name} -> {href}')
                orphan_refs[f'{d}/{href}'] += 1
    orphans = []
    for d in DIRS:
        for a in (ROOT / d).glob('article-*.html'):
            key = f'{d}/{a.name}'
            if orphan_refs[key] == 0:
                orphans.append(key)
    return dead, orphans

def check_sitemap():
    issues = []
    for d in DIRS:
        sitemap = ROOT / d / 'sitemap.xml'
        if not sitemap.exists():
            issues.append(f'{d}: Missing sitemap.xml')
            continue
        content = sitemap.read_text(encoding='utf-8')
        urls = re.findall(r'<loc>([^<]+)</loc>', content)
        html_files = [f.name for f in (ROOT / d).glob('*.html')]
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
    return issues

def check_compliance():
    issues = []
    for d in DIRS:
        r = ROOT / d / 'robots.txt'
        a = ROOT / d / 'ads.txt'
        if not r.exists(): issues.append(f'{d}: Missing robots.txt')
        if not a.exists(): issues.append(f'{d}: Missing ads.txt')
    return issues

def main():
    total = seo_ok = content_ok = 0
    all_issues = defaultdict(list)

    for d in DIRS:
        for f in sorted((ROOT / d).glob('*.html')):
            total += 1
            html = f.read_text(encoding='utf-8')
            seo = check_seo(html)
            if not seo: seo_ok += 1
            else: all_issues[str(f.relative_to(ROOT))] += seo
            if 'article-' in f.name:
                cont = check_content(html)
                if not cont: content_ok += 1
                else: all_issues[str(f.relative_to(ROOT))] += cont

    dead, orphans = check_links()
    sm_issues = check_sitemap()
    comp_issues = check_compliance()

    article_count = sum(1 for d in DIRS for f in (ROOT/d).glob('article-*.html'))

    lines = []
    lines.append('# Site Health Report')
    lines.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append('')
    lines.append('## Summary')
    lines.append(f'| Check | Status |')
    lines.append(f'|-------|--------|')
    lines.append(f'| SEO | {seo_ok}/{total} |')
    lines.append(f'| Content | {content_ok}/{article_count} |')
    lines.append(f'| Dead Links | {len(dead)} |')
    lines.append(f'| Orphans | {len(orphans)} |')
    lines.append(f'| Sitemap | {len(sm_issues)} issues |')
    lines.append(f'| Compliance | {len(comp_issues)} issues |')

    if dead:
        lines.append('')
        lines.append('## Dead Links')
        for dl in dead:
            lines.append(f'- {dl}')
    if orphans:
        lines.append('')
        lines.append('## Orphan Pages')
        for o in orphans:
            lines.append(f'- {o}')
    if sm_issues:
        lines.append('')
        lines.append('## Sitemap Issues')
        for s in sm_issues:
            lines.append(f'- {s}')
    if comp_issues:
        lines.append('')
        lines.append('## Compliance Issues')
        for c in comp_issues:
            lines.append(f'- {c}')
    if all_issues:
        lines.append('')
        lines.append('## Page Issues')
        for path, issues in sorted(all_issues.items()):
            lines.append(f'- **{path}**: {", ".join(issues)}')

    report = '\n'.join(lines)
    out = ROOT / 'shared' / 'site-health-report.md'
    out.write_text(report, encoding='utf-8')
    print(report)
    print(f'\nReport saved to {out}')

if __name__ == '__main__':
    main()
