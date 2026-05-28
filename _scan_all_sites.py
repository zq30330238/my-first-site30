"""
Comprehensive all-site audit: MD5 dupes, broken imgs, broken links, corrupt files, unreferenced imgs.
"""
import os, re, hashlib, sys
from collections import defaultdict

SITE_DIRS = [d for d in os.listdir('.') if os.path.isdir(d) and d not in (
    'shared','__pycache__','_tmp_fix','backup-config','demos','global-architecture-redirect',
    'logs','temp','tmp','tmp_moto_banner','videos','workers','.git','.github','.claude',
    '.codex','.codegraph','.reasonix','.vercel','.vscode','.wrangler','.agents'
)]

# Domain mapping (site dir -> domain)
SITE_DOMAINS = {
    'anime-site': 'anime.jycsd.com',
    'aot-site': 'aot.jycsd.com',
    'bleach-site': 'bleach.jycsd.com',
    'chinese-architecture-site': 'chinese-architecture.jycsd.com',
    'clothing-site': 'clothing.jycsd.com',
    'dailymedadvice': 'dailymedadvice.com',
    'dragonball-site': 'dragonball.jycsd.com',
    'eldenring-site': 'eldenring.jycsd.com',
    'entertainment': 'entertainment.jycsd.com',
    'fortnite-site': 'fortnite.jycsd.com',
    'games-site': 'games.jycsd.com',
    'hxh-site': 'hxh.jycsd.com',
    'jjk-site': 'jjk.jycsd.com',
    'jojo-site': 'jojo.jycsd.com',
    'lol-site': 'lol.jycsd.com',
    'main-site': 'www.jycsd.com',
    'minecraft-site': 'minecraft.jycsd.com',
    'naruto-site': 'naruto.jycsd.com',
    'onepiece-site': 'onepiece.jycsd.com',
    'rightsdaily': 'rightsdaily.com',
    'sao-site': 'sao.jycsd.com',
    'sub-auto': 'auto.jycsd.com',
    'sub-finance': 'finance.jycsd.com',
    'sub-food': 'food.jycsd.com',
    'sub-healthy': 'healthy.jycsd.com',
    'sub-home': 'home.jycsd.com',
    'sub-moto': 'moto.jycsd.com',
    'sub-pets': 'pets.jycsd.com',
    'sub-tech': 'tech.jycsd.com',
    'sub-travel': 'travel.jycsd.com',
    'tokyoghoul-site': 'tokyoghoul.jycsd.com',
    'valorant-site': 'valorant.jycsd.com',
    'western-architecture-site': 'western-architecture.jycsd.com',
}

results = {}

