import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from download_images import download_character, is_valid_png, SEEN_HASHES
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')
DEST = ROOT / 'dragonball-site' / 'images'
SERIES_DBZ = 'Dragon Ball Z'
SERIES_DBS = 'Dragon Ball Super'
SERIES_DB = 'Dragon Ball'
SERIES_GT = 'Dragon Ball GT'

STATS = {'p1_done': [], 'p1_fail': [], 'p2_done': [], 'p2_fail': []}

def download_one(name, series, max_n=1):
    print(f'\n  [{name}]')
    n = download_character(name, series, DEST, max_images=max_n)
    time.sleep(2)
    if n > 0:
        slug = name.lower().replace(' ', '-').replace('.', '').replace("'", '').replace('(', '').replace(')', '')
        print(f'  [OK] {name} -> {slug}.png')
        return True
    else:
        print(f'  [FAIL] {name} -> no image found')
        return False

def batch_download(char_list, label, stat_key_done, stat_key_fail):
    total = len(char_list)
    for i, (name, series) in enumerate(char_list):
        print(f'\n--- {label} [{i+1}/{total}] ---')
        ok = download_one(name, series)
        if ok:
            STATS[stat_key_done].append(name)
        else:
            STATS[stat_key_fail].append(name)
        if (i + 1) % 10 == 0:
            print(f'\n  [PROGRESS] {label}: {i+1}/{total} done')

# ============================================================
# PRIORITY 1 — Independent Core Characters (40)
# ============================================================
P1 = [
    # Saiyan Saga / Saiyans
    ('Raditz', SERIES_DBZ),
    ('Nappa', SERIES_DBZ),
    ('Bardock', SERIES_DBZ),
    ('Gine', SERIES_DBZ),
    ('King Vegeta', SERIES_DBZ),
    ('Paragus', SERIES_DBZ),
    ('Tarble', SERIES_DBZ),
    # Movie villains
    ('Cooler', SERIES_DBZ),
    ('Turles', SERIES_DBZ),
    ('Bojack', SERIES_DBZ),
    ('Janemba', SERIES_DBZ),
    ('Lord Slug', SERIES_DBZ),
    ('Hirudegarn', SERIES_DBZ),
    ('Tapion', SERIES_DBZ),
    ('Garlic Jr.', SERIES_DBZ),
    ('Dr. Wheelo', SERIES_DBZ),
    ('Hatchiyack', SERIES_DBZ),
    # Androids
    ('Android 16', SERIES_DBZ),
    ('Android 17', SERIES_DBZ),
    ('Android 19', SERIES_DBZ),
    ('Dr. Gero', SERIES_DBZ),
    # Buu Saga villains
    ('Dabura', SERIES_DBZ),
    ('Babidi', SERIES_DBZ),
    ('Supreme Kai', SERIES_DBZ),
    ('Kibito', SERIES_DBZ),
    ('Zarbon', SERIES_DBZ),
    ('Dodoria', SERIES_DBZ),
    ('Captain Ginyu', SERIES_DBZ),
    ('Recoome', SERIES_DBZ),
    # Supporting heroes
    ('Kid Trunks', SERIES_DBZ),
    ('Videl', SERIES_DBZ),
    ('Mr. Satan', SERIES_DBZ),
    ('Yajirobe', SERIES_DB),
    ('Korin', SERIES_DB),
    ('Mr. Popo', SERIES_DB),
    ('Kami', SERIES_DB),
    ('King Piccolo', SERIES_DB),
    ('Future Trunks', SERIES_DBZ),
]

# ============================================================
# PRIORITY 2 — Important but flexible (30)
# ============================================================
P2 = [
    # Ginyu Force remaining
    ('Jeice', SERIES_DBZ),
    ('Burter', SERIES_DBZ),
    ('Guldo', SERIES_DBZ),
    ('King Cold', SERIES_DBZ),
    # Universe 6
    ('Cabba', SERIES_DBS),
    ('Caulifla', SERIES_DBS),
    ('Kale', SERIES_DBS),
    ('Hit', SERIES_DBS),
    ('Kefla', SERIES_DBS),
    ('Toppo', SERIES_DBS),
    # GT
    ('Pan GT', SERIES_GT),
    ('Giru', SERIES_GT),
    ('Omega Shenron', SERIES_GT),
    # Daima
    ('Glorio', SERIES_DB),
    ('Panzy', SERIES_DB),
    ('King Gomah', SERIES_DB),
    # Other World
    ('Pikkon', SERIES_DBZ),
    ('King Yemma', SERIES_DBZ),
    ('Grand Kai', SERIES_DBZ),
    # Galactic Patrol / Moro arc
    ('Jaco', SERIES_DBS),
    ('Merus', SERIES_DBS),
    ('Granolah', SERIES_DBS),
    ('Gas', SERIES_DBS),
    ('Moro', SERIES_DBS),
    ('Seven-Three', SERIES_DBS),
    # GT villains
    ('General Rilldo', SERIES_GT),
    ('Baby', SERIES_GT),
    ('Super 17', SERIES_GT),
    # Misc
    ('Cell Juniors', SERIES_DBZ),
    ('Oolong', SERIES_DB),
    ('Puar', SERIES_DB),
    ('Emperor Pilaf', SERIES_DB),
    ('Shu', SERIES_DB),
    ('Mai', SERIES_DBS),
]

# ============================================================
# PRE-LOAD EXISTING HASHES (dedup against already downloaded images)
# ============================================================
for fpath in DEST.glob('*.png'):
    try:
        with open(fpath, 'rb') as f:
            import hashlib
            SEEN_HASHES.add(hashlib.md5(f.read()).hexdigest())
    except:
        pass
print(f'Loaded {len(SEEN_HASHES)} existing hashes for dedup')

# ============================================================
# EXECUTE
# ============================================================
print('=' * 60)
print('PRIORITY 1: Core Characters (40)')
print('=' * 60)
batch_download(P1, 'P1', 'p1_done', 'p1_fail')

print('\n' + '=' * 60)
print('PRIORITY 2: Important Characters (30+)')
print('=' * 60)
batch_download(P2, 'P2', 'p2_done', 'p2_fail')

# ============================================================
# SUMMARY
# ============================================================
print('\n' + '=' * 60)
print('DOWNLOAD SUMMARY — Dragon Ball')
print('=' * 60)
print(f'\nP1 ({len(P1)} chars):')
print(f'  SUCCESS ({len(STATS["p1_done"])}): {", ".join(STATS["p1_done"])}')
print(f'  FAILED ({len(STATS["p1_fail"])}): {", ".join(STATS["p1_fail"])}')

print(f'\nP2 ({len(P2)} chars):')
print(f'  SUCCESS ({len(STATS["p2_done"])}): {", ".join(STATS["p2_done"])}')
print(f'  FAILED ({len(STATS["p2_fail"])}): {", ".join(STATS["p2_fail"])}')

total_ok = len(STATS['p1_done']) + len(STATS['p2_done'])
total_fail = len(STATS['p1_fail']) + len(STATS['p2_fail'])
print(f'\nTOTAL: {total_ok} ok, {total_fail} failed, {total_ok + total_fail} attempted')

# Verify existing + new count
final_count = len(list(DEST.glob('*.png')))
print(f'Total PNG files in directory: {final_count}')
