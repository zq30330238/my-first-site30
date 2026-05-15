"""Article quality checker — word count, structure, Schema, AdSense"""
import re, sys
from pathlib import Path

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def count_words(text):
    return len(strip_html(text).split())

def check_file(path):
    html = Path(path).read_text(encoding='utf-8')
    text = strip_html(html)
    words = len(text.split())
    h2s = len(re.findall(r'<h2[^>]*>', html))
    has_schema = 'application/ld+json' in html
    has_adsense = 'adsbygoogle' in html

    status = '+'
    issues = []
    if words < 800: status = 'X'; issues.append(f'Too short: {words} words')
    elif words > 2000: issues.append(f'Long: {words} words')
    if h2s < 2: issues.append(f'Only {h2s} H2 headings')
    if not has_schema: issues.append('No JSON-LD Schema')
    if not has_adsense: issues.append('No AdSense units')

    return {
        'file': str(Path(path).name),
        'words': words,
        'h2s': h2s,
        'schema': has_schema,
        'adsense': has_adsense,
        'status': status,
        'issues': issues
    }

if __name__ == '__main__':
    ROOT = Path(r'd:\AI网站文件夹')
    DIRS = ['main-site'] + [f'sub-{s}' for s in ['healthy','pets','home','finance','tech','travel']]

    if len(sys.argv) > 1:
        result = check_file(sys.argv[1])
        print(f"{result['file']}: {result['words']} words, {result['h2s']} H2s, schema={result['schema']}, adsense={result['adsense']}")
        for i in result['issues']:
            print(f'  - {i}')
    else:
        total = ok = 0
        for d in DIRS:
            for f in sorted((ROOT / d).glob('article-*.html')):
                total += 1
                r = check_file(f)
                if r['status'] == '+':
                    ok += 1
                else:
                    print(f'{d}/{r["file"]}: {r["words"]}w {", ".join(r["issues"])}')
        print(f'\n{ok}/{total} articles pass quality check')
