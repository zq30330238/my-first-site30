"""
batch_fix_images.py — 批量重新下载 image_mismatch_report.md 中标记的65张错误图片
使用 download_images.py 的 download_character + doubao 验证
备用方案：DuckDuckGo 图片搜索
"""

import sys, os, shutil, json, time, re, subprocess, hashlib
from pathlib import Path
from io import BytesIO

ROOT = Path(r'd:\AI网站文件夹')
sys.path.insert(0, str(ROOT / 'shared'))

# ── 导入 download_images.py 的核心函数 ──
from download_images import (
    download_character, quick_validate, verify_character,
    download_image, is_valid_png, ensure_transparent, compress_image, SESSION
)

# ── DuckDuckGo 备用 ──
try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

TMP_BASE = ROOT / '_tmp_fix'
FAILED_LOG = ROOT / 'failed_images.json'

# ── 统计 ──
stats = {
    'total_entries': 0,
    'fixed': 0,
    'pngwing_failed': 0,
    'ddgs_fixed': 0,
    'final_failed': 0,
    'skipped_logos': 0,
}
failed_list = []

# ══════════════════════════════════════════════════════════════
# 错误图片清单
# 格式: (site_dir, 错误文件名, 角色名称, 系列/作品)
# 从 image_mismatch_report.md 提取
# ══════════════════════════════════════════════════════════════

