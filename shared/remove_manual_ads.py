import os, re

def clean_manual_ads(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern 1: Remove ad-unit blocks (div.ad-unit containing ad-label + adsbygoogle + push)
    content = re.sub(
        r'<div class="ad-unit">\s*<span class="ad-label">Advertisement</span>\s*<ins class="adsbygoogle"[\s\S]*?</ins>\s*<script>\(adsbygoogle[\s\S]*?</script>\s*</div>\s*',
        '',
        content
    )

    # Pattern 2: Remove standalone ad-label + adsbygoogle + push
    content = re.sub(
        r'<div class="ad-label">Advertisement</div>\s*<ins class="adsbygoogle"[\s\S]*?</ins>\s*<script>\(adsbygoogle[\s\S]*?</script>\s*',
        '',
        content
    )

    # Pattern 3: Remove standalone adsbygoogle ins + push
    content = re.sub(
        r'<ins class="adsbygoogle"[\s\S]*?</ins>\s*<script>\(adsbygoogle[\s\S]*?</script>\s*',
        '',
        content
    )

    # Pattern 4: Remove ad-container placeholder divs (sub-site index/policy pages)
    content = re.sub(
        r'<div class="ad-container[^"]*">\s*Advertisement\s*</div>\s*',
        '',
        content
    )

    # Pattern 5: Remove inline Advertisement placeholders (game/anime detail pages like dragonball)
    content = re.sub(
        r'<div[^>]*class="[^"]*\bbg-bgSecondary\\30\b[^"]*"[^>]*>[\s\S]*?<span[^>]*class="[^"]*uppercase tracking-wider text-xs[^"]*"[^>]*>Advertisement</span>[\s\S]*?</div>\s*',
        '',
        content
    )

    # Pattern 6: Clean up CSS rules for .ad-unit, .ad-label, .ad-container
    content = re.sub(
        r'\.ad-unit\s*\{[^}]*\}\s*',
        '',
        content
    )
    content = re.sub(
        r'\.ad-label\s*\{[^}]*\}\s*',
        '',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


dirs = [
    'main-site', 'games-site', 'anime-site', 'dragonball-site',
    'fortnite-site', 'eldenring-site', 'minecraft-site',
    'valorant-site', 'lol-site', 'onepiece-site', 'naruto-site',
    'sub-healthy', 'sub-pets', 'sub-home', 'sub-finance', 'sub-tech', 'sub-travel'
]

base = 'd:/AI网站文件夹'
total = 0
modified = 0

for d in dirs:
    path = os.path.join(base, d)
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith('.html'):
                fp = os.path.join(root, f)
                total += 1
                if clean_manual_ads(fp):
                    modified += 1
                    print(f'  MODIFIED: {os.path.relpath(fp, base)}')

print(f'\nTotal HTML files scanned: {total}')
print(f'Files modified (ads removed): {modified}')
