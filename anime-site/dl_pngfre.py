"""
Download Demon Slayer + JJK character images from pngfre.com
pngwing doesn't have these series, but pngfre does.
Run: python3 anime-site/dl_pngfre.py
"""
import requests, re, os, sys, time, subprocess, json
from pathlib import Path

ROOT = Path('/root/my-first-site30')
ANIME_IMG = ROOT / 'anime-site' / 'images'
ANIME_IMG.mkdir(parents=True, exist_ok=True)
SHARED = ROOT / 'shared'
DOUBAO = SHARED / 'doubao_vision.py'
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

def verify_image(path, expected_name):
    """Check if image contains the right character"""
    r = subprocess.run(
        ['python3', str(DOUBAO), str(path)],
        capture_output=True, text=True, timeout=120
    )
    output = (r.stdout + r.stderr).lower()
    parts = expected_name.lower().replace('-', ' ').split()
    found = sum(1 for p in parts if len(p) > 2 and p in output)
    negatives = ['fruit', 'raspberry', 'flower', 'logo', 'abstract', 'frame',
                  'watercolor', 'background', 'parchment', 'phoenix', 'butterfly',
                  'leaf', 'decoration', 'shattered glass', 'gold border', 'card',
                  'speech bubble', 'powder', 'explosion', 'smartphone']
    if any(n in output for n in negatives):
        return False, 'decorative'
    # Check for anime/series keywords
    series_kw = ['demon slayer', '鬼灭之刃', 'kny', 'jujutsu kaisen', '咒术回战', 'anime']
    has_series = any(k in output for k in series_kw)
    if found >= 1 or (found >= 0 and has_series):
        return True, f'match({found})'
    return False, f'no_match({found})'

def get_pngfre_urls(category_url):
    """Get all full-size PNG URLs from a pngfre category page"""
    r = SESSION.get(category_url, timeout=20)
    imgs = re.findall(r'<img[^>]+src=\"([^\"]+\.png[^\"]*)\"', r.text)
    imgs += re.findall(r'data-lazy-src=\"([^\"]+\.png[^\"]*)\"', r.text)
    unique = set()
    for url in imgs:
        full = re.sub(r'-\d+x\d+', '', url)
        if '.png' in full:
            unique.add(full)
    return list(unique)

def download_and_verify(url, char_name, save_name):
    """Download, verify, rembg, save"""
    target = ANIME_IMG / save_name
    try:
        r = SESSION.get(url, timeout=60)
        if r.status_code != 200 or len(r.content) < 10240:
            return False
        if r.content[:4] != b'\x89PNG':
            return False
        with open(target, 'wb') as f:
            f.write(r.content)
        ok, reason = verify_image(target, char_name)
        if ok:
            try:
                from rembg import remove
                with open(target, 'rb') as f:
                    data = f.read()
                result = remove(data)
                with open(target, 'wb') as f:
                    f.write(result)
            except:
                pass
            log(f'  ✓ {save_name} ({char_name})')
            return True
        else:
            log(f'  ✗ {save_name} ({char_name}) -> {reason}')
            target.unlink(missing_ok=True)
            return False
    except Exception as e:
        log(f'  ✗ {save_name}: {e}')
        target.unlink(missing_ok=True)
        return False

def main():
    log('=' * 60)
    log('Download DS + JJK images from pngfre.com')
    log('=' * 60)

    # Priority 1: Demon Slayer
    log('\n--- DEMON SLAYER ---')
    ds_urls = get_pngfre_urls('https://pngfre.com/demon-slayer-png/')
    log(f'Found {len(ds_urls)} images on pngfre DS page')

    ds_chars = ['tanjiro', 'giyu', 'nezuko', 'shinobu', 'zenitsu', 'inosuke', 'rengoku', 'muzan']
    downloaded_ds = {c: 0 for c in ds_chars}

    for url in ds_urls:
        # Try to match each URL to a character via doubao
        for char in ds_chars:
            if downloaded_ds[char] >= 1:
                continue
            save = f'ds_{char}.png' if char != 'tanjiro' else 'tanjiro.png'
            if download_and_verify(url, char, save):
                downloaded_ds[char] += 1
                break
        time.sleep(3)
        if all(v >= 1 for v in downloaded_ds.values()):
            break

    log(f'DS results: {sum(downloaded_ds.values())}/8 OK')

    # Priority 2: JJK
    log('\n--- JUJUTSU KAISEN ---')
    for char_name, url_path in [('Satoru Gojo', 'satoru-gojo-png')]:
        jjk_url = f'https://pngfre.com/{url_path}/'
        urls = get_pngfre_urls(jjk_url)
        log(f'Found {len(urls)} images for {char_name}')
        for url in urls:
            save = 'jjk_gojo.png'
            if download_and_verify(url, 'gojo', save):
                break
            time.sleep(3)

    # Verify results
    total = len(list(ANIME_IMG.glob('*.png')))
    log(f'\nTotal images in anime-site/images/: {total}')
    log('Done!')

if __name__ == '__main__':
    main()
