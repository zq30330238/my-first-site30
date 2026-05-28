"""Audit all 33 sites for missing and mismatched images."""
import os, json, re
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
img_re = re.compile(r'src="(/images/[^"]+)"')
alt_re = re.compile(r'alt="([^"]*)"')

with open(ROOT / 'shared' / 'site_config.json', encoding='utf-8') as f:
    config = json.load(f)

total_broken = 0
total_missing = 0
results = []

for site in config['sites']:
    site_dir = ROOT / site['dir']
    if not site_dir.is_dir():
        continue

    broken_refs = []
    missing_img_tags = []

    for fpath in site_dir.rglob('*.html'):
        if fpath.parent.name.startswith('.'):
            continue
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        img_refs = img_re.findall(content)
        for ref in img_refs:
            if 'tailwind' in ref or 'google' in ref or 'googletag' in ref:
                continue
            img_path = site_dir / ref.lstrip('/')
            if not img_path.exists():
                broken_refs.append({
                    'page': str(fpath.relative_to(site_dir)),
                    'missing': ref
                })
                print(f'{site["dir"]}/{fpath.relative_to(site_dir)} missing: {ref}')

        if not img_refs:
            missing_img_tags.append(str(fpath.relative_to(site_dir)))

    if broken_refs or missing_img_tags:
        results.append({
            'site': site['dir'],
            'broken_refs': len(broken_refs),
            'no_img_pages': len(missing_img_tags),
            'details_broken': broken_refs[:5],
            'details_no_img': missing_img_tags[:3],
            'total_broken': len(broken_refs) + len(missing_img_tags)
        })
        total_broken += len(broken_refs)
        total_missing += len(missing_img_tags)

print('\n=== SUMMARY ===')
for r in sorted(results, key=lambda x: x['total_broken'], reverse=True):
    print(f"{r['site']}: {r['broken_refs']} broken refs, {r['no_img_pages']} no-img pages")
print(f'\nTotal: {total_broken} broken refs, {total_missing} no-img pages')
