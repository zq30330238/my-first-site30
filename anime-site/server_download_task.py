"""
Server task: Download correct anime character images for anime.jycsd.com
Run: python3 anime-site/server_download_task.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.download_images import download_character, ensure_transparent, STATS
from pathlib import Path

ROOT = Path(__file__).parent.parent
ANIME_IMAGES = ROOT / 'anime-site' / 'images'
ANIME_IMAGES.mkdir(parents=True, exist_ok=True)

# Characters needed for anime.jycsd.com
# Format: (name, series, target_filename_in_anime_images)
CHARACTERS = [
    # PRIORITY 1: Demon Slayer (ALL current images are decorative garbage)
    ('Tanjiro Kamado', 'Demon Slayer', 'tanjiro.png'),
    ('Giyu Tomioka', 'Demon Slayer', 'ds_giyu.png'),
    ('Nezuko Kamado', 'Demon Slayer', 'ds_nezuko.png'),
    ('Shinobu Kocho', 'Demon Slayer', 'ds_shinobu.png'),
    ('Zenitsu Agatsuma', 'Demon Slayer', 'ds_zenitsu.png'),
    ('Inosuke Hashibira', 'Demon Slayer', 'ds_inosuke.png'),
    ('Kyojuro Rengoku', 'Demon Slayer', 'ds_rengoku.png'),
    ('Muzan Kibutsuji', 'Demon Slayer', 'ds_muzan.png'),

    # PRIORITY 2: JJK (some wrong)
    ('Yuji Itadori', 'Jujutsu Kaisen', 'yuji.png'),
    ('Satoru Gojo', 'Jujutsu Kaisen', 'jjk_gojo.png'),
    ('Ryomen Sukuna', 'Jujutsu Kaisen', 'jjk_sukuna.png'),
]

def download_and_save(name, series, target_name):
    """Download character image, verify with doubao, and save to anime-site/images/"""
    target = ANIME_IMAGES / target_name

    # Use the existing download pipeline but save directly to anime-site/images/
    n = download_character(name, series, str(ANIME_IMAGES), max_images=1)
    if n > 0:
        print(f'  ✓ Downloaded {target_name} for {name}')
        # Ensure transparency
        ensure_transparent(str(target))
        return True
    else:
        print(f'  ✗ Failed to download {name} ({target_name})')
        return False

def main():
    print('=' * 60)
    print('Anime Wiki Hub - Image Download Pipeline')
    print('Server: 206.119.168.150')
    print('=' * 60)

    success = 0
    fail = 0

    for name, series, target in CHARACTERS:
        print(f'\n[{name}] ({series}) -> {target}')
        if download_and_save(name, series, target):
            success += 1
        else:
            fail += 1
        import time
        time.sleep(3)

    print('\n' + '=' * 60)
    print(f'Done: {success} OK, {fail} failed')
    print('=' * 60)

if __name__ == '__main__':
    main()
