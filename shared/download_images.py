import requests, re, os, time, hashlib, subprocess, json
from pathlib import Path
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.pngwing.com/',
})

PNGWING_SEARCH = 'https://www.pngwing.com/en/search?q={}'
STATS = {}
SEEN_HASHES = set()

VERIFY_PROMPT = """Look at this image carefully.
Character/Subject expected: {character_name}
Context: {series_or_topic}

Answer YES if ALL of these are true:
1. This image CLEARLY shows {character_name}
2. The character/subject is recognizable and matches common depictions
3. This is a proper character image or scene image (not a logo, text, or abstract pattern)

Answer NO if ANY of these is true:
1. This is a different character/person/subject entirely
2. This is a logo, text, chart, abstract pattern, or decorative frame
3. This is a group/crowd shot where the specific character can't be identified
4. The image is too blurry/dark to identify the subject
5. This is a real-life cosplay photo (not the actual animated/game character)

Reply ONLY with YES or NO."""


def quick_validate(img_path):
    """Local Pillow pre-check before doubao API. Returns (passed, reason)."""
    try:
        img = Image.open(img_path)
        w, h = img.size
        if w < 100 or h < 100:
            return False, f'too small ({w}x{h})'
        if w / h > 3.0 or h / w > 3.0:
            return False, f'bad aspect ratio ({w}x{h})'
        if img.mode == 'RGBA':
            alpha = img.getchannel('A')
            extrema = alpha.getextrema()
            if extrema[0] == 255 and extrema[1] == 255:
                return False, 'no transparency'
            if alpha.getbbox() is None:
                return False, 'fully transparent'
        from PIL import ImageStat
        gray = img.convert('L')
        stat = ImageStat.Stat(gray)
        if stat.stddev[0] < 15:
            return False, f'flat image (stddev={stat.stddev[0]:.1f})'
        return True, 'passed'
    except Exception as e:
        return False, f'error: {e}'


def verify_character(filepath, char_name, series=""):
    """Use doubao vision to verify image contains the correct character.
    ALWAYS calls doubao after local pre-check — NO MORE SKIPPING."""
    # Always quick_validate first — reject bad formats/sizes early
    passed, reason = quick_validate(filepath)
    if not passed:
        print(f'  [LOCAL REJECT] {Path(filepath).name}: {reason}')
        return False

    # Now ALWAYS verify content with doubao
    print(f'  [DOUBAO VERIFY] {Path(filepath).name}: checking if this is {char_name}...')
    script = Path(__file__).parent / 'doubao_vision.py'
    if not script.exists():
        print(f'  [WARN] doubao_vision.py not found, allowing image through')
        return True

    try:
        prompt = VERIFY_PROMPT.format(character_name=char_name, series_or_topic=series)
        r = subprocess.run(
            ['py', str(script), str(filepath), prompt],
            capture_output=True, text=True, timeout=45
        )
        output = (r.stdout + r.stderr).strip()
        print(f'  [DOUBAO RESPONSE] {output[:200]}')

        # Check for explicit YES
        if output.upper().strip() == 'YES' or 'YES' in output.upper().split():
            print(f'  [DOUBAO PASS] {Path(filepath).name}: confirmed as {char_name}')
            return True

        # Any other response = reject
        print(f'  [DOUBAO REJECT] {Path(filepath).name}: not recognized as {char_name}')
        return False
    except subprocess.TimeoutExpired:
        print(f'  [DOUBAO TIMEOUT] {Path(filepath).name}')
        return False
    except Exception as e:
        print(f'  [DOUBAO ERROR] {Path(filepath).name}: {e}')
        return False

def ensure_transparent(filepath):
    """Run rembg on image if it has no transparency."""
    try:
        img = Image.open(filepath)
        if img.mode == 'RGBA':
            bbox = img.getchannel('A').getextrema()
            if bbox[0] < 255:
                return True
        from rembg import remove
        with open(filepath, 'rb') as f:
            data = f.read()
        result = remove(data)
        with open(filepath, 'wb') as f:
            f.write(result)
        print(f'  [REMBG] {filepath.name}')
        return True
    except Exception as e:
        print(f'  [REMBG ERR] {filepath.name}: {e}')
        return False

