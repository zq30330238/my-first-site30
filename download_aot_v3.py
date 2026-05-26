#!/usr/bin/env python3
"""Download AOT character PNGs from pngwing via proxy."""
import requests, re, time, json, os, io, urllib.parse
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("d:/AI网站文件夹/aot-site/images")
PROXY = "http://127.0.0.1:1080"
PROXIES = {"http": PROXY, "https": PROXY}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
IMG_H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
}

SEARCH_QUERIES = {
    "jean-kirstein": ["Jean+Kirstein", "Jean+Kirstein+AOT"],
    "keith-shadis": ["Keith+Shadis", "Keith+Shadis+AOT"],
    "kenny-ackerman": ["Kenny+Ackerman", "Kenny+Ackerman+AOT"],
    "levi-ackerman": ["Levi+Ackerman", "Levi+Ackerman+AOT"],
    "mikasa-ackerman": ["Mikasa+Ackerman", "Mikasa+Ackerman+AOT"],
    "pieck-finger": ["Pieck+Finger", "Pieck+Finger+AOT"],
    "porco-galliard": ["Porco+Galliard", "Porco+Galliard+AOT"],
    "reiner-braun": ["Reiner+Braun", "Reiner+Braun+AOT"],
    "rod-reiss": ["Rod+Reiss", "Rod+Reiss+AOT"],
    "sasha-blouse": ["Sasha+Blouse", "Sasha+Blouse+AOT"],
    "ymir": ["Ymir+freckled", "Ymir+AOT"],
    "ymir-fritz": ["Ymir+Fritz", "Ymir+Fritz+AOT"],
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, timeout=15, referer=None):
    hdrs = dict(HEADERS)
    if referer:
        hdrs['Referer'] = referer
    try:
        return requests.get(url, headers=hdrs, proxies=PROXIES, timeout=timeout)
    except Exception as e:
        log(f"  Fetch error: {e}")
        return None

def dl_img(url, referer=None):
    hdrs = dict(IMG_H)
    if referer:
        hdrs['Referer'] = referer
    try:
        r = requests.get(url, headers=hdrs, proxies=PROXIES, timeout=30)
        if r.status_code == 200 and len(r.content) > 2048:
            return r.content
        return None
    except Exception as e:
        log(f"  DL error: {e}")
        return None

def extract_items(html):
    """Extract (detail_url, full_img_url, alt_text) from search page HTML."""
    items = []
    # Pattern: <a itemprop="url" href="..." target="_blank">
    #            <img itemprop="thumbnail" ... data-src="...thumbnail.png" alt="...">
    #          </a>
    for m in re.finditer(
        r'<a\s+itemprop="url"\s+href="(https://www\.pngwing\.com/en/free-png-[^"]+)"[^>]*>'
        r'\s*<img\s+itemprop="thumbnail"[^>]*data-src="(https://w7\.pngwing\.com/pngs/[^"]+-thumbnail\.png)"[^>]*alt="([^"]*)"',
        html
    ):
        detail_url = m.group(1)
        thumb_url = m.group(2)
        alt_text = m.group(3)
        # Full image URL = remove -thumbnail before .png
        full_url = thumb_url.replace('-thumbnail.png', '.png')
        items.append((detail_url, full_url, alt_text))
    return items

def search_character(query):
    """Search pngwing and return image items."""
    url = f"https://www.pngwing.com/en/search?q={query}"
    log(f"  Search: {url}")
    r = fetch(url)
    if not r or r.status_code != 200:
        return []
    items = extract_items(r.text)
    log(f"  Found {len(items)} items")
    return items

def is_relevant(alt_text, name_parts):
    """Check if image is relevant to the character."""
    alt_lower = alt_text.lower()
    # Must contain character's first AND last name (or just first name for Ymir)
    matches = sum(1 for part in name_parts if part in alt_lower)
    return matches >= len(name_parts) - 1  # at least all but one name part matches