WRONG_FILES = [
    # ── naruto-site (8张 _2 变体) ──
    ('naruto-site', 'hinata-hyuga_2.png', 'Hinata Hyuga', 'Naruto'),
    ('naruto-site', 'killer-bee_2.png', 'Killer Bee', 'Naruto'),
    ('naruto-site', 'might-guy_2.png', 'Might Guy', 'Naruto'),
    ('naruto-site', 'minato-namikaze_2.png', 'Minato Namikaze', 'Naruto'),
    ('naruto-site', 'obito-uchiha_2.png', 'Obito Uchiha', 'Naruto'),
    ('naruto-site', 'orochimaru_2.png', 'Orochimaru', 'Naruto'),
    ('naruto-site', 'pain-nagato_2.png', 'Pain Nagato', 'Naruto'),
    ('naruto-site', 'sakura-haruno_2.png', 'Sakura Haruno', 'Naruto'),

    # ── onepiece-site (1 base + 6 _2) ──
    ('onepiece-site', 'crocodile.png', 'Crocodile', 'One Piece'),
    ('onepiece-site', 'boa-hancock_2.png', 'Boa Hancock', 'One Piece'),
    ('onepiece-site', 'donquixote-doflamingo_2.png', 'Donquixote Doflamingo', 'One Piece'),
    ('onepiece-site', 'portgas-d-ace_2.png', 'Portgas D. Ace', 'One Piece'),
    ('onepiece-site', 'trafalgar-law_2.png', 'Trafalgar Law', 'One Piece'),
    ('onepiece-site', 'yamato_2.png', 'Yamato', 'One Piece'),
    ('onepiece-site', 'nami_2.png', 'Nami', 'One Piece'),

    # ── dragonball-site (6 base + 1 _2) ──
    ('dragonball-site', 'android18.png', 'Android 18', 'Dragon Ball'),
    ('dragonball-site', 'chichi.png', 'Chi-Chi', 'Dragon Ball'),
    ('dragonball-site', 'bardock-dbs.png', 'Bardock', 'Dragon Ball'),
    ('dragonball-site', 'dyspo_2.png', 'Dyspo', 'Dragon Ball'),
    ('dragonball-site', 'mr-satan.png', 'Mr. Satan', 'Dragon Ball'),
    ('dragonball-site', 'pan.png', 'Pan', 'Dragon Ball'),
    ('dragonball-site', 'goten.png', 'Goten', 'Dragon Ball'),

    # ── lol-site (2+4 skin variants, 3 unique chars) ──
    ('lol-site', 'khazix_2.png', "Kha'Zix", 'League of Legends'),
    ('lol-site', 'khazix_3.png', "Kha'Zix", 'League of Legends'),
    ('lol-site', 'vayne_3.png', 'Vayne', 'League of Legends'),
    ('lol-site', 'draven_2.png', 'Draven', 'League of Legends'),
    ('lol-site', 'sylas_2.png', 'Sylas', 'League of Legends'),

    # ── fortnite-site (2 base) ──
    ('fortnite-site', 'brite-bomber.png', 'Brite Bomber', 'Fortnite'),
    ('fortnite-site', 'mecha-team-leader.png', 'Mecha Team Leader', 'Fortnite'),

    # ── games-site (skip logos, fix reynax) ──
    ('games-site', 'valorant-reyna.png', 'Reyna', 'Valorant'),

    # ── anime-site (1 base) ──
    ('anime-site', 'vegeta.png', 'Vegeta', 'Dragon Ball'),

    # ── aot-site (4 base) ──
    ('aot-site', 'bertholdt-hoover.png', 'Bertholdt Hoover', 'Attack on Titan'),
    ('aot-site', 'erwin-smith.png', 'Erwin Smith', 'Attack on Titan'),
    ('aot-site', 'hange-zoe.png', 'Hange Zoe', 'Attack on Titan'),
    ('aot-site', 'reiner-braun.png', 'Reiner Braun', 'Attack on Titan'),

    # ── valorant-site (3 base) ──
    ('valorant-site', 'chamber.png', 'Chamber', 'Valorant'),
    ('valorant-site', 'fade.png', 'Fade', 'Valorant'),
    ('valorant-site', 'iso.png', 'Iso', 'Valorant'),

    # ── eldenring-site (5 base) ──
    ('eldenring-site', 'patches.png', 'Patches', 'Elden Ring'),
    ('eldenring-site', 'tarnished.png', 'Tarnished', 'Elden Ring'),
    ('eldenring-site', 'melina.png', 'Melina', 'Elden Ring'),
    ('eldenring-site', 'astel-naturalborn-of-the-void.png', 'Astel Naturalborn of the Void', 'Elden Ring'),
    ('eldenring-site', 'godskin-duo.png', 'Godskin Duo', 'Elden Ring'),

    # ── minecraft-site (4 base) ──
    ('minecraft-site', 'crafting_table.png', 'Crafting Table', 'Minecraft'),
    ('minecraft-site', 'diamond.png', 'Diamond', 'Minecraft'),
    ('minecraft-site', 'enchanting_table.png', 'Enchanting Table', 'Minecraft'),
    ('minecraft-site', 'skeleton.png', 'Skeleton', 'Minecraft'),

    # ── hxh-site (6 base) ──
    ('hxh-site', 'feitan-portor.png', 'Feitan Portor', 'Hunter x Hunter'),
    ('hxh-site', 'kite.png', 'Kite', 'Hunter x Hunter'),
    ('hxh-site', 'knuckle-bine.png', 'Knuckle Bine', 'Hunter x Hunter'),
    ('hxh-site', 'machi-komachine.png', 'Machi Komachine', 'Hunter x Hunter'),
    ('hxh-site', 'shaiapouf.png', 'Shaiapouf', 'Hunter x Hunter'),
    ('hxh-site', 'chrollo-lucilfer.png', 'Chrollo Lucilfer', 'Hunter x Hunter'),

    # ── sao-site (6 base) ──
    ('sao-site', 'dark-repulser.png', 'Dark Repulser', 'Sword Art Online'),
    ('sao-site', 'elucidator.png', 'Elucidator', 'Sword Art Online'),
    ('sao-site', 'mothers-rosario.png', "Mother's Rosario", 'Sword Art Online'),
    ('sao-site', 'kikuoka.png', 'Kikuoka', 'Sword Art Online'),
    ('sao-site', 'quinella.png', 'Quinella', 'Sword Art Online'),
    ('sao-site', 'agil.png', 'Agil', 'Sword Art Online'),

    # ── tokyoghoul-site (3 base) ──
    ('tokyoghoul-site', 'juuzou-suzuya.png', 'Juuzou Suzuya', 'Tokyo Ghoul'),
    ('tokyoghoul-site', 'koutarou-amon.png', 'Koutarou Amon', 'Tokyo Ghoul'),
    ('tokyoghoul-site', 'seidou-takizawa.png', 'Seidou Takizawa', 'Tokyo Ghoul'),
]

# Logo images that need special handling (not character-based)
LOGO_FILES = {
    ('games-site', 'bg3-logo.png'): ('Baldur Gate 3 logo', 'Baldur Gate 3 game'),
    ('games-site', 'minecraft-logo.png'): ('Minecraft logo', 'Minecraft game'),
}


def compute_slug(char_name):
    """Compute the slug as download_character would."""
    return char_name.lower().replace(' ', '-').replace('.', '').replace("'", '')


