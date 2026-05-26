#!/usr/bin/env python3
"""
Download images for ALL clothing-site pages using Wikimedia Commons API (free, no key).
Each ethnic group and topic page gets its own unique images.

Strategy:
1. Primary: Wikimedia Commons search (free license, real photos)
2. Fallback: loremflickr.com (tag-based Flickr photos)
3. Final fallback: Generate solid-color placeholder with text overlay
"""

import os, json, re, time, hashlib, sys, random
import requests
from io import BytesIO

BASE_DIR = r"d:\AI网站文件夹\clothing-site"
IMAGE_DIR = os.path.join(BASE_DIR, "images")
ETHNIC_DATA = os.path.join(BASE_DIR, "ethnic_data.json")

os.makedirs(IMAGE_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
WIKI_UA = "MyersFashionBot/1.0 (image downloader; zq30330238@gmail.com)"


# ============================================================
# DOWNLOAD FUNCTIONS
# ============================================================

def search_wikimedia(query, limit=3):
    """Search Wikimedia Commons for images matching query. Returns list of image URLs."""
    params = {
        "action": "query", "format": "json",
        "generator": "search", "gsrnamespace": 6,
        "gsrsearch": query, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|size",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": WIKI_UA}, timeout=15)
        r.raise_for_status()
        data = r.json()
        urls = []
        if "query" in data and "pages" in data["query"]:
            pages = sorted(data["query"]["pages"].values(), key=lambda x: int(x.get("index", 9999)))
            for pinfo in pages:
                if "imageinfo" in pinfo:
                    ii = pinfo["imageinfo"][0]
                    url = ii.get("url", "")
                    size = ii.get("size", 0)
                    if url and size > 10240:  # >10KB
                        urls.append(url)
        return urls
    except Exception:
        return []


def search_loremflickr(query, limit=1):
    """Download random image from loremflickr based on tags. Returns list of URLs."""
    # loremflickr returns a single image per request, so call multiple times
    urls = []
    for i in range(limit):
        kw = query.replace(" ", ",")[:80]  # limit tag length
        url = f"https://loremflickr.com/1200/800/{kw}?random={i}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 20480:
                # Save to temp to check if it's a real image or default placeholder
                temp_path = os.path.join(IMAGE_DIR, f"_tmp_{i}_{hash(kw)}.jpg")
                with open(temp_path, "wb") as f:
                    f.write(r.content)
                # Check file size - default placeholder is ~104KB, real images vary
                if os.path.getsize(temp_path) > 25000:  # larger than default placeholder
                    urls.append(temp_path)  # already saved
                else:
                    os.remove(temp_path)
            if i < limit - 1:
                time.sleep(1)
        except Exception:
            pass
    return urls


def download_from_url(url, save_path, max_retries=2):
    """Download an image from URL to local path. Returns True on success."""
    if os.path.exists(save_path) and os.path.getsize(save_path) > 10240:
        return True

    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and len(r.content) > 10240:
                # Determine extension from content type
                ct = r.headers.get("content-type", "")
                if "png" in ct:
                    ext = ".png"
                elif "jpeg" in ct or "jpg" in ct:
                    ext = ".jpg"
                elif "webp" in ct:
                    ext = ".webp"
                else:
                    ext = ".jpg"

                final_path = save_path.rsplit(".", 1)[0] + ext
                with open(final_path, "wb") as f:
                    f.write(r.content)
                size_kb = len(r.content) / 1024
                print(f"  [OK] {os.path.basename(final_path)} ({size_kb:.0f}KB)")
                return True
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2)
    return False


