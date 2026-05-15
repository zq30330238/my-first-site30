"""Trim overly long meta descriptions to 120-155 chars at sentence boundary"""
import re, os
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
DIRS = ['main-site', 'sub-healthy', 'sub-pets', 'sub-home', 'sub-finance', 'sub-tech', 'sub-travel']

def trim_desc(content, max_len=155):
    """Trim description to max_len at nearest sentence boundary"""
    content = content.strip()
    if len(content) <= max_len:
        return content
    truncated = content[:max_len]
    for sep in ['. ', '! ', '? ', '."', '!"', '?"']:
        idx = truncated.rfind(sep)
        if idx > 80 and idx + len(sep) <= max_len:
            return truncated[:idx + len(sep)].strip()
    return truncated.rsplit(' ', 1)[0].strip()

fixed = 0
for d in DIRS:
    for html_file in (ROOT / d).glob('*.html'):
        content = html_file.read_text(encoding='utf-8')
        match = re.search(r'<meta name="description" content="([^"]+)"', content)
        if not match:
            continue
        old_desc = match.group(1)
        new_desc = trim_desc(old_desc)
        if new_desc != old_desc and len(new_desc) >= 120:
            content = content.replace(
                f'<meta name="description" content="{old_desc}"',
                f'<meta name="description" content="{new_desc}"'
            )
            html_file.write_text(content, encoding='utf-8')
            print(f'  {d}/{html_file.name}: {len(old_desc)} -> {len(new_desc)} chars')
            fixed += 1

print(f'\nFixed {fixed} descriptions')