def extract_suffix(filename):
    """Extract _N suffix from filename. Returns (base_name, N) or (base_name, 0)."""
    m = re.search(r'_(\d+)\.png$', filename)
    if m:
        base = filename[:m.start()]
        return base, int(m.group(1))
    base = filename.replace('.png', '')
    return base, 0


def get_download_source_name(slug, suffix_n):
    """
    Map existing _N suffix to download_character's naming.
    Existing _2.png → download's slug_1.png (2nd download)
    Existing _3.png → download's slug_2.png (3rd download)
    Existing slug.png (no suffix) → download's slug.png (1st download)
    """
    if suffix_n == 0:
        return f'{slug}.png'
    # download_character naming: first=slug.png, second=slug_1.png, third=slug_2.png
    # Existing _N = download's slug_{N-1}.png (for N >= 2)
    src_name = f'{slug}_{suffix_n - 1}.png'
    return src_name


def delete_wrong_file(site_dir, filename):
    """Delete wrong image file if it exists, with retry for Windows locks."""
    fpath = site_dir / filename
    if not fpath.exists():
        return 0
    size = os.path.getsize(fpath)
    for attempt in range(3):
        try:
            fpath.unlink()
            return size
        except PermissionError:
            if attempt < 2:
                print(f'   [LOCKED] {filename}: retrying in 2s...')
                time.sleep(2)
            else:
                print(f'   [LOCKED] {filename}: could not delete after 3 attempts, skipping')
        except OSError:
            if attempt < 2:
                print(f'   [LOCKED] {filename}: OS error, retrying in 2s...')
                time.sleep(2)
            else:
                print(f'   [LOCKED] {filename}: could not delete after 3 attempts, skipping')
    return 0


def download_with_ddgs(char_name, series, target_path):
    """
    DuckDuckGo fallback: search images, download, verify with doubao.
    Returns True if successful.
    """
    if not HAS_DDGS:
        return False

    query = f'{char_name} {series} PNG transparent'
    print(f'  [DDGS] Searching: "{query}"')

    try:
        ddgs = DDGS()
        results = list(ddgs.images(query, max_results=5))
    except Exception as e:
        print(f'  [DDGS] Search error: {e}')
        return False

    if not results:
        # Try simpler query
        try:
            ddgs = DDGS()
            results = list(ddgs.images(f'{char_name} character render', max_results=5))
        except Exception as e:
            print(f'  [DDGS] Fallback search error: {e}')
            return False

    if not results:
        print(f'  [DDGS] No results')
        return False

    for img in results:
        url = img.get('image', '')
        if not url:
            continue
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code != 200 or len(r.content) < 10240:
                continue

            # Save temp
            temp_path = Path(str(target_path) + '.tmp')
            with open(temp_path, 'wb') as f:
                f.write(r.content)

            # Quick validate
            passed, reason = quick_validate(str(temp_path))
            if not passed:
                temp_path.unlink(missing_ok=True)
                continue

            # Doubao verify
            if verify_character(str(temp_path), char_name, series):
                shutil.copy2(str(temp_path), str(target_path))
                temp_path.unlink(missing_ok=True)
                ensure_transparent(str(target_path))
                compress_image(str(target_path))
                print(f'  [DDGS PASS] saved {Path(target_path).name}')
                return True
            else:
                temp_path.unlink(missing_ok=True)
        except Exception as e:
            print(f'  [DDGS ERR] {url[:80]}: {e}')
            continue

    return False


def download_logo(target_path, logo_name, game_name):
    """Download a game logo image."""
    query = f'{logo_name} PNG transparent'
    print(f'  [LOGO] Searching: "{query}"')

    # Try DuckDuckGo first
    if HAS_DDGS:
        try:
            ddgs = DDGS()
            results = list(ddgs.images(query, max_results=5))
            for img in results:
                url = img.get('image', '')
                if not url:
                    continue
                try:
                    r = SESSION.get(url, timeout=15)
                    if r.status_code == 200 and len(r.content) > 10240:
                        with open(target_path, 'wb') as f:
                            f.write(r.content)
                        if is_valid_png(target_path):
                            sz = os.path.getsize(target_path)
                            print(f'  [LOGO] saved {target_path.name} ({sz//1024}KB)')
                            return True
                except:
                    continue
        except Exception as e:
            print(f'  [LOGO] DDGS error: {e}')

    # Also try pngwing
    from download_images import search_pngwing
    urls = search_pngwing(query)
    for url in urls:
        try:
            r = SESSION.get(url, timeout=15)
            if r.status_code == 200 and len(r.content) > 10240 and r.content[:4] == b'\x89PNG':
                with open(target_path, 'wb') as f:
                    f.write(r.content)
                if is_valid_png(target_path):
                    print(f'  [LOGO] saved from pngwing')
                    return True
        except:
            continue

    return False