def get_images_for_group(keywords, save_prefix, count=3):
    """
    Get `count` images for a group using multiple strategies.
    Returns number of images successfully downloaded.
    """
    success = 0
    suffixes = ["hero", "detail", "festival"]

    # Strategy 1: Wikimedia Commons
    print(f"  Searching Wikimedia for: {keywords[:60]}...")
    wiki_urls = search_wikimedia(keywords, limit=count * 2)  # get extras in case some fail
    random.shuffle(wiki_urls)  # get variety

    for i in range(count):
        save_path = os.path.join(IMAGE_DIR, f"{save_prefix}_{suffixes[i]}.jpg")
        if os.path.exists(save_path) and os.path.getsize(save_path) > 10240:
            print(f"  [SKIP] {save_prefix}_{suffixes[i]}.jpg exists")
            success += 1
            continue

        # Try Wikimedia URLs
        downloaded = False
        if i < len(wiki_urls):
            print(f"  Downloading from Wikimedia: {save_prefix}_{suffixes[i]}.jpg...")
            if download_from_url(wiki_urls[i], save_path):
                success += 1
                downloaded = True

        # Strategy 2: Try loremflickr as fallback
        if not downloaded:
            print(f"  Fallback to loremflickr: {save_prefix}_{suffixes[i]}.jpg...")
            lf_result = search_loremflickr(keywords, limit=1)
            if lf_result and os.path.exists(lf_result[0]):
                os.rename(lf_result[0], save_path)
                print(f"  [OK] {save_prefix}_{suffixes[i]}.jpg (loremflickr)")
                success += 1
                downloaded = True

        # Strategy 3: Try broader Wikimedia search
        if not downloaded:
            broad_kw = keywords.split(" ")[:3]  # first 3 words only
            broad_kw = " ".join(broad_kw) + " costume"
            print(f"  Broader Wikimedia search: {broad_kw}...")
            broad_urls = search_wikimedia(broad_kw, limit=3)
            if broad_urls and i < len(broad_urls):
                if download_from_url(broad_urls[i], save_path):
                    success += 1
                    downloaded = True

        # Strategy 4: Ultimate fallback - search by ethnic group name only
        if not downloaded:
            just_name = keywords.split(" ")[0] + " " + keywords.split(" ")[1] if len(keywords.split(" ")) > 1 else keywords.split(" ")[0]
            just_name = just_name.strip(" ,")
            print(f"  Final fallback: {just_name}...")
            fallback_urls = search_wikimedia(just_name, limit=5)
            if fallback_urls:
                if download_from_url(fallback_urls[i % len(fallback_urls)], save_path):
                    success += 1

        if not downloaded:
            print(f"  [FAIL] {save_prefix}_{suffixes[i]}.jpg - no source found")

        time.sleep(1)  # polite delay between requests

    return success


# ============================================================
# BUILD MANIFESTS
# ============================================================

def build_ethnic_manifest():
    """Build manifest for 56 ethnic groups from JSON data."""
    with open(ETHNIC_DATA, encoding="utf-8") as f:
        data = json.load(f)
    return [(key, info["image_keywords"]) for key, info in data.items()]


ETHNIC_MANIFEST = None  # lazy load

# Non-ethnic page keyword mapping
NON_ETHNIC_PAGES = [
    ("han-dynasty", "Han Dynasty ancient Chinese clothing hanfu silk robe traditional"),
    ("tang-dynasty", "Tang Dynasty Chinese clothing ancient silk dress traditional"),
    ("song-dynasty", "Song Dynasty Chinese clothing hanfu elegant traditional"),
    ("ming-dynasty", "Ming Dynasty Chinese clothing hanfu horse-face skirt traditional"),
    ("qing-dynasty", "Qing Dynasty Chinese clothing qipao Manchu robe traditional"),
    ("dragon-phoenix", "Chinese dragon phoenix wedding attire traditional embroidered"),
    ("qipao-history", "Chinese qipao cheongsam silk dress traditional elegant"),
    ("tang-suit", "Chinese tang suit jacket mandarin collar silk traditional"),
    ("zhongshan-suit", "Chinese Zhongshan suit Mao suit mandarin collar formal"),
    ("eastern-western-wedding", "wedding dress bride gown Chinese red white western comparison"),
    ("qipao-vs-evening-dress", "qipao cheongsam evening gown dress comparison fashion"),
    ("blazer", "blazer jacket tailored suit fashion classic wardrobe"),
    ("cashmere-sweater", "cashmere sweater knitwear luxury wool fashion"),
    ("little-black-dress", "little black dress LBD evening formal fashion classic"),
    ("trench-coat", "trench coat Burberry style classic outerwear fashion"),
    ("white-shirt", "white shirt button-up blouse classic wardrobe essential"),
    ("ballet-flats", "ballet flats shoes flat ballerina classic women fashion"),
    ("jeans", "jeans denim pants classic wardrobe casual fashion"),
    ("london-ss2026", "London fashion week Spring Summer runway avant-garde streetwear"),
    ("milan-fw2026", "Milan fashion week Fall Winter runway Italian luxury tailoring"),
    ("ny-fw2026", "New York fashion week Fall Winter runway American sportswear"),
    ("paris-ss2026", "Paris fashion week Spring Summer runway haute couture luxury"),
]


