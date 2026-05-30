"""List all confirmed mismatches with key details"""
import json

r = json.load(open('d:/AI网站文件夹/visual_audit_verified.json', 'r', encoding='utf-8'))
confirmed = r['confirmed']

# Group by site
from collections import defaultdict
by_site = defaultdict(list)
for m in confirmed:
    by_site[m['site']].append(m)

for site, items in sorted(by_site.items()):
    print(f"\n=== {site} ({len(items)}) ===")
    for m in items:
        page = m['page'].replace('\\', '/')
        img = m['image'].split('/')[-1] if m['image'] else 'N/A'
        title_short = m['title'].split(' | ')[0].split(' — ')[0].strip()
        print(f"  {page}")
        print(f"    Title: {title_short}  Image: {img}  Reason: {m['reason']}")