def process_group(site, char_name, series, wrong_files):
    """
    Process a group of wrong files for the same (site, char_name, series).
    Returns (fixed_count, failed_list_for_this_group).
    """
    site_dir = ROOT / site / 'images'
    if not site_dir.exists():
        print(f'  [SKIP] {site}/images/ not found')
        return 0, wrong_files

    slug = compute_slug(char_name)

    # Determine max_images needed
    max_n = 0
    rename_map = {}  # {dest_filename: source_temp_filename}

    for fname in wrong_files:
        base_name, suffix_n = extract_suffix(fname)
        max_n = max(max_n, suffix_n)

        # Source file in temp dir
        src_name = get_download_source_name(slug, suffix_n)
        rename_map[fname] = src_name

    # max_images needed in download_character
    # For _2 suffix: need 2 downloads → slug_1.png
    # For _3 suffix: need 3 downloads → slug_2.png
    # So max_images = max_n (suffix N → need N downloads)
    max_images = max(1, max_n)

    # Check for name mismatch (slug vs expected filename)
    name_mismatch = False
    for fname in wrong_files:
        # Compare base name (without suffix) to slug
        base_name, _ = extract_suffix(fname)
        if base_name != slug:
            name_mismatch = True

    print(f'\n── {site}: {char_name} ({series}) ──')
    print(f'   Wrong files: {", ".join(wrong_files)}')
    print(f'   Slug: {slug}, Max images needed: {max_images}')

    # ── Step 1: Delete wrong files ──
    total_deleted = 0
    for fname in wrong_files:
        sz = delete_wrong_file(site_dir, fname)
        if sz > 0:
            total_deleted += 1
            print(f'   Deleted {fname} ({sz//1024}KB)')
    if total_deleted == 0:
        print(f'   (no files to delete)')

    # ── Step 2: Download to temp dir ──
    tmp_dir = TMP_BASE / site / slug
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    print(f'   Downloading to temp: {tmp_dir}...')
    try:
        downloaded_count = download_character(char_name, series, str(tmp_dir), max_images=max_images)
    except Exception as e:
        print(f'   [ERROR] download_character crashed: {e}')
        downloaded_count = 0

    if downloaded_count == 0:
        # PNGWing failed completely, try DuckDuckGo fallback
        print(f'   [FALLBACK] PNGWing returned 0 images, trying DuckDuckGo...')

        ddgs_success = 0
        for fname, src_name in rename_map.items():
            target_path = site_dir / fname
            if download_with_ddgs(char_name, series, target_path):
                ddgs_success += 1

        if ddgs_success > 0:
            print(f'   [DDGS] Fixed {ddgs_success}/{len(wrong_files)} files')
            return ddgs_success, []
        else:
            print(f'   [FAILED] Both PNGWing and DDGS failed for {char_name}')
            return 0, wrong_files

    # ── Step 3: Copy verified images to site dir with correct names ──
    fixed = 0
    failed_for_char = []

    for fname, src_name in rename_map.items():
        src_path = tmp_dir / src_name
        dst_path = site_dir / fname

        if src_path.exists():
            try:
                shutil.copy2(str(src_path), str(dst_path))
                sz = os.path.getsize(dst_path)
                print(f'   [OK] {fname} ({sz//1024}KB) ← {src_name}')
                fixed += 1
            except (PermissionError, OSError) as e:
                print(f'   [LOCKED] {fname}: copy failed ({e}), trying DDGS fallback...')
                if download_with_ddgs(char_name, series, dst_path):
                    fixed += 1
                else:
                    failed_for_char.append(fname)
        else:
            # Try to find any downloaded file and use it
            downloaded_files = list(tmp_dir.glob('*.png'))
            if downloaded_files:
                # Use the first (or any) downloaded image
                shutil.copy2(str(downloaded_files[0]), str(dst_path))
                sz = os.path.getsize(dst_path)
                print(f'   [OK] {fname} ({sz//1024}KB) ← {downloaded_files[0].name} (fallback)')
                fixed += 1
            else:
                print(f'   [FAIL] {fname}: no source file {src_name}')
                failed_for_char.append(fname)

    return fixed, failed_for_char