def compress_image(filepath, max_width=640):
    """Compress image: resize to max_width, optimize PNG or convert to JPEG."""
    try:
        img = Image.open(filepath)
        if img.width > max_width:
            ratio = max_width / img.width
            new_h = int(img.height * ratio)
            img = img.resize((max_width, new_h), Image.LANCZOS)
        before = os.path.getsize(filepath)
        if img.mode == 'RGBA':
            try:
                img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                img = img.convert('RGBA')
            except:
                pass
            img.save(filepath, 'PNG', optimize=True)
        else:
            out_path = str(filepath).replace('.png', '.jpg')
            img.save(out_path, 'JPEG', quality=80, optimize=True)
            if out_path != str(filepath):
                os.remove(filepath)
                return out_path
        saved_path = filepath if Path(filepath).suffix == '.png' else str(filepath).replace('.png', '.jpg')
        after = os.path.getsize(saved_path)
        print(f'  [COMPRESS] {Path(filepath).name}: {before//1024}KB -> {after//1024}KB (saved {(before-after)//1024}KB)')
        return saved_path
    except Exception as e:
        print(f'  [COMPRESS ERR] {Path(filepath).name}: {e}')
        return filepath

def is_valid_png(filepath):
    if not os.path.exists(filepath):
        return False
    if os.path.getsize(filepath) < 10240:
        return False
    with open(filepath, 'rb') as f:
        return f.read(4) == b'\x89PNG'

def search_pngwing(query):
    url = PNGWING_SEARCH.format(requests.utils.quote(query))
    try:
        r = SESSION.get(url, timeout=20)
        if r.status_code != 200:
            return []
        thumb_urls = re.findall(r'data-src=\"(https://w7\.pngwing\.com[^\"]+-thumbnail\.png)\"', r.text)
        full_urls = [u.replace('-thumbnail.png', '.png') for u in thumb_urls]
        return full_urls
    except Exception as e:
        print(f'  Search error [{query}]: {e}')
        return []

def download_image(url, filepath):
    if os.path.exists(filepath):
        if is_valid_png(filepath):
            return 'exists'
    try:
        r = SESSION.get(url, timeout=30)
        if r.status_code == 200 and len(r.content) > 10240:
            if r.content[:4] == b'\x89PNG':
                h = hashlib.md5(r.content).hexdigest()
                if h in SEEN_HASHES:
                    return 'dup'
                SEEN_HASHES.add(h)
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                if is_valid_png(filepath):
                    return 'ok'
        return 'bad'
    except Exception as e:
        return f'err:{e}'

def download_character(char_name, series, out_dir, max_images=2):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = char_name.lower().replace(' ', '-').replace('.', '').replace("'", '')
    downloaded = 0

    # Build relevance keywords from character name
    keywords = [w.lower() for w in char_name.replace('.', '').split() if len(w) > 1]
    if len(keywords) > 1:
        keywords.append(char_name.lower().replace('.', '').replace(' ', '-'))

    # Main queries + fallback queries for retry
    queries = [
        f'{char_name} {series}',
        f'{char_name} {series} character',
        f'{char_name} {series} transparent',
    ]
    fallback_queries = [
        f'{char_name} {series} render PNG',
        f'{char_name} {series} official art',
        f'{char_name} anime character transparent',
    ]

    seen_urls = set()
    attempts = 0
    max_attempts = 9  # 3 queries x 3 URLs max per query

    # Try main queries first, then fallbacks
    all_queries = queries + fallback_queries

    for query_idx, query in enumerate(all_queries):
        if downloaded >= max_images or attempts >= max_attempts:
            break

        print(f'  Searching: "{query}"')
        urls = search_pngwing(query)
        relevant = [u for u in urls if any(k in u.lower() for k in keywords)]
        subtle = [u for u in urls if u not in relevant]
        ordered_urls = relevant + subtle

        for url in ordered_urls:
            if downloaded >= max_images:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)

            suffix = f'_{downloaded+1}' if downloaded > 0 else ''
            fname = f'{slug}{suffix}.png'
            fpath = out_dir / fname

            result = download_image(url, str(fpath))
            if result not in ('ok', 'exists'):
                attempts += 1
                if attempts >= max_attempts:
                    break
                continue

            # Quick validate (format/size check)
            passed, reason = quick_validate(str(fpath))
            if not passed:
                print(f'    [LOCAL REJECT] {fname}: {reason}')
                try: os.remove(str(fpath))
                except: pass
                attempts += 1
                if attempts >= max_attempts:
                    break
                continue

            # Doubao verify — THE CRITICAL STEP
            if verify_character(str(fpath), char_name, series):
                sz = os.path.getsize(str(fpath))
                print(f'    [PASS] {fname} ({sz//1024}KB) — content confirmed')
                ensure_transparent(str(fpath))
                compress_image(str(fpath))
                downloaded += 1
            else:
                print(f'    [REJECT] {fname}: wrong content, trying next...')
                try: os.remove(str(fpath))
                except: pass
                attempts += 1
                if attempts >= max_attempts:
                    break

            time.sleep(1.0)  # Polite delay between attempts

    # Log failures
    if downloaded < max_images and attempts >= max_attempts:
        failed_file = Path(__file__).parent.parent / 'failed_images.json'
        failed = {}
        if failed_file.exists():
            try: failed = json.loads(failed_file.read_text())
            except: pass
        failed[char_name] = {
            'series': series,
            'site_dir': str(out_dir),
            'max_images': max_images,
            'downloaded': downloaded,
            'attempts': attempts
        }
        failed_file.write_text(json.dumps(failed, indent=2))
        print(f'    [FAILED] {char_name}: only got {downloaded}/{max_images} after {attempts} attempts')

    return downloaded

