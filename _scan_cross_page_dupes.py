import os, re
from collections import defaultdict

SITE_DIRS = [d for d in os.listdir('.') if os.path.isdir(d) and d not in (
    'shared','__pycache__','_tmp_fix','backup-config','demos','global-architecture-redirect',
    'logs','temp','tmp','tmp_moto_banner','videos','workers','.git','.github','.claude',
    '.codex','.codegraph','.reasonix','.vercel','.vscode','.wrangler','.agents'
)]

total_overused = 0
for site in sorted(SITE_DIRS):
    img_pages = defaultdict(set)

    for root, dirs, files in os.walk(site):
        for f in files:
            if not f.endswith('.html'):
                continue
            fp = os.path.join(root, f)
            page_rel = os.path.relpath(fp, site).replace('\\', '/')
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            for m in re.finditer(r'(?:src|content|og:image|twitter:image|image)["\047=]\s*["\047]?(?:https?://[^/]+)?(?:/)?(images/[^"\047\s<>]+\.(?:jpg|jpeg|png|webp|gif|svg))', content, re.I):
                img = m.group(1).split('?')[0]
                if img.startswith('images/'):
                    img_pages[img].add(page_rel)

    overused = {img: pages for img, pages in img_pages.items() if len(pages) >= 5}
    if overused:
        total_overused += len(overused)
        print('')
        print('=== {} === ({} images on 5+ pages)'.format(site, len(overused)))
        for img, pages in sorted(overused.items(), key=lambda x: -len(x[1]))[:15]:
            print('  {} : {} pages'.format(img, len(pages)))

print('')
print('TOTAL: {} sites with cross-page image reuse'.format(total_overused))