def process_logos():
    """Handle logo images separately."""
    fixed = 0
    failed = []

    print('\n' + '=' * 60)
    print('LOGO IMAGES (special handling)')
    print('=' * 60)

    for (site, fname), (logo_name, game_name) in LOGO_FILES.items():
        site_dir = ROOT / site / 'images'
        if not (site_dir / fname).exists():
            print(f'  [SKIP] {site}/{fname} does not exist')
            continue

        print(f'\n── {site}: {fname} ──')

        # Delete old
        sz = delete_wrong_file(site_dir, fname)
        if sz > 0:
            print(f'  Deleted old file ({sz//1024}KB)')

        # Download logo
        if download_logo(site_dir / fname, logo_name, game_name):
            fixed += 1
            print(f'  [OK] Logo saved')
        else:
            failed.append((site, fname))
            print(f'  [FAIL] Could not download logo')

    return fixed, failed


def main():
    print('=' * 60)
    print('BATCH FIX WRONG IMAGES')
    print('=' * 60)

    # Clear failed log
    if FAILED_LOG.exists():
        old_failed = json.loads(FAILED_LOG.read_text()) if FAILED_LOG.read_text().strip() else {}
    else:
        old_failed = {}
    print(f'Previous failed_images.json entries: {len(old_failed)}')

    start_time = time.time()

    # ── Group wrong files by (site, char_name, series) ──
    groups = {}
    for site, fname, char_name, series in WRONG_FILES:
        key = (site, char_name, series)
        if key not in groups:
            groups[key] = []
        groups[key].append(fname)

    print(f'\nTotal entries to fix: {len(WRONG_FILES)}')
    print(f'Unique character downloads: {len(groups)}')

    # ── Process each group ──
    total_fixed = 0
    total_pngwing_failed = 0
    total_ddgs_fixed = 0
    total_final_failed = 0

    for idx, ((site, char_name, series), wrong_files) in enumerate(groups.items(), 1):
        print(f'\n[{idx}/{len(groups)}] ', end='')
        try:
            fixed, failed_files = process_group(site, char_name, series, wrong_files)
        except Exception as e:
            print(f'[ERROR] process_group crashed for {char_name}: {e}')
            import traceback
            traceback.print_exc()
            fixed = 0
            failed_files = wrong_files
            total_pngwing_failed += 1
        total_fixed += fixed

        if fixed < len(wrong_files):
            total_pngwing_failed += 1
            # Try DuckDuckGo for failed ones
            site_dir = ROOT / site / 'images'
            for fname in failed_files:
                print(f'   [DDGS RETRY] {fname}...')
                try:
                    if download_with_ddgs(char_name, series, site_dir / fname):
                        total_fixed += 1
                        total_ddgs_fixed += 1
                    else:
                        total_final_failed += 1
                        failed_list.append((site, fname, char_name, series))
                except Exception as e:
                    print(f'   [DDGS ERROR] {fname}: {e}')
                    total_final_failed += 1
                    failed_list.append((site, fname, char_name, series))

        # Small delay between characters
        time.sleep(1.0)

    # ── Process logos ──
    logo_fixed, logo_failed = process_logos()
    total_fixed += logo_fixed

    # ── Report ──
    elapsed = time.time() - start_time

    print('\n' + '=' * 60)
    print('FIX RESULTS')
    print('=' * 60)
    print(f'  Total entries:          {len(WRONG_FILES) + len(LOGO_FILES)}')
    print(f'  Fixed via PNGWing:      {total_fixed - total_ddgs_fixed}')
    print(f'  Fixed via DDGS:         {total_ddgs_fixed}')
    print(f'  Logo fixes:             {logo_fixed}')
    print(f'  Final failures:         {total_final_failed}')
    print(f'  Time:                   {elapsed:.0f}s')

    if failed_list:
        print('\n── FAILED ITEMS (need manual fix) ──')
        for site, fname, char_name, series in failed_list:
            print(f'  {site}/{fname} → {char_name} ({series})')
        print(f'\nTotal: {len(failed_list)} items still wrong')

    # ── Cleanup temp ──
    if TMP_BASE.exists():
        shutil.rmtree(TMP_BASE)
        print(f'\nCleaned up temp directory')

    print('\nDone.')


if __name__ == '__main__':
    main()