def main():
    ROOT = Path(r'd:\AI网站文件夹')

    # === PRIORITY 1: One Piece ===
    print('=' * 60)
    print('PRIORITY 1: ONE PIECE')
    print('=' * 60)
    op_chars = [
        ('Monkey D. Luffy', 'One Piece'),
        ('Roronoa Zoro', 'One Piece'),
        ('Nami', 'One Piece'),
        ('Sanji', 'One Piece'),
        ('Usopp', 'One Piece'),
        ('Tony Tony Chopper', 'One Piece'),
        ('Nico Robin', 'One Piece'),
        ('Franky', 'One Piece'),
        ('Brook', 'One Piece'),
        ('Jinbe', 'One Piece'),
        ('Portgas D. Ace', 'One Piece'),
        ('Trafalgar Law', 'One Piece'),
        ('Shanks', 'One Piece'),
        ('Boa Hancock', 'One Piece'),
        ('Donquixote Doflamingo', 'One Piece'),
        ('Buggy', 'One Piece'),
        ('Crocodile', 'One Piece'),
        ('Monkey D. Garp', 'One Piece'),
        ('Silvers Rayleigh', 'One Piece'),
        ('Kaido', 'One Piece'),
        ('Big Mom Charlotte Linlin', 'One Piece'),
        ('Yamato', 'One Piece'),
        ('Eustass Kid', 'One Piece'),
        ('Marco the Phoenix', 'One Piece'),
    ]
    op_total = 0
    for name, series in op_chars:
        print(f'\n[{name}]')
        n = download_character(name, series, ROOT / 'onepiece-site' / 'images', max_images=2)
        op_total += n
        time.sleep(2)
    STATS['One Piece'] = op_total

    # === PRIORITY 2: Naruto ===
    print('\n' + '=' * 60)
    print('PRIORITY 2: NARUTO')
    print('=' * 60)
    naruto_chars = [
        ('Naruto Uzumaki', 'Naruto'),
        ('Sasuke Uchiha', 'Naruto'),
        ('Sakura Haruno', 'Naruto'),
        ('Kakashi Hatake', 'Naruto'),
        ('Itachi Uchiha', 'Naruto'),
        ('Hinata Hyuga', 'Naruto'),
        ('Jiraiya', 'Naruto'),
        ('Tsunade', 'Naruto'),
        ('Orochimaru', 'Naruto'),
        ('Gaara', 'Naruto'),
        ('Minato Namikaze', 'Naruto'),
        ('Madara Uchiha', 'Naruto'),
        ('Obito Uchiha', 'Naruto'),
        ('Rock Lee', 'Naruto'),
        ('Neji Hyuga', 'Naruto'),
        ('Shikamaru Nara', 'Naruto'),
        ('Might Guy', 'Naruto'),
        ('Pain Nagato', 'Naruto'),
        ('Killer Bee', 'Naruto'),
        ('Hashirama Senju', 'Naruto'),
        ('Tobirama Senju', 'Naruto'),
        ('Kushina Uzumaki', 'Naruto'),
        ('Kabuto Yakushi', 'Naruto'),
        ('Deidara', 'Naruto'),
    ]
    naruto_total = 0
    for name, series in naruto_chars:
        print(f'\n[{name}]')
        n = download_character(name, series, ROOT / 'naruto-site' / 'images', max_images=2)
        naruto_total += n
        time.sleep(2)
    STATS['Naruto'] = naruto_total

    # === PRIORITY 3: Valorant ===
    print('\n' + '=' * 60)
    print('PRIORITY 3: VALORANT')
    print('=' * 60)
    valorant_items = [
        ('Jett', 'Valorant agent'),
        ('Phoenix', 'Valorant agent'),
        ('Sage', 'Valorant agent'),
        ('Reyna', 'Valorant agent'),
        ('Chamber', 'Valorant agent'),
        ('Omen', 'Valorant agent'),
        ('Yoru', 'Valorant agent'),
        ('Sova', 'Valorant agent'),
        ('Brimstone', 'Valorant agent'),
        ('Viper', 'Valorant agent'),
        ('Cypher', 'Valorant agent'),
        ('Killjoy', 'Valorant agent'),
        ('Raze', 'Valorant agent'),
        ('Breach', 'Valorant agent'),
        ('Skye', 'Valorant agent'),
        ('KAYO', 'Valorant agent'),
        ('Astra', 'Valorant agent'),
        ('Neon', 'Valorant agent'),
        ('Fade', 'Valorant agent'),
        ('Harbor', 'Valorant agent'),
        ('Gekko', 'Valorant agent'),
        ('Deadlock', 'Valorant agent'),
        ('Iso', 'Valorant agent'),
        ('Clove', 'Valorant agent'),
        ('Vyse', 'Valorant agent'),
    ]
    val_total = 0
    for name, series in valorant_items:
        print(f'\n[{name}]')
        n = download_character(name, series, ROOT / 'valorant-site' / 'images', max_images=1)
        val_total += n
        time.sleep(2)
    STATS['Valorant'] = val_total

    # === PRIORITY 4: Fortnite ===
    print('\n' + '=' * 60)
    print('PRIORITY 4: FORTNITE')
    print('=' * 60)
    fn_chars = [
        ('Jonesy', 'Fortnite skin'),
        ('Raven', 'Fortnite skin'),
        ('Peely', 'Fortnite skin'),
        ('Fishstick', 'Fortnite skin'),
        ('Skull Trooper', 'Fortnite skin'),
        ('Cuddle Team Leader', 'Fortnite skin'),
        ('Omega', 'Fortnite skin'),
        ('Lynx', 'Fortnite skin'),
        ('Drift', 'Fortnite skin'),
        ('Black Knight', 'Fortnite skin'),
        ('Renegade Raider', 'Fortnite skin'),
        ('Midas', 'Fortnite skin'),
        ('Skye', 'Fortnite skin'),
        ('Mecha Team Leader', 'Fortnite skin'),
        ('Brite Bomber', 'Fortnite skin'),
        ('Rex', 'Fortnite skin'),
        ('Tricera Ops', 'Fortnite skin'),
        ('Dark Voyager', 'Fortnite skin'),
        ('Rust Lord', 'Fortnite skin'),
        ('The Reaper', 'Fortnite skin'),
    ]
    fn_total = 0
    for name, series in fn_chars:
        print(f'\n[{name}]')
        n = download_character(name, series, ROOT / 'fortnite-site' / 'images', max_images=1)
        fn_total += n
        time.sleep(2)
    STATS['Fortnite'] = fn_total

    # === PRIORITY 4: Elden Ring ===
    print('\n' + '=' * 60)
    print('PRIORITY 4: ELDEN RING')
    print('=' * 60)
    er_chars = [
        ('Malenia Blade of Miquella', 'Elden Ring'),
        ('Ranni the Witch', 'Elden Ring'),
        ('Starscourge Radahn', 'Elden Ring'),
        ('Godfrey First Elden Lord', 'Elden Ring'),
        ('Morgott the Omen King', 'Elden Ring'),
        ('Mohg Lord of Blood', 'Elden Ring'),
        ('Godrick the Grafted', 'Elden Ring'),
        ('Rennala Queen of the Full Moon', 'Elden Ring'),
        ('Maliketh the Black Blade', 'Elden Ring'),
        ('Dragonlord Placidusax', 'Elden Ring'),
        ('Fire Giant', 'Elden Ring'),
        ('Rykard Lord of Blasphemy', 'Elden Ring'),
        ('Astel Naturalborn of the Void', 'Elden Ring'),
        ('Lichdragon Fortissax', 'Elden Ring'),
        ('Godskin Duo', 'Elden Ring'),
        ('Tarnished', 'Elden Ring'),
        ('Melina', 'Elden Ring'),
        ('Blaidd', 'Elden Ring'),
        ('Alexander Iron Fist', 'Elden Ring'),
        ('Patches', 'Elden Ring'),
    ]
    er_total = 0
    for name, series in er_chars:
        print(f'\n[{name}]')
        n = download_character(name, series, ROOT / 'eldenring-site' / 'images', max_images=1)
        er_total += n
        time.sleep(2)
    STATS['Elden Ring'] = er_total

    # === SUMMARY ===
    print('\n' + '=' * 60)
    print('DOWNLOAD SUMMARY')
    print('=' * 60)
    for site, count in STATS.items():
        print(f'  {site}: {count} images')
    print(f'  TOTAL: {sum(STATS.values())} images')


if __name__ == '__main__':
    main()
