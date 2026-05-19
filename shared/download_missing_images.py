import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from download_images import download_character, is_valid_png
from pathlib import Path

ROOT = Path(r'd:\AI网站文件夹')

# === Missing One Piece characters ===
print('=' * 60)
print('ONE PIECE - downloading missing: blackbeard, mihawk, sabo')
print('=' * 60)
op_extra = [
    ('Marshall D. Teach', 'One Piece'),
    ('Dracule Mihawk', 'One Piece'),
    ('Sabo', 'One Piece'),
]
for name, series in op_extra:
    print(f'\n[{name}]')
    n = download_character(name, series, ROOT / 'onepiece-site' / 'images', max_images=2)
    print(f'  Downloaded: {n}')
    time.sleep(2)

# === Fortnite (all missing) ===
print('\n' + '=' * 60)
print('FORTNITE - all images missing')
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
    print(f'  Downloaded: {n}')
    time.sleep(2)

# === Elden Ring (all missing) ===
print('\n' + '=' * 60)
print('ELDEN RING - all images missing')
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
    print(f'  Downloaded: {n}')
    time.sleep(2)

# Summary
print(f'\n{"=" * 60}')
print('DOWNLOAD SUMMARY')
print(f'{"=" * 60}')
print(f'  One Piece extra: {sum(1 for _ in op_extra)}')
print(f'  Fortnite: {fn_total}')
print(f'  Elden Ring: {er_total}')
print(f'  TOTAL: {fn_total + er_total}')
