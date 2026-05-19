import requests, re, os, time, hashlib
from pathlib import Path

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

    queries = [
        f'{char_name} {series}',
        f'{char_name} {series} character',
        f'{char_name} {series} transparent',
    ]

    seen_urls = set()
    for query in queries:
        if downloaded >= max_images:
            break
        print(f'  Searching: "{query}"')
        urls = search_pngwing(query)
        # Filter: URL must contain at least one keyword from character name
        relevant = [u for u in urls if any(k in u.lower() for k in keywords)]
        subtle = [u for u in urls if u not in relevant]
        urls = relevant + subtle
        for url in urls:
            if downloaded >= max_images:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)
            suffix = f'_{downloaded+1}' if downloaded > 0 else ''
            fname = f'{slug}{suffix}.png'
            fpath = out_dir / fname
            result = download_image(url, str(fpath))
            if result == 'ok':
                sz = os.path.getsize(str(fpath))
                print(f'    OK: {fname} ({sz//1024}KB)')
                downloaded += 1
            elif result == 'exists':
                print(f'    SKIP: {fname} (already valid)')
                downloaded += 1
            else:
                continue
        time.sleep(1.5)

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