for site in sorted(SITE_DIRS):
    domain = SITE_DOMAINS.get(site, site.replace('-site','') + '.jycsd.com')
    images_dir = os.path.join(site, 'images')
    if not os.path.exists(images_dir):
        continue

    site_result = {
        'md5_dupes': 0,
        'broken_imgs': 0,
        'broken_links': 0,
        'corrupt_0kb': 0,
        'unreferenced': 0,
        'total_imgs': 0,
        'total_html': 0,
    }

    # Collect all images on disk
    disk_imgs = {}
    md5_map = defaultdict(list)
    for root, dirs, files in os.walk(images_dir):
        for f in files:
            if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.gif','.svg')):
                fp = os.path.join(root, f)
                sz = os.path.getsize(fp)
                site_result['total_imgs'] += 1
                if sz == 0:
                    site_result['corrupt_0kb'] += 1
                rel = os.path.relpath(fp, site).replace('\\', '/')
                disk_imgs[rel] = sz
                if sz > 1024:
                    with open(fp, 'rb') as fh:
                        md5_map[hashlib.md5(fh.read()).hexdigest()].append(rel)

    # MD5 duplicates
    dupes = {k:v for k,v in md5_map.items() if len(v) > 1}
    site_result['md5_dupes'] = sum(len(v)-1 for v in dupes.values())

    # Collect all HTML pages and their image/link references
    html_files = []
    for root, dirs, files in os.walk(site):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    site_result['total_html'] = len(html_files)

    referenced_imgs = set()
    for fp in html_files:
        rel = os.path.relpath(fp, site).replace('\\', '/')
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            content = fh.read()

        # Find image references (both absolute and relative)
        patterns = [
            r'https?://' + re.escape(domain) + r'/(images/[^\"\'\s<>]+\.(?:jpg|jpeg|png|webp|gif|svg))',
            r'["\'(]\s*/(images/[^\"\'\s<>]+\.(?:jpg|jpeg|png|webp|gif|svg))',
            r'src=[\"\'](images/[^\"\']+\.(?:jpg|jpeg|png|webp|gif|svg))[\"\']',
        ]
        for pattern in patterns:
            for m in re.finditer(pattern, content, re.I):
                img_rel = m.group(1)
                # Normalize path
                img_rel = img_rel.replace('\\', '/')
                if img_rel.startswith('images/'):
                    referenced_imgs.add(img_rel)

        # Find broken internal links
        for m in re.finditer(r'href=[\"\']([^\"\']+)[\"\']', content, re.I):
            href = m.group(1)
            if href.startswith('http') and domain not in href:
                continue
            if href.startswith('#') or href.startswith('javascript') or href.startswith('mailto') or href.startswith('tel:'):
                continue
            if not href or href == '/':
                continue
            # Map to local path
            if href.startswith('https://' + domain):
                path = href[len('https://' + domain):]
            elif href.startswith('http://' + domain):
                path = href[len('http://' + domain):]
            elif href.startswith('http') or href.startswith('//'):
                continue
            else:
                path = href
            if not path or path == '/':
                continue
            if path[0] != '/':
                base = os.path.dirname(rel)
                path = '/' + os.path.normpath(os.path.join(base, path)).replace('\\', '/')
            # Check if file exists
            if path.endswith('/'):
                local = os.path.join(site, path[1:] + 'index.html')
            else:
                local = os.path.join(site, path[1:])
                if not os.path.exists(local) and not local.endswith('.html'):
                    local2 = local + '.html'
                    if os.path.exists(local2):
                        local = local2
            if not os.path.exists(local):
                site_result['broken_links'] += 1

    # Check referenced images exist on disk
    for img_rel in referenced_imgs:
        if img_rel not in disk_imgs:
            site_result['broken_imgs'] += 1

    # Unreferenced images
    for img_rel in disk_imgs:
        if img_rel not in referenced_imgs:
            site_result['unreferenced'] += 1

    results[site] = site_result

# Print summary
print('=' * 100)
print('{:40s} {:>6s} {:>6s} {:>5s} {:>6s} {:>6s} {:>8s} {:>6s}'.format(
    'SITE', 'HTML', 'IMGS', 'MD5D', 'BRKIMG', 'BRKLNK', 'CORRUPT', 'UNREF'))
print('=' * 100)

total = defaultdict(int)
for site, r in sorted(results.items()):
    flag = ''
    if r['md5_dupes'] > 0 or r['broken_imgs'] > 0 or r['broken_links'] > 0 or r['corrupt_0kb'] > 0:
        flag = ' <-- ISSUES'
    print('{:40s} {:>5d} {:>5d} {:>5d} {:>6d} {:>6d} {:>8d} {:>6d}{}'.format(
        site, r['total_html'], r['total_imgs'], r['md5_dupes'],
        r['broken_imgs'], r['broken_links'], r['corrupt_0kb'], r['unreferenced'], flag))
    for k in total:
        total[k] += r[k]

print('=' * 100)
print('{:40s} {:>5d} {:>5d} {:>5d} {:>6d} {:>6d} {:>8d} {:>6d}'.format(
    'TOTAL', total['total_html'], total['total_imgs'], total['md5_dupes'],
    total['broken_imgs'], total['broken_links'], total['corrupt_0kb'], total['unreferenced']))