def download_best(slug, name):
    """Download the best character image from pngwing."""
    name_lower = name.lower()
    name_parts = name_lower.split()

    queries = SEARCH_QUERIES.get(slug, [name.replace(' ', '+')])
    best_data = None
    best_size = 0

    for q in queries:
        items = search_character(q)
        for detail_url, full_url, alt_text in items:
            # Check relevance
            if not is_relevant(alt_text, name_parts):
                continue
            # Download the full image
            log(f"  Trying: {full_url[-60:]}")
            data = dl_img(full_url, referer=detail_url)
            if data and len(data) > best_size:
                best_data = data
                best_size = len(data)
                log(f"  Got {len(data)} bytes (relevant)")
            time.sleep(0.5)

        if best_data:
            break
        time.sleep(1)

    return best_data

def validate_and_save(data, slug):
    """Validate and save as PNG."""
    if len(data) < 10240:
        return None, f"Too small: {len(data)} bytes"
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w < 200 or h < 200:
            return None, f"Small dims: {w}x{h}"
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        fp = OUTPUT_DIR / f"{slug}.png"
        img.save(fp, 'PNG')
        return fp, f"{os.path.getsize(fp)} bytes, {w}x{h}"
    except Exception as e:
        return None, f"PIL error: {e}"

def remove_bg(img_data):
    """Remove background using rembg."""
    try:
        import rembg
        session = rembg.new_session()
        return rembg.remove(img_data, session=session)
    except Exception as e:
        log(f"  rembg error: {e}")
        return img_data

def verify_vision(fp, name):
    """Verify with doubao vision."""
    log(f"  Doubao vision check...")
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'd:/AI网站文件夹/shared/doubao_vision.py', str(fp),
             f'Describe this Attack on Titan character. Is this {name}?'],
            capture_output=True, text=True, timeout=60
        )
        out = (result.stdout or result.stderr).strip()
        log(f"  Vision: {out[:200]}")
        return out
    except Exception as e:
        log(f"  Vision error: {e}")
        return ""

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Test proxy
    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  Proxy: {'OK' if r and r.status_code == 200 else 'FAIL'}")

    names = {
        "jean-kirstein": "Jean Kirstein",
        "keith-shadis": "Keith Shadis",
        "kenny-ackerman": "Kenny Ackerman",
        "levi-ackerman": "Levi Ackerman",
        "mikasa-ackerman": "Mikasa Ackerman",
        "pieck-finger": "Pieck Finger",
        "porco-galliard": "Porco Galliard",
        "reiner-braun": "Reiner Braun",
        "rod-reiss": "Rod Reiss",
        "sasha-blouse": "Sasha Blouse",
        "ymir": "Ymir",
        "ymir-fritz": "Ymir Fritz",
    }

    results = {}

    for slug, name in names.items():
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        data = download_best(slug, name)

        if not data:
            log(f"  FAILED: no image found")
            results[slug] = "FAILED"
            continue

        fp, msg = validate_and_save(data, slug)
        if not fp:
            results[slug] = f"FAILED ({msg})"
            continue

        log(f"  Saved: {fp} ({msg})")

        # Background removal
        log(f"  Removing background...")
        with open(fp, 'rb') as f:
            raw = f.read()
        cleaned = remove_bg(raw)
        if cleaned != raw:
            img = Image.open(io.BytesIO(cleaned))
            img.save(fp, 'PNG')
            log(f"  After rembg: {os.path.getsize(fp)} bytes")

        # Vision verification
        vision = verify_vision(fp, name)

        results[slug] = {
            "status": "OK",
            "file": str(fp),
            "size": os.path.getsize(fp),
            "vision": vision[:200],
        }

        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in results.values() if isinstance(v, dict) and v.get('status') == 'OK')
    fail = sum(1 for v in results.values() if isinstance(v, str))
    log(f"OK: {ok}, FAIL: {fail}")
    for slug, r in results.items():
        if isinstance(r, dict):
            log(f"  [OK] {slug}: {r['size']} bytes")
        else:
            log(f"  [FAIL] {slug}: {r}")

    with open(OUTPUT_DIR / "download_report.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
