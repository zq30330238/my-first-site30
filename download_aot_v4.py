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

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=timeout)
        return r
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

def search_items(query):
    """Search pngwing and return (detail_url, full_img_url, alt_text) items."""
    url = f"https://www.pngwing.com/en/search?q={urllib.parse.quote_plus(query)}"
    log(f"  Search: {url}")
    r = fetch(url)
    if not r or r.status_code != 200:
        log(f"  Fetch failed: status={r.status_code if r else 'None'}, len={len(r.text) if r else 0}")
        return []

    html = r.text
    links = re.findall(r'href="(https://www\.pngwing\.com/en/free-png-[^"]+)"', html)
    thumbs = re.findall(r'data-src="(https://w7\.pngwing\.com/pngs/[^"]+-thumbnail\.png)"', html)
    alts = re.findall(r'<img[^>]*itemprop="thumbnail"[^>]*alt="([^"]*)"', html)

    items = []
    for link, thumb, alt in zip(links, thumbs, alts):
        full_url = thumb.replace('-thumbnail.png', '.png')
        items.append((link, full_url, alt.lower()))

    log(f"  Found {len(items)} items")
    return items

def score_relevance(alt_lower, name_parts):
    """Score relevance of image alt text to character."""
    score = 0
    parts_found = sum(1 for p in name_parts if p in alt_lower)
    if parts_found >= len(name_parts) - 1:
        score += 10

    # Count OTHER character names in alt text
    other_chars = ['eren', 'mikasa', 'armin', 'levi', 'reiner', 'annie', 'bertholdt',
                   'hange', 'erwin', 'sasha', 'connie', 'jean', 'ymir', 'historia',
                   'porco', 'pieck', 'zeke', 'rod', 'keith', 'kenny', 'floch', 'galliard',
                   'kirstein', 'kirschtein', 'blouse', 'finger', 'braun', 'shadis',
                   'ackerman', 'reiss', 'fritz']
    char_count = sum(1 for c in other_chars if c in alt_lower and c not in name_parts)

    if char_count == 0:
        score += 15
    elif char_count == 1:
        score += 8
    elif char_count == 2:
        score += 3

    if 'attack on titan' in alt_lower or 'shingeki' in alt_lower:
        score += 3
    if 'chibi' in alt_lower:
        score -= 2
    if 'logo' in alt_lower or 'icon' in alt_lower:
        score -= 3

    return score

def download_best(slug, name):
    """Download the best matching character image from pngwing."""
    name_parts = name.lower().split()

    # Try more specific queries first
    queries = [
        f"{name} Attack on Titan png",
        f"{name} Attack on Titan",
        name,
    ]

    all_candidates = []
    seen_urls = set()

    for q in queries:
        log(f"  Query: '{q}'")
        items = search_items(q)
        for detail_url, full_url, alt_lower in items:
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            score = score_relevance(alt_lower, name_parts)
            if score >= 8:
                all_candidates.append((score, full_url, detail_url, alt_lower))

        if all_candidates:
            break
        time.sleep(1)

    if not all_candidates:
        # Lower threshold for less common characters
        log(f"  Low threshold search...")
        for q in [f"{name} Attack on Titan", name]:
            items = search_items(q)
            for detail_url, full_url, alt_lower in items:
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                score = score_relevance(alt_lower, name_parts)
                if score >= 5:
                    all_candidates.append((score, full_url, detail_url, alt_lower))
            if all_candidates:
                break
            time.sleep(1)

    if not all_candidates:
        # Absolute last resort: just download any matching search result
        log(f"  Last resort: just download anything related...")
        items = search_items(name)
        for detail_url, full_url, alt_lower in items:
            parts_found = sum(1 for p in name_parts if p in alt_lower)
            if parts_found >= 1:
                score = 1
                all_candidates.append((score, full_url, detail_url, alt_lower))
            if len(all_candidates) >= 3:
                break

    if not all_candidates:
        return None

    all_candidates.sort(key=lambda x: -x[0])
    log(f"  Best candidate score={all_candidates[0][0]}")

    for score, full_url, detail_url, _ in all_candidates[:5]:
        log(f"  Downloading (score={score})...")
        data = dl_img(full_url, referer=detail_url)
        if data and len(data) >= 10240:
            log(f"  Got {len(data)} bytes")
            return data
        time.sleep(1)

    return None

def validate_and_save(data, slug):
    if len(data) < 10240:
        return None, f"Too small: {len(data)} bytes"
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w < 200 or h < 200:
            return None, f"Small: {w}x{h}"
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        fp = OUTPUT_DIR / f"{slug}.png"
        img.save(fp, 'PNG')
        return fp, f"{os.path.getsize(fp)} bytes, {w}x{h}"
    except Exception as e:
        return None, f"PIL error: {e}"

def remove_bg(img_data):
    try:
        import rembg
        session = rembg.new_session()
        return rembg.remove(img_data, session=session)
    except Exception as e:
        log(f"  rembg error: {e}")
        return img_data

def verify_vision(fp, name):
    log(f"  Doubao vision check...")
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'd:/AI网站文件夹/shared/doubao_vision.py', str(fp),
             f'Describe this Attack on Titan character. Is this {name}? Identify key features.'],
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

    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  Proxy: {'OK' if r and r.status_code == 200 else 'FAIL'}")

    characters = {
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

    for slug, name in characters.items():
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

        # Remove background
        log(f"  Removing background...")
        with open(fp, 'rb') as f:
            raw = f.read()
        cleaned = remove_bg(raw)
        if cleaned != raw:
            Image.open(io.BytesIO(cleaned)).save(fp, 'PNG')
            log(f"  After rembg: {os.path.getsize(fp)} bytes")

        # Vision verification
        vision = verify_vision(fp, name)

        results[slug] = {
            "status": "OK",
            "file": str(fp),
            "size": os.path.getsize(fp),
            "vision_says": vision[:150],
        }

        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in results.values() if isinstance(v, dict))
    fail = sum(1 for v in results.values() if isinstance(v, str))
    log(f"OK: {ok}, FAIL: {fail}")
    for slug, r in results.items():
        if isinstance(r, dict):
            log(f"  [OK] {slug}: {r['size']} bytes")
        else:
            log(f"  [FAIL] {slug}")

    report = OUTPUT_DIR / "download_report.json"
    with open(report, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"\nReport: {report}")

if __name__ == '__main__':
    main()