# ============================================================
# UPDATE HTML FILES
# ============================================================

def get_image_refs(filepath):
    """Find all /images/ references in an HTML file, in order."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    refs = re.findall(r'(/images/[\w.-]+\.(?:jpg|png|webp))', content)
    return refs, content


def replace_image_refs(filepath, new_prefix, count=3):
    """
    Replace sequential image references in an HTML file.
    Ref 1 -> {new_prefix}_hero.jpg
    Ref 2 -> {new_prefix}_detail.jpg
    Ref 3 -> {new_prefix}_festival.jpg
    """
    refs, content = get_image_refs(filepath)
    if not refs:
        return False

    suffixes = ["hero", "detail", "festival"]
    original = content

    for i, old_ref in enumerate(refs):
        if i >= count:
            break
        new_ref = f"/images/{new_prefix}_{suffixes[i]}.jpg"
        content = content.replace(old_ref, new_ref, 1)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


# ============================================================
# FASHION WEEK INDEX (direct Unsplash photo URLs)
# ============================================================

FW_INDEX_PATH = os.path.join(BASE_DIR, "western", "fashion-week-trends", "index.html")
FW_PHOTOS = [
    ("paris-fashion-week_hero.jpg", "1509631179647-0177331693ae", "Paris Fashion Week runway"),
    ("milan-fashion-week_hero.jpg", "1490481651871-ab68de25d43d", "Milan Fashion Week runway"),
    ("london-fashion-week_hero.jpg", "1539109136881-3be0616acf4b", "London Fashion Week runway"),
    ("newyork-fashion-week_hero.jpg", "1551488831-00ddcb6c6bd3", "New York Fashion Week runway"),
]


def download_fw_photos():
    """Download the specific Unsplash photos used in fashion week index."""
    ok = 0
    for filename, photo_id, alt in FW_PHOTOS:
        fpath = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 10240:
            print(f"  [SKIP] {filename} exists")
            ok += 1
            continue

        # Try multiple sizes
        for size in ["w=1600&h=900&fit=crop", "w=1200&h=800&fit=crop"]:
            url = f"https://images.unsplash.com/photo-{photo_id}?{size}"
            try:
                r = requests.get(url, headers=HEADERS, timeout=20)
                if r.status_code == 200 and len(r.content) > 20480:
                    with open(fpath, "wb") as f:
                        f.write(r.content)
                    print(f"  [OK] {filename} ({len(r.content)/1024:.0f}KB)")
                    ok += 1
                    break
            except:
                continue
        else:
            print(f"  [FAIL] {filename}")
        time.sleep(1)
    return ok


def update_fw_index():
    """Replace Unsplash URLs with local paths in fashion week index."""
    with open(FW_INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    replacements = [
        ("1509631179647-0177331693ae", "paris-fashion-week_hero"),
        ("1490481651871-ab68de25d43d", "milan-fashion-week_hero"),
        ("1539109136881-3be0616acf4b", "london-fashion-week_hero"),
        ("1551488831-00ddcb6c6bd3", "newyork-fashion-week_hero"),
    ]

    for pid, local_name in replacements:
        pattern = rf'https://images\.unsplash\.com/photo-{re.escape(pid)}\?[^"\']+'
        content = re.sub(pattern, f"/images/{local_name}.jpg", content)

    if content != original:
        with open(FW_INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


# ============================================================
# MD5 DEDUP
# ============================================================

def deduplicate():
    hashes = {}
    removed = 0
    for fname in sorted(os.listdir(IMAGE_DIR)):
        if not fname.endswith((".jpg", ".png", ".webp")) or fname.startswith("_"):
            continue
        fpath = os.path.join(IMAGE_DIR, fname)
        with open(fpath, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        if md5 in hashes:
            os.remove(fpath)
            print(f"  [DEDUP] {fname} -> duplicate of {hashes[md5]}")
            removed += 1
        else:
            hashes[md5] = fname
    return removed


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("CLOTHING-SITE IMAGE DOWNLOAD")
    print("Source: Wikimedia Commons + Fallbacks")
    print("=" * 60)

    eth_ok, eth_fail = 0, 0
    non_ok, non_fail = 0, 0
    fw_ok = 0

    # ---- Phase 1: Ethnic groups ----
    print("\n=== Phase 1: Ethnic Groups (56) ===")
    with open(ETHNIC_DATA, encoding="utf-8") as f:
        ethnic_data = json.load(f)

    for idx, (key, info) in enumerate(ethnic_data.items(), 1):
        keywords = info["image_keywords"]
        name_en = info["name_en"]
        print(f"\n[{idx}/56] {name_en} ({key})")

        existing = sum(1 for s in ["hero", "detail", "festival"]
                       if os.path.exists(os.path.join(IMAGE_DIR, f"{key}_{s}.jpg"))
                       and os.path.getsize(os.path.join(IMAGE_DIR, f"{key}_{s}.jpg")) > 10240)
        if existing == 3:
            print(f"  All 3 images exist, skipping")
            eth_ok += 3
            continue

        n = get_images_for_group(keywords, key, count=3)
        eth_ok += n
        eth_fail += (3 - n)

    # ---- Phase 2: Non-ethnic pages ----
    print("\n\n=== Phase 2: Other Pages ({}) ===".format(len(NON_ETHNIC_PAGES)))
    for idx, (base, keywords) in enumerate(NON_ETHNIC_PAGES, 1):
        print(f"\n[{idx}/{len(NON_ETHNIC_PAGES)}] {base}")

        existing = sum(1 for s in ["hero", "detail", "festival"]
                       if os.path.exists(os.path.join(IMAGE_DIR, f"{base}_{s}.jpg"))
                       and os.path.getsize(os.path.join(IMAGE_DIR, f"{base}_{s}.jpg")) > 10240)
        if existing == 3:
            print(f"  All 3 images exist, skipping")
            non_ok += 3
            continue

        n = get_images_for_group(keywords, base, count=3)
        non_ok += n
        non_fail += (3 - n)

    # ---- Phase 3: Fashion week index photos ----
    print("\n\n=== Phase 3: Fashion Week Index Photos ===")
    fw_ok = download_fw_photos()

    # ---- Phase 4: MD5 Dedup ----
    print("\n\n=== Phase 4: MD5 Deduplication ===")
    dedup_count = deduplicate()

    # ---- Phase 5: Update HTML files ----
    print("\n\n=== Phase 5: Update HTML References ===")

    # 5a: Fashion week index
    print("\n[Fashion Week Index]")
    fw_updated = update_fw_index()
    print(f"  {'Updated' if fw_updated else 'No changes needed'}")

    # 5b: Ethnic group pages
    print("\n[Ethnic Group Pages]")
    eth_dir = os.path.join(BASE_DIR, "chinese", "56-ethnic-groups")
    eth_upd, eth_skip = 0, 0
    for fname in sorted(os.listdir(eth_dir)):
        if not fname.endswith(".html") or fname == "index.html":
            continue
        key = fname.replace(".html", "")
        fpath = os.path.join(eth_dir, fname)
        if replace_image_refs(fpath, key):
            eth_upd += 1
        else:
            eth_skip += 1
    print(f"  Updated: {eth_upd}, Skipped (no image refs): {eth_skip}")

    # 5c: Non-ethnic pages
    print("\n[Other Pages]")
    other_upd, other_skip = 0, 0
    page_paths = [
        ("han-dynasty", "chinese/dynasty-evolution/han-dynasty.html"),
        ("tang-dynasty", "chinese/dynasty-evolution/tang-dynasty.html"),
        ("song-dynasty", "chinese/dynasty-evolution/song-dynasty.html"),
        ("ming-dynasty", "chinese/dynasty-evolution/ming-dynasty.html"),
        ("qing-dynasty", "chinese/dynasty-evolution/qing-dynasty.html"),
        ("dragon-phoenix", "chinese/topics/dragon-phoenix.html"),
        ("qipao-history", "chinese/topics/qipao-history.html"),
        ("tang-suit", "chinese/topics/tang-suit.html"),
        ("zhongshan-suit", "chinese/topics/zhongshan-suit.html"),
        ("eastern-western-wedding", "compare/eastern-western-wedding.html"),
        ("qipao-vs-evening-dress", "compare/qipao-vs-evening-dress.html"),
        ("blazer", "western/classic-pieces/blazer.html"),
        ("cashmere-sweater", "western/classic-pieces/cashmere-sweater.html"),
        ("little-black-dress", "western/classic-pieces/little-black-dress.html"),
        ("trench-coat", "western/classic-pieces/trench-coat.html"),
        ("white-shirt", "western/classic-pieces/white-shirt.html"),
        ("ballet-flats", "western/classic-pieces/ballet-flats.html"),
        ("jeans", "western/classic-pieces/jeans.html"),
        ("london-ss2026", "western/fashion-week-trends/london-ss2026.html"),
        ("milan-fw2026", "western/fashion-week-trends/milan-fw2026.html"),
        ("ny-fw2026", "western/fashion-week-trends/ny-fw2026.html"),
        ("paris-ss2026", "western/fashion-week-trends/paris-ss2026.html"),
    ]
    for base, rel_path in page_paths:
        fpath = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(fpath):
            print(f"  [WARN] {rel_path} not found")
            continue
        if replace_image_refs(fpath, base):
            other_upd += 1
        else:
            other_skip += 1
    print(f"  Updated: {other_upd}, Skipped: {other_skip}")

    # ---- SUMMARY ----
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Ethnic images:     {eth_ok} OK, {eth_fail} failed (of {3 * len(ethnic_data)})")
    print(f"  Non-ethnic images: {non_ok} OK, {non_fail} failed (of {3 * len(NON_ETHNIC_PAGES)})")
    print(f"  Fashion week:      {fw_ok} OK (of {len(FW_PHOTOS)})")
    print(f"  Dedup removed:     {dedup_count}")
    print(f"  HTML updated:")
    print(f"    Fashion week index: {'Yes' if fw_updated else 'No'}")
    print(f"    Ethnic pages:       {eth_upd}")
    print(f"    Other pages:        {other_upd}")

    # Count final image total
    final_imgs = [f for f in os.listdir(IMAGE_DIR) if f.endswith((".jpg", ".png", ".webp")) and not f.startswith("_")]
    total_size = sum(os.path.getsize(os.path.join(IMAGE_DIR, f)) for f in final_imgs)
    print(f"\n  Images in directory: {len(final_imgs)}")
    print(f"  Total size: {total_size/1024/1024:.1f} MB")

    # Verify remaining unsplash refs
    unsplash_count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        if "images" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                    if "images.unsplash.com" in fp.read():
                        unsplash_count += 1
    print(f"\n  HTML files still with Unsplash URLs: {unsplash_count} (should be 0)")


if __name__ == "__main__":
    main()
