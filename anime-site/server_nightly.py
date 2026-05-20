"""
Server nightly task: Fix anime.jycsd.com images
Only ONE site per night. Quality over quantity.
Run: python3 anime-site/server_nightly.py
"""
import subprocess, time, os, sys
from pathlib import Path

ROOT = Path('/root/my-first-site30')
ANIME_IMG = ROOT / 'anime-site' / 'images'
ANIME_IMG.mkdir(parents=True, exist_ok=True)
SHARED = ROOT / 'shared'
LOG = Path('/tmp/anime_nightly.log')

def log(msg):
    t = time.strftime('%H:%M:%S')
    line = f'[{t}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a') as f:
        f.write(line + '\n')
        f.flush()

def verify_image(path, char_name):
    """Use doubao to verify image is correct character"""
    r = subprocess.run(
        ['python3', str(SHARED / 'doubao_vision.py'), str(path)],
        capture_output=True, text=True, timeout=60
    )
    output = (r.stdout + r.stderr).lower()
    # Check for character name
    name_parts = char_name.lower().replace('-', ' ').split()
    found = sum(1 for p in name_parts if len(p) > 2 and p in output)
    # Check for decorative negatives
    negatives = ['fruit', 'raspberry', 'flower', 'logo', 'abstract', 'frame',
                  'watercolor', 'parchment', 'phoenix', 'butterfly', 'leaf',
                  'decoration', 'shattered glass', 'gold border', 'card',
                  'speech bubble', 'powder', 'explosion', 'smartphone',
                  'hand holding', 'golden', 'ornamental']
    is_deco = any(n in output for n in negatives)
    if is_deco:
        return False, 'decorative'
    if found >= 1:
        return True, 'character_match'
    return False, f'no_match(found={found})'

def try_download(char_name, series, filename):
    """Try to download one character image with verification"""
    target = ANIME_IMG / filename
    log(f'Downloading {filename} ({char_name} from {series})...')

    # Search pngwing with different queries
    import requests, re
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    })

    queries = [
        f'{char_name} {series}',
        f'{char_name} {series} character',
        f'{char_name} {series} png',
    ]

    seen = set()
    for query in queries:
        url = f'https://www.pngwing.com/en/search?q={requests.utils.quote(query)}'
        try:
            r = session.get(url, timeout=20)
            if r.status_code != 200:
                continue
            thumbs = re.findall(r'data-src="(https://w7\.pngwing\.com[^"]+-thumbnail\.png)"', r.text)
            full_urls = [u.replace('-thumbnail.png', '.png') for u in thumbs]

            for img_url in full_urls:
                if img_url in seen:
                    continue
                seen.add(img_url)

                # Download
                ir = session.get(img_url, timeout=30)
                if ir.status_code != 200 or len(ir.content) < 10240:
                    continue
                if ir.content[:4] != b'\x89PNG':
                    continue

                # Save temp
                with open(target, 'wb') as f:
                    f.write(ir.content)

                # Verify with doubao
                ok, reason = verify_image(target, char_name)
                if ok:
                    # Run rembg
                    try:
                        from rembg import remove
                        with open(target, 'rb') as f:
                            data = f.read()
                        result = remove(data)
                        with open(target, 'wb') as f:
                            f.write(result)
                        log(f'  ✓ {filename} verified + rembg OK')
                    except Exception as e:
                        log(f'  ✓ {filename} verified (rembg err: {e})')
                    return True
                else:
                    log(f'  ✗ {filename} rejected ({reason})')
                    target.unlink(missing_ok=True)
                    continue
        except Exception as e:
            log(f'  ✗ query error: {e}')
        time.sleep(2)

    log(f'  ✗ FAILED: no valid image found for {char_name}')
    return False

def ensure_transparent_all():
    """Run rembg on all images that need it"""
    from PIL import Image
    from rembg import remove

    for f in sorted(ANIME_IMG.glob('*.png')):
        try:
            img = Image.open(f)
            if img.mode == 'RGBA':
                a = img.getchannel('A')
                if a.getextrema()[0] < 50:
                    continue  # already transparent
            log(f'  rembg {f.name}...')
            with open(f, 'rb') as fh:
                data = fh.read()
            result = remove(data)
            with open(f, 'wb') as fh:
                fh.write(result)
        except Exception as e:
            log(f'  rembg err {f.name}: {e}')

def main():
    log('=' * 50)
    log('NIGHTLY: anime.jycsd.com image fix')
    log('=' * 50)

    # Only DS and JJK images (the broken ones)
    characters = [
        # Demon Slayer (all current images are decorative garbage)
        ('Tanjiro Kamado', 'Demon Slayer', 'tanjiro.png'),
        ('Giyu Tomioka', 'Demon Slayer', 'ds_giyu.png'),
        ('Nezuko Kamado', 'Demon Slayer', 'ds_nezuko.png'),
        ('Shinobu Kocho', 'Demon Slayer', 'ds_shinobu.png'),
        ('Zenitsu Agatsuma', 'Demon Slayer', 'ds_zenitsu.png'),
        ('Inosuke Hashibira', 'Demon Slayer', 'ds_inosuke.png'),
        ('Kyojuro Rengoku', 'Demon Slayer', 'ds_rengoku.png'),
        ('Muzan Kibutsuji', 'Demon Slayer', 'ds_muzan.png'),
        # JJK (some wrong)
        ('Yuji Itadori', 'Jujutsu Kaisen', 'yuji.png'),
        ('Satoru Gojo', 'Jujutsu Kaisen', 'jjk_gojo.png'),
        ('Ryomen Sukuna', 'Jujutsu Kaisen', 'jjk_sukuna.png'),
    ]

    ok = 0
    fail = 0
    for name, series, filename in characters:
        if try_download(name, series, filename):
            ok += 1
        else:
            fail += 1
        time.sleep(3)

    # Ensure all images are transparent
    log('\nRunning rembg on all images...')
    ensure_transparent_all()

    log('\n' + '=' * 50)
    log(f'RESULT: {ok} OK, {fail} failed')
    count = len(list(ANIME_IMG.glob('*.png')))
    log(f'Total images in anime-site/images/: {count}')
    log('=' * 50)

if __name__ == '__main__':
    main()
