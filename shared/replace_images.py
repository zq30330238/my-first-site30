"""Replace CSS gradient hero placeholders with real Unsplash images based on article keywords"""
import re
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['sub-healthy','sub-pets','sub-home','sub-finance','sub-tech','sub-travel']

count = 0
for d in DIRS:
    for f in sorted((ROOT / d).glob('article-*.html')):
        html = f.read_text(encoding='utf-8')
        if 'images.unsplash.com' in html or 'source.unsplash.com' in html:
            continue

        # Extract first keyword from meta keywords or tags
        kw_match = re.search(r'<meta name="keywords" content="([^"]+)"', html)
        if kw_match:
            keyword = kw_match.group(1).split(',')[0].strip().replace(' ', '-').lower()
        else:
            tags = re.findall(r'"([^"]*)"', html)
            keyword = d.replace('sub-', '')

        # Pattern 1: Tailwind gradient (any rounded/text size) + emoji
        pattern1 = r'<div class="[^"]*h-64[^"]*bg-gradient-to-br[^"]*flex items-center justify-center[^"]*mb-8">[^<]*</div>'
        # Pattern 2: Inline style gradient (with or without comment)
        pattern2 = r'(?:<!-- Gradient Placeholder Image -->\s*)?<div[^>]*style="background:\s*linear-gradient[^"]*"[^>]*>[^<]*</div>'
        old_div = re.search(pattern1, html) or re.search(pattern2, html)

        if not old_div:
            print(f'{d}/{f.name}: SKIP - no gradient placeholder found')
            continue

        img_tag = f'''<img
        src="https://source.unsplash.com/800x400/?{keyword}"
        alt="{keyword.replace('-', ' ').title()} - article hero image"
        class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"
        loading="lazy"
        width="800"
        height="400">'''

        html = html.replace(old_div.group(0), img_tag, 1)
        f.write_text(html, encoding='utf-8')
        count += 1
        print(f'{d}/{f.name}: {keyword}')

print(f'\nReplaced {count} images')
