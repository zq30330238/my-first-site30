#!/usr/bin/env python3
"""Download AOT character PNGs using system HTTP proxy to bypass GFW."""
import requests, re, time, json, os, io, sys, urllib.parse
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("d:/AI网站文件夹/aot-site/images")
PROXY = "http://127.0.0.1:1080"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}
IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

PROXIES = {"http": PROXY, "https": PROXY}

CHARACTER_SEARCH = {
    "jean-kirstein": ["Jean Kirstein", "Jean Kirstein Attack on Titan"],
    "keith-shadis": ["Keith Shadis", "Keith Shadis Attack on Titan"],
    "kenny-ackerman": ["Kenny Ackerman", "Kenny Ackerman Attack on Titan"],
    "levi-ackerman": ["Levi Ackerman", "Levi Ackerman Attack on Titan"],
    "mikasa-ackerman": ["Mikasa Ackerman", "Mikasa Ackerman Attack on Titan"],
    "pieck-finger": ["Pieck Finger", "Pieck Finger Attack on Titan"],
    "porco-galliard": ["Porco Galliard", "Porco Galliard Attack on Titan"],
    "reiner-braun": ["Reiner Braun", "Reiner Braun Attack on Titan"],
    "rod-reiss": ["Rod Reiss", "Rod Reiss Attack on Titan"],
    "sasha-blouse": ["Sasha Blouse", "Sasha Blouse Attack on Titan"],
    "ymir": ["Ymir freckled AOT", "Ymir Attack on Titan"],
    "ymir-fritz": ["Ymir Fritz AOT", "Ymir Fritz Attack on Titan"],
}

# Direct detail page URLs (pre-searched from working instances)
# Format: {slug: [(search_query, pngwing_detail_url), ...]}
# These are known pngwing urls for AOT characters
KNOWN_PNGWING = {
    "levi-ackerman": [
        "https://www.pngwing.com/en/free-png-xftfi",
        "https://www.pngwing.com/en/free-png-zxtmn",
    ],
    "mikasa-ackerman": [
        "https://www.pngwing.com/en/free-png-ygtwc",
        "https://www.pngwing.com/en/free-png-nryxp",
    ],
    "reiner-braun": [
        "https://www.pngwing.com/en/free-png-bvbiy",
    ],
    "sasha-blouse": [
        "https://www.pngwing.com/en/free-png-bqvnx",
    ],
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, headers_extra=None, timeout=15):
    hdrs = dict(HEADERS)
    if headers_extra:
        hdrs.update(headers_extra)
    try:
        r = requests.get(url, headers=hdrs, proxies=PROXIES, timeout=timeout)
        return r
    except Exception as e:
        log(f"  Fetch error: {e}")
        return None

def dl_image(url, referer=None):
    hdrs = dict(IMG_HEADERS)
    if referer:
        hdrs['Referer'] = referer
    try:
        r = requests.get(url, headers=hdrs, proxies=PROXIES, timeout=30)
        if r.status_code == 200 and len(r.content) > 1024:
            return r.content
        log(f"  HTTP {r.status_code}, size={len(r.content) if r.content else 0}")
        return None
    except Exception as e:
        log(f"  DL error: {e}")
        return None

def search_pngwing(query):
    """Search pngwing and return list of detail page URLs."""
    results = []
    for base_url in ['https://www.pngwing.com/en/search', 'https://www.pngwing.com/search']:
        url = f"{base_url}?q={urllib.parse.quote(query)}"
        log(f"  Search: {url}")
        r = fetch(url)
        if not r or r.status_code != 200:
            continue
        html = r.text

        if 'Just a moment' in html or 'challenge-platform' in html:
            log(f"  Cloudflare challenge")
            continue

        paths = re.findall(r'href="(/en/free-png-[^"]+)"', html)
        if not paths:
            paths = re.findall(r'href="(/free-png-[^"]+)"', html)

        seen = set()
        for p in paths:
            fu = f"https://www.pngwing.com{p}" if not p.startswith('http') else p
            if fu not in seen:
                seen.add(fu)
                results.append(fu)
            if len(results) >= 5:
                break
        if results:
            break
    log(f"  Found {len(results)} detail pages")
    return results

def get_download_url(detail_url):
    """Extract original image download URL from pngwing detail page."""
    log(f"  Detail: {detail_url}")
    r = fetch(detail_url)
    if not r or r.status_code != 200:
        return None
    html = r.text

    # Pattern 1: download link with width
    dl = re.findall(r'href="(/en/free-png-[^"]+/download\?width=\d+)"', html)
    if dl:
        return f"https://www.pngwing.com{dl[0]}"

    # Pattern 2: imgix direct URL
    imgix = re.findall(r'(https://assets\.imgix\.net/[^"\']+\.png[^"\']*)', html)
    if imgix:
        return imgix[0]

    # Pattern 3: any PNG not logo/icon
    all_png = re.findall(r'(https?://[^"\']+\.png[^"\']*)', html)
    for u in all_png:
        if 'logo' not in u.lower() and 'icon' not in u.lower() and 'thumb' not in u.lower():
            return u
    return None

def try_pngwing(slug):
    """Download from pngwing - try known URLs first, then search."""
    # Try known direct URLs first
    known = KNOWN_PNGWING.get(slug, [])
    for du in known:
        dl_url = get_download_url(du)
        if dl_url:
            data = dl_image(dl_url, referer=du)
            if data and len(data) > 10240:
                log(f"  Got {len(data)} bytes from known pngwing URL")
                return data
        time.sleep(1)

    # Then try search
    queries = CHARACTER_SEARCH.get(slug, [slug.replace('-', ' ')])
    for q in queries:
        detail_urls = search_pngwing(q)
        for du in detail_urls:
            dl_url = get_download_url(du)
            if dl_url:
                data = dl_image(dl_url, referer=du)
                if data and len(data) > 10240:
                    log(f"  Got {len(data)} bytes from pngwing search")
                    return data
            time.sleep(1.5)
        time.sleep(1)
    return None

