"""Unified site health check — SEO + links + content + sitemap in one pass.
Default: incremental (git-diff changed files only). Use --full for all pages."""
import re, sys, json, subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]
STATE_FILE = ROOT / 'shared' / '.health-state.json'

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
    if 'G-GGNWR1X1GV' not in html: issues.append('Missing GA4 tracking')
    if 'ca-pub-2595917642864488' not in html: issues.append('Missing AdSense')
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

def get_changed_files():
    """Return list of changed/new HTML files from git diff"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10
        )
        changed = [l.strip().replace('\\', '/') for l in result.stdout.split('\n') if l.strip().endswith('.html')]
        result2 = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard'],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10
        )
        untracked = [l.strip().replace('\\', '/') for l in result2.stdout.split('\n') if l.strip().endswith('.html')]
        return changed + untracked
    except:
        return None

def save_state(seo_ok, total, content_ok, article_count, dead, orphans, sm_issues, comp_issues):
    state = {
        'last_check': datetime.now().isoformat(),
        'seo_score': f'{seo_ok}/{total}',
        'content_score': f'{content_ok}/{article_count}',
        'dead_links': len(dead),
        'orphans': len(orphans),
        'sitemap_issues': len(sm_issues),
        'compliance_issues': len(comp_issues),
        'total_pages': total
    }
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding='utf-8')

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return None

def main():
    full_scan = '--full' in sys.argv or '-f' in sys.argv
    changed_files = None if full_scan else get_changed_files()

    # If incremental and no changes, skip
    if not full_scan and changed_files is not None and len(changed_files) == 0:
        prev = load_state()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'# Site Health — {ts}')
        print('No changed pages since last check. Skipping.')
        if prev:
            print(f"Last full score: SEO {prev['seo_score']}, Content {prev['content_score']}")
        return

    total = seo_ok = content_ok = 0
    all_issues = defaultdict(list)

    for d in DIRS:
        for f in sorted((ROOT / d).glob('*.html')):
            rel = str(f.relative_to(ROOT)).replace('\\', '/')
            if not full_scan and changed_files is not None and rel not in changed_files:
                continue
            total += 1
            html = f.read_text(encoding='utf-8')
            seo = check_seo(html)
            if not seo: seo_ok += 1
            else: all_issues[rel] += seo
            if 'article-' in f.name:
                cont = check_content(html)
                if not cont: content_ok += 1
                else: all_issues[rel] += cont

    # If no pages were checked, nothing to report
    if total == 0:
        print('No HTML pages to check (no changes detected).')
        return

    # Full scan fill-in: re-check everything for SEO/content counts
    if full_scan:
        seo_ok = content_ok = total = 0
        all_issues.clear()
        for d in DIRS:
            for f in sorted((ROOT / d).glob('*.html')):
                total += 1
                rel = str(f.relative_to(ROOT)).replace('\\', '/')
                html = f.read_text(encoding='utf-8')
                seo = check_seo(html)
                if not seo: seo_ok += 1
                else: all_issues[rel] += seo
                if 'article-' in f.name:
                    cont = check_content(html)
                    if not cont: content_ok += 1
                    else: all_issues[rel] += cont

    dead, orphans = check_links()
    sm_issues = check_sitemap()
    comp_issues = check_compliance()
    article_count = sum(1 for d in DIRS for f in (ROOT/d).glob('article-*.html'))

    lines = []
    lines.append('# Site Health Report')
    mode = 'FULL' if full_scan else 'INCREMENTAL'
    lines.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ({mode} scan)')
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
        for dl in dead: lines.append(f'- {dl}')
    if orphans:
        lines.append('')
        lines.append('## Orphan Pages')
        for o in orphans: lines.append(f'- {o}')
    if sm_issues:
        lines.append('')
        lines.append('## Sitemap Issues')
        for s in sm_issues: lines.append(f'- {s}')
    if comp_issues:
        lines.append('')
        lines.append('## Compliance Issues')
        for c in comp_issues: lines.append(f'- {c}')
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

    save_state(seo_ok, total, content_ok, article_count, dead, orphans, sm_issues, comp_issues)

if __name__ == '__main__':
    main()