# Show broken links detail for sites with issues
print('\n' + '=' * 100)
print('BROKEN LINKS DETAIL')
print('=' * 100)
for site, r in sorted(results.items()):
    if r['broken_links'] > 0:
        print('\n--- {} ({} broken links) ---'.format(site, r['broken_links']))
        domain = SITE_DOMAINS.get(site, '')
        html_files = []
        for root, dirs, files in os.walk(site):
            for f in files:
                if f.endswith('.html'):
                    html_files.append(os.path.join(root, f))
        shown = 0
        for fp in sorted(html_files):
            rel = os.path.relpath(fp, site).replace('\\', '/')
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            for m in re.finditer(r'href=[\"\']([^\"\']+)[\"\']', content, re.I):
                href = m.group(1)
                if href.startswith('http') and domain and domain not in href:
                    continue
                if href.startswith('#') or href.startswith('javascript') or href.startswith('mailto') or href.startswith('tel:'):
                    continue
                if not href or href == '/':
                    continue
                if href.startswith('https://' + domain):
                    path = href[len('https://' + domain):]
                elif href.startswith('http://' + domain):
                    path = href[len('http://' + domain):]
                elif href.startswith('http') or href.startswith('//'):
                    continue
                else:
                    path = href
                if not path or path == '/':
                    continue
                if path[0] != '/':
                    base = os.path.dirname(rel)
                    path = '/' + os.path.normpath(os.path.join(base, path)).replace('\\', '/')
                if path.endswith('/'):
                    local = os.path.join(site, path[1:] + 'index.html')
                else:
                    local = os.path.join(site, path[1:])
                    if not os.path.exists(local) and not local.endswith('.html'):
                        if os.path.exists(local + '.html'):
                            local = local + '.html'
                if not os.path.exists(local):
                    print('  {} -> {}'.format(rel, path))
                    shown += 1
                    if shown >= 10:
                        break
            if shown >= 10:
                print('  ... showing first 10')
                break

# Broken images detail
print('\n' + '=' * 100)
print('BROKEN IMAGE DETAIL')
print('=' * 100)
for site, r in sorted(results.items()):
    if r['broken_imgs'] > 0:
        print('\n--- {} ({} broken imgs) ---'.format(site, r['broken_imgs']))
        domain = SITE_DOMAINS.get(site, '')
        disk_imgs = {}
        for root, dirs, files in os.walk(os.path.join(site, 'images')):
            for f in files:
                fp = os.path.join(root, f)
                disk_imgs[os.path.relpath(fp, site).replace('\\', '/')] = True
        shown = 0
        html_files = []
        for root, dirs, files in os.walk(site):
            for f in files:
                if f.endswith('.html'):
                    html_files.append(os.path.join(root, f))
        for fp in sorted(html_files):
            rel = os.path.relpath(fp, site).replace('\\', '/')
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            patterns = [
                r'https?://' + re.escape(domain) + r'/(images/[^\"\'\s<>]+\.(?:jpg|jpeg|png|webp|gif|svg))',
                r'["\'(]\s*/(images/[^\"\'\s<>]+\.(?:jpg|jpeg|png|webp|gif|svg))',
                r'src=[\"\'](images/[^\"\']+\.(?:jpg|jpeg|png|webp|gif|svg))[\"\']',
            ]
            for pattern in patterns:
                for m in re.finditer(pattern, content, re.I):
                    img_rel = m.group(1).replace('\\', '/')
                    if img_rel.startswith('images/') and img_rel not in disk_imgs:
                        print('  {} -> {}'.format(rel, img_rel))
                        shown += 1
                        if shown >= 10:
                            break
                if shown >= 10:
                    break
            if shown >= 10:
                print('  ... showing first 10')
                break