def try_stickpng(slug, name):
    """Try stickpng.com."""
    urls = [
        f"https://www.stickpng.com/search?q={urllib.parse.quote(name)}",
        f"https://www.stickpng.com/img/cartoons/attack-on-titan/{name.replace(' ', '-').lower()}",
    ]
    for url in urls:
        log(f"  stickpng: {url}")
        r = fetch(url)
        if not r or r.status_code != 200:
            continue
        html = r.text
        imgs = re.findall(r'(https://[^"]+\.png[^"]*)', html)
        for img_url in imgs:
            if 'logo' not in img_url.lower() and 'icon' not in img_url.lower():
                data = dl_image(img_url, referer=url)
                if data and len(data) > 20480:
                    log(f"  Got {len(data)} bytes from stickpng")
                    return data
                time.sleep(0.5)
        time.sleep(1)
    return None

def try_imgur(slug, name):
    """Try imgur."""
    client_id = "546c25a59c58ad7"
    search_url = f"https://api.imgur.com/3/gallery/search/top/all?q={urllib.parse.quote(name + ' Attack on Titan')}"
    log(f"  Imgur: {search_url}")
    try:
        r = requests.get(search_url,
            headers={'Authorization': f'Client-ID {client_id}', 'User-Agent': 'Mozilla/5.0'},
            proxies=PROXIES, timeout=15)
        if r.status_code != 200:
            log(f"  HTTP {r.status_code}")
            return None
        data = r.json()
        items = data.get('data', [])
        log(f"  {len(items)} results")
        for item in items[:5]:
            if item.get('type') and 'image' in item['type']:
                link = item.get('link', '')
                if link:
                    img_data = dl_image(link)
                    if img_data and len(img_data) > 20480:
                        return img_data
            elif item.get('is_album'):
                album_id = item.get('id', '')
                if album_id:
                    r2 = requests.get(f"https://api.imgur.com/3/album/{album_id}",
                        headers={'Authorization': f'Client-ID {client_id}'},
                        proxies=PROXIES, timeout=10)
                    if r2.status_code == 200:
                        for img in r2.json().get('data', {}).get('images', [])[:2]:
                            link = img.get('link', '')
                            if link:
                                img_data = dl_image(link)
                                if img_data and len(img_data) > 20480:
                                    return img_data
            time.sleep(0.5)
        return None
    except Exception as e:
        log(f"  Imgur error: {e}")
        return None

def remove_background(img_data):
    """Remove background using rembg."""
    try:
        import rembg
        session = rembg.new_session()
        result = rembg.remove(img_data, session=session)
        return result
    except Exception as e:
        log(f"  rembg error: {e}")
        return img_data

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

def verify_with_vision(filepath, name):
    """Use doubao vision to verify image."""
    log(f"  Doubao vision verification...")
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'd:/AI网站文件夹/shared/doubao_vision.py', str(filepath),
             f'Describe this character from Attack on Titan. Is this {name}? Identify key features.'],
            capture_output=True, text=True, timeout=60
        )
        output = (result.stdout or result.stderr).strip()
        log(f"  Vision: {output[:200]}")
        return output
    except Exception as e:
        log(f"  Vision error: {e}")
        return ""

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Test proxy
    log("Testing proxy...")
    test = fetch("https://www.google.com")
    if test and test.status_code == 200:
        log("  Proxy OK")
    else:
        log("  WARNING: Proxy issue")

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
        "ymir": "Ymir (freckled)",
        "ymir-fritz": "Ymir Fritz",
    }

    results = {}

    for slug, name in names.items():
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        data = None
        source = None

        data = try_pngwing(slug)
        if data:
            source = "pngwing"

        if not data:
            log(f"  Trying imgur...")
            data = try_imgur(slug, name)
            if data:
                source = "imgur"

        if not data:
            log(f"  Trying stickpng...")
            data = try_stickpng(slug, name)
            if data:
                source = "stickpng"

        if not data:
            log(f"  FAILED: all sources exhausted")
            results[slug] = "FAILED"
            continue

        fp, msg = validate_and_save(data, slug)
        if not fp:
            results[slug] = f"FAILED ({msg})"
            continue

        log(f"  Saved: {fp} ({msg}) from {source}")

        # Background removal
        log(f"  Removing background...")
        with open(fp, 'rb') as f:
            img_data = f.read()
        final_data = remove_background(img_data)
        if final_data != img_data:
            img = Image.open(io.BytesIO(final_data))
            img.save(fp, 'PNG')
            log(f"  Background removed, size: {os.path.getsize(fp)} bytes")

        # Vision verification
        vision_out = verify_with_vision(fp, name)

        results[slug] = {
            "status": "OK",
            "file": str(fp),
            "size": os.path.getsize(fp),
            "source": source,
            "vision": vision_out[:200],
        }

        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in results.values() if isinstance(v, dict) and v.get('status') == 'OK')
    fail = sum(1 for v in results.values() if isinstance(v, str) and v == 'FAILED')
    log(f"OK: {ok}, FAIL: {fail}")
    for slug, r in results.items():
        if isinstance(r, dict) and r['status'] == 'OK':
            log(f"  [OK] {slug}: {r['size']} bytes from {r['source']}")
        else:
            log(f"  [FAIL] {slug}")

    report_path = OUTPUT_DIR / "download_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"\nReport: {report_path}")

if __name__ == '__main__':
    main()
