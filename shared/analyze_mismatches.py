"""Categorize visual audit mismatches"""
import json, sys
from collections import Counter

r = json.load(open('visual_audit_report.json','r',encoding='utf-8'))

blogs, chars, indexes, other = [], [], [], []

for m in r['mismatches']:
    page = m['page'].replace('\\', '/')
    if '/blog/' in page or page.startswith('blog/'):
        blogs.append(m)
    elif '/characters/' in page or '/bosses/' in page or '/agents/' in page or '/quests/' in page:
        chars.append(m)
    elif page.endswith('/index.html') or page == 'index.html':
        indexes.append(m)
    else:
        other.append(m)

print(f'=== VISUAL AUDIT RESULTS ===')
print(f'Verified: {r["verified"]}/{r["total"]}, Errors: {r["errors"]}')
print(f'Total mismatches: {len(r["mismatches"])}')
print(f'  Blog pages: {len(blogs)} (default images, known issue)')
print(f'  Character/boss/agent pages: {len(chars)}')
print(f'  Index pages: {len(indexes)}')
print(f'  Other: {len(other)}')
print()

if chars:
    char_sites = Counter(m['site'] for m in chars)
    print('Character page mismatches by site:')
    for site, count in char_sites.most_common():
        print(f'  {site}: {count}')
    print()
    print('Character details:')
    for m in chars:
        img = m['image'].split('/')[-1] if m['image'] else 'N/A'
        print(f'  {m["site"]}/{m["page"]} -> {img}')

if indexes:
    print(f'\nIndex mismatches:')
    for m in indexes:
        print(f'  {m["site"]}/{m["page"]} -> {m["image"]}')

if other:
    print(f'\nOther mismatches:')
    for m in other:
        print(f'  {m["site"]}/{m["page"]} -> {m["image"]}')

# Check which sites are affected
all_sites = Counter(m['site'] for m in r['mismatches'])
print(f'\nAffected sites:')
for site, count in all_sites.most_common():
    print(f'  {site}: {count} pages')
