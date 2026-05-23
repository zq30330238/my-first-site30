"""
Download Demon Slayer + JJK character images from pngfre.com
Strategy: parse alt text from HTML (contains character names).
NO rembg here - run separately to avoid OOM.
Run: python3 anime-site/dl_pngfre.py
"""
import requests, re, time
from pathlib import Path

ROOT = Path('/root/my-first-site30')
ANIME_IMG = ROOT / 'anime-site' / 'images'
ANIME_IMG.mkdir(parents=True, exist_ok=True)
LOG = Path('/tmp/dl_pngfre.log')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

def log(msg):
    t = time.strftime('%H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')
        f.flush()

def find_images_on_page(url):
    """Parse img tags from a page, return list of (alt_text, full_size_url)"""
    r = SESSION.get(url, timeout=20)
    body_start = r.text.find('<body')
    body_end = r.text.find('</body>')
    body = r.text[body_start:body_end] if body_start >= 0 else r.text

    results = []
    for img_tag in re.findall(r'<img[^>]+>', body):
        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        alt = alt_match.group(1) if alt_match else ''

        src_match = re.search(r'src="([^"]+\.png)"', img_tag)
        if not src_match:
            src_match = re.search(r'data-lazy-src="([^"]+\.png)"', img_tag)
        if not src_match:
            continue

        full_url = re.sub(r'-\d+x\d+(?=\.png)', '', src_match.group(1))
        results.append((alt.strip(), full_url))
    return results

def download_png(url, target_path):
    """Download PNG file, no rembg"""
    r = SESSION.get(url, timeout=60)
    if r.status_code != 200 or len(r.content) < 10240:
        return False
    if r.content[:4] != b'\x89PNG':
        return False
    with open(target_path, 'wb') as f:
        f.write(r.content)
    return True

def match_alt(alt_text, keywords):
    """Check if alt_text contains any keyword"""
    alt_lower = alt_text.lower()
    return any(k.lower() in alt_lower for k in keywords)

def main():
    log('=' * 60)
    log('Download DS + JJK images from pngfre.com')
    log('=' * 60)

    # === DEMON SLAYER ===
    log('\n--- DEMON SLAYER ---')

    # Character mapping: save_name -> [alt text keywords to match]
    char_map = [
        ('tanjiro.png',  ['tanjiro kamado', 'tanjiro']),
        ('ds_giyu.png',   ['giyu tomioka', 'giyu', 'tomioka']),
        ('ds_nezuko.png', ['nezuko kamado', 'nezuko']),
        ('ds_shinobu.png',['shinobu kocho', 'shinobu', 'kocho']),
        ('ds_zenitsu.png',['zenitsu agatsuma', 'zenitsu']),
        ('ds_inosuke.png',['inosuke hashibira', 'inosuke']),
        ('ds_rengoku.png',['kyojuro rengoku', 'rengoku']),
        ('ds_muzan.png',  ['muzan kibutsuji', 'muzan']),
    ]

    images = find_images_on_page('https://pngfre.com/demon-slayer-png/')
    log(f'Found {len(images)} images on DS category page')

    downloaded = set()
    used_urls = set()

    # Pass 1: Match by alt text from category page
    for save_name, keywords in char_map:
        for alt, url in images:
            if url in used_urls:
                continue
            if not match_alt(alt, keywords):
                continue
            if match_alt(alt, ['logo', 'poster']):
                continue
            target = ANIME_IMG / save_name
            log(f'  {save_name} <- "{alt[:50]}..."')
            if download_png(url, target):
                used_urls.add(url)
                downloaded.add(save_name)
                log(f'  ✓ {save_name}')
            break

    # Pass 2: Check individual character pages for missing ones
    individual_slugs = {
        'tanjiro.png':  'tanjiro-kamado-png',
        'ds_giyu.png':   'giyu-tomioka-png',
        'ds_nezuko.png': 'nezuko-png',
        'ds_shinobu.png':'shinobu-kocho-png',
        'ds_zenitsu.png':'zenitsu-agatsuma-png',
        'ds_inosuke.png':'inosuke-hashibira-png',
        'ds_rengoku.png':'kyojuro-rengoku-png',
        'ds_muzan.png':  'muzan-kibutsuji-png',
    }

    missing = [s for s, _ in char_map if s not in downloaded]
    if missing:
        log(f'\nMissing {len(missing)}/{len(char_map)}, trying individual pages...')
        for save_name in missing:
            slug = individual_slugs.get(save_name)
            if not slug:
                continue
            page_url = f'https://pngfre.com/{slug}/'
            page_imgs = find_images_on_page(page_url)
            log(f'  {slug}: {len(page_imgs)} images')
            for alt, url in page_imgs:
                if url in used_urls:
                    continue
                if match_alt(alt, ['logo', 'poster']):
                    continue
                target = ANIME_IMG / save_name
                if download_png(url, target):
                    used_urls.add(url)
                    downloaded.add(save_name)
                    log(f'  ✓ {save_name} (individual page)')
                    break

    # Pass 3: Fallback - any non-logo image for still-missing
    missing = [s for s, _ in char_map if s not in downloaded]
    if missing:
        log(f'\nFallback for {missing}...')
        for alt, url in images:
            if url in used_urls:
                continue
            if match_alt(alt, ['logo', 'poster']):
                continue
            if not missing:
                break
            save_name = missing.pop(0)
            target = ANIME_IMG / save_name
            log(f'  fallback: {save_name} <- "{alt[:50]}..."')
            if download_png(url, target):
                used_urls.add(url)
                downloaded.add(save_name)
                log(f'  ✓ {save_name}')
            else:
                missing.insert(0, save_name)

    log(f'DS: {len(downloaded)}/8')

    # === JUJUTSU KAISEN ===
    log('\n--- JUJUTSU KAISEN ---')
    jjk_map = [
        ('jjk_gojo.png',   ['satoru gojo', 'gojo']),
        ('jjk_sukuna.png', ['ryomen sukuna', 'sukuna']),
        ('yuji.png',       ['yuji itadori', 'itadori', 'yuji']),
    ]

    # Pass 1: Try dedicated pages
    jjk_pages = ['satoru-gojo-png']
    for slug in jjk_pages:
        page_imgs = find_images_on_page(f'https://pngfre.com/{slug}/')
        for alt, url in page_imgs:
            for save_name, keywords in jjk_map:
                if save_name in downloaded:
                    continue
                if match_alt(alt, keywords):
                    target = ANIME_IMG / save_name
                    if download_png(url, target):
                        downloaded.add(save_name)
                        log(f'  ✓ {save_name} (dedicated page)')
                    break

    # Pass 2: Anime category page for remaining
    missing_jjk = [s for s, _ in jjk_map if s not in downloaded]
    if missing_jjk:
        log(f'JJK missing: {missing_jjk}, checking anime-png category...')
        anime_imgs = find_images_on_page('https://pngfre.com/anime-png/')
        log(f'Found {len(anime_imgs)} images on anime-png page')
        for alt, url in anime_imgs:
            for save_name, keywords in jjk_map:
                if save_name in downloaded:
                    continue
                if match_alt(alt, keywords):
                    target = ANIME_IMG / save_name
                    if download_png(url, target):
                        downloaded.add(save_name)
                        log(f'  ✓ {save_name} (anime category)')
                    break

    log(f'JJK: {sum(1 for s, _ in jjk_map if s in downloaded)}/3')

    # Summary
    total = len(list(ANIME_IMG.glob('*.png')))
    log('\n' + '=' * 60)
    log(f'Total images: {total}')
    log('Next: run rembg separately')
    log('Done!')

if __name__ == '__main__':
    main()
