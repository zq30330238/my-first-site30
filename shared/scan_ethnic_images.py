"""Scan ethnic group pages to find missing images."""
import os, re

pages_dir = r'd:\AI网站文件夹\clothing-site\chinese\56-ethnic-groups'
img_re = re.compile(r'src="/images/([^"]+\.jpg)"')

for fname in sorted(os.listdir(pages_dir)):
    if fname == 'index.html' or not fname.endswith('.html'):
        continue
    path = os.path.join(pages_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    imgs = [m for m in img_re.findall(content) if 'tailwind' not in m]
    ethnic = fname.replace('.html', '')
    print(f'{ethnic}: {len(imgs)} imgs — {imgs}')
