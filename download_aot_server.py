#!/usr/bin/env python3
"""Download Attack on Titan character images on remote server (has internet access)."""
import requests, os, re, time, json, sys, io
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("/root/aot_images")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Known fandom page URLs for each character (direct access, no search needed)
FANDOM_PAGES = {
    "jean-kirstein": "https://attackontitan.fandom.com/wiki/Jean_Kirstein",
    "keith-shadis": "https://attackontitan.fandom.com/wiki/Keith_Shadis",
    "kenny-ackerman": "https://attackontitan.fandom.com/wiki/Kenny_Ackerman",
    "levi-ackerman": "https://attackontitan.fandom.com/wiki/Levi_Ackerman",
    "mikasa-ackerman": "https://attackontitan.fandom.com/wiki/Mikasa_Ackerman",
    "pieck-finger": "https://attackontitan.fandom.com/wiki/Pieck_Finger",
    "porco-galliard": "https://attackontitan.fandom.com/wiki/Porco_Galliard",
    "reiner-braun": "https://attackontitan.fandom.com/wiki/Reiner_Braun",
    "rod-reiss": "https://attackontitan.fandom.com/wiki/Rod_Reiss",
    "sasha-blouse": "https://attackontitan.fandom.com/wiki/Sasha_Blouse",
    "ymir": "https://attackontitan.fandom.com/wiki/Ymir_(freckled)",
    "ymir-fritz": "https://attackontitan.fandom.com/wiki/Ymir_Fritz",
}

# Alternative search terms for pngwing
PNGWING_QUERIES = {
    "jean-kirstein": ["Jean Kirstein AOT", "Jean Kirstein"],
    "keith-shadis": ["Keith Shadis AOT", "Keith Shadis"],
    "kenny-ackerman": ["Kenny Ackerman AOT", "Kenny Ackerman"],
    "levi-ackerman": ["Levi Ackerman AOT", "Levi Ackerman"],
    "mikasa-ackerman": ["Mikasa Ackerman AOT", "Mikasa Ackerman"],
    "pieck-finger": ["Pieck Finger AOT", "Pieck Finger"],
    "porco-galliard": ["Porco Galliard AOT", "Porco Galliard"],
    "reiner-braun": ["Reiner Braun AOT", "Reiner Braun"],
    "rod-reiss": ["Rod Reiss AOT", "Rod Reiss"],
    "sasha-blouse": ["Sasha Blouse AOT", "Sasha Blouse"],
    "ymir": ["Ymir AOT freckled", "Ymir AOT"],
    "ymir-fritz": ["Ymir Fritz AOT", "Ymir Fritz"],
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def download_file(url, headers_dict=None, referer=None):
    """Download a file from URL."""
    hdrs = dict(IMG_HEADERS if headers_dict is None else headers_dict)
    if referer:
        hdrs['Referer'] = referer
    try:
        r = requests.get(url, headers=hdrs, timeout=30)
        if r.status_code == 200 and len(r.content) > 1024:
            return r.content
        else:
            log(f"  HTTP {r.status_code}, size {len(r.content) if r.content else 0}")
            return None
    except Exception as e:
        log(f"  Download error: {e}")
        return None

def search_pngwing(query):
    """Search pngwing and return list of detail URLs."""
    results = []
    search_url = f"https://www.pngwing.com/en/search?q={requests.utils.quote(query)}"
    log(f"  Searching: {search_url}")
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            log(f"  Search returned {r.status_code}")
            # Try https://www.pngwing.com/search?q=... (without /en/)
            search_url2 = f"https://www.pngwing.com/search?q={requests.utils.quote(query)}"
            r = requests.get(search_url2, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                log(f"  Alt search also {r.status_code}")
                return results

        html = r.text

        # Find detail page links (free-png-xxxxx)
        detail_paths = re.findall(r'href="(/en/free-png-[^"]+)"', html)
        if not detail_paths:
            detail_paths = re.findall(r'href="(/free-png-[^"]+)"', html)

        seen = set()
        for dp in detail_paths:
            if not dp.startswith('http'):
                full_url = f"https://www.pngwing.com{dp}"
            else:
                full_url = dp
            if full_url not in seen:
                seen.add(full_url)
                results.append(full_url)
            if len(results) >= 5:
                break

        log(f"  Found {len(results)} pngwing detail pages")
        return results
    except Exception as e:
        log(f"  Search error: {e}")
        return results

def get_pngwing_original(detail_url):
    """Extract original PNG download URL from pngwing detail page."""
    log(f"  Detail: {detail_url}")
    try:
        r = requests.get(detail_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        html = r.text

        # Pattern: download link with width parameter
        dl_matches = re.findall(r'href="(/en/free-png-[^"]+/download\?width=\d+)"', html)
        # Pattern 2: /free-png-xxxxx/download
        if not dl_matches:
            dl_matches = re.findall(r'href="(/free-png-[^"]+/download\?width=\d+)"', html)

        if dl_matches:
            dl_url = f"https://www.pngwing.com{dl_matches[0]}"
            log(f"  DL link: {dl_url}")
            return dl_url

        # Pattern 3: Direct imgix PNG URL
        png_matches = re.findall(r'(https://assets\.imgix\.net/[^"\']+\.png[^"\']*)', html)
        for png_url in png_matches:
            log(f"  Direct PNG: {png_url[:100]}")
            return png_url

        # Pattern 4: Any PNG URL on the page
        all_png = re.findall(r'(https?://[^"\']+\.png[^"\']*)', html)
        for p in all_png:
            if 'logo' not in p.lower() and 'icon' not in p.lower():
                log(f"  Found PNG: {p[:100]}")
                return p

        log(f"  No download URL found")
        return None
    except Exception as e:
        log(f"  Detail error: {e}")
        return None

def try_pngwing(slug):
    """Try to download character from pngwing using multiple queries."""
    queries = PNGWING_QUERIES.get(slug, [slug.replace('-', ' ')])
    for q in queries:
        log(f"  PNGwing query: '{q}'")
        detail_urls = search_pngwing(q)
        for du in detail_urls:
            dl_url = get_pngwing_original(du)
            if dl_url:
                img_data = download_file(dl_url, referer=du)
                if img_data and len(img_data) > 10240:
                    log(f"  Got {len(img_data)} bytes from pngwing")
                    return img_data
            time.sleep(1)
        time.sleep(1)
    return None

def try_fandom_wiki(slug):
    """Download image from fandom wiki character page."""
    url = FANDOM_PAGES.get(slug)
    if not url:
        log(f"  No fandom page defined for {slug}")
        return None

    log(f"  Fandom: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            log(f"  Fandom returned {r.status_code}")
            return None

        html = r.text

        # Try multiple image source patterns (fandom uses lazy loading)
        img_urls = []

        # Pattern 1: data-src (lazy loading)
        for m in re.finditer(r'data-src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"', html):
            img_urls.append(m.group(1))

        # Pattern 2: src attribute
        for m in re.finditer(r'src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"', html):
            img_urls.append(m.group(1))

        # Pattern 3: any img with relevant size
        for m in re.finditer(r'src="(https://[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"', html):
            url_candidate = m.group(1)
            if 'static.wikia.nocookie.net' in url_candidate or 'vignette.wikia.nocookie.net' in url_candidate:
                img_urls.append(url_candidate)

        # De-duplicate
        img_urls = list(dict.fromkeys(img_urls))

        # Filter out clearly wrong images
        filtered = []
        for iu in img_urls:
            iu_lower = iu.lower()
            if any(x in iu_lower for x in ['logo', 'icon', 'button', 'banner', 'nav', 'background', 'wordmark']):
                continue
            # Prefer larger images (scale-to-width or /revision/latest)
            filtered.append(iu)

        log(f"  Found {len(filtered)} candidate images on fandom")

        # Try each, largest first (prefer /revision/latest which is full res)
        sorted_imgs = sorted(filtered, key=lambda x: 0 if '/revision/latest' in x else 1)

        for img_url in sorted_imgs[:10]:
            img_data = download_file(img_url, referer=url)
            if img_data and len(img_data) > 20480:
                log(f"  Got {len(img_data)} bytes from fandom: {img_url[:80]}")
                return img_data
            time.sleep(0.5)

        log(f"  No suitable image from fandom")
        return None

    except Exception as e:
        log(f"  Fandom error: {e}")
        return None

def try_deviantart(slug, name):
    """Try deviantart for high quality character art."""
    queries = [
        f"{name} Attack on Titan render PNG",
        f"{name} AOT PNG transparent",
    ]
    for q in queries:
        url = f"https://www.deviantart.com/search?q={requests.utils.quote(q)}"
        log(f"  DA: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            html = r.text
            # Find image URLs
            imgs = re.findall(r'(https://[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)', html)
            for img_url in imgs:
                if any(x in img_url for x in ['logo', 'icon', 'avatar']):
                    continue
                img_data = download_file(img_url, referer=url)
                if img_data and len(img_data) > 30720:
                    log(f"  Got {len(img_data)} bytes from DA")
                    return img_data
                time.sleep(0.5)
        except Exception as e:
            log(f"  DA error: {e}")
        time.sleep(1)
    return None

def try_alternatives(slug, name):
    """Try various alternative sources."""
    sources = [
        ("zerochan", f"https://www.zerochan.net/search?q={requests.utils.quote(name + ' Attack on Titan')}"),
        ("safebooru", f"https://safebooru.org/index.php?page=post&s=list&tags={requests.utils.quote(name.replace(' ', '_') + '_attack_on_titan')}"),
    ]

    for src_name, url in sources:
        log(f"  {src_name}: {url}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            html = r.text
            imgs = re.findall(r'(https://[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)', html)
            for img_url in imgs:
                if any(x in img_url for x in ['logo', 'icon', 'avatar', 'thumb']):
                    continue
                img_data = download_file(img_url, referer=url)
                if img_data and len(img_data) > 30720:
                    log(f"  Got {len(img_data)} bytes from {src_name}")
                    return img_data
                time.sleep(0.5)
        except Exception as e:
            log(f"  {src_name} error: {e}")
        time.sleep(1)
    return None

def validate_image_size(img_data, min_size=30720):
    """Basic validation."""
    if len(img_data) < min_size:
        return False
    try:
        img = Image.open(io.BytesIO(img_data))
        w, h = img.size
        if w < 300 or h < 300:
            return False
        return True
    except:
        return False

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    character_names = {
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

    for slug, name in character_names.items():
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        img_data = None
        source = None

        # 1. Try pngwing first
        img_data = try_pngwing(slug)
        if img_data:
            source = "pngwing"

        # 2. Try fandom wiki
        if not img_data:
            log(f"  PNGwing failed, trying fandom wiki...")
            img_data = try_fandom_wiki(slug)
            if img_data:
                source = "fandom"

        # 3. Try deviantart
        if not img_data:
            log(f"  Fandom failed, trying deviantart...")
            img_data = try_deviantart(slug, name)
            if img_data:
                source = "deviantart"

        # 4. Try other alternatives
        if not img_data:
            log(f"  Trying alternatives...")
            img_data = try_alternatives(slug, name)
            if img_data:
                source = "alternative"

        if not img_data:
            log(f"  FAILED: no image from any source")
            results[slug] = "FAILED"
            continue

        # Validate
        if not validate_image_size(img_data):
            log(f"  FAILED: image validation ({len(img_data)} bytes)")
            results[slug] = f"FAILED (size: {len(img_data)})"
            continue

        # Save
        filepath = OUTPUT_DIR / f"{slug}.png"
        try:
            img = Image.open(io.BytesIO(img_data))
            if img.mode == 'RGB':
                img = img.convert('RGBA')
            img.save(filepath, 'PNG')
        except Exception as e:
            log(f"  Save error: {e}, saving raw")
            with open(filepath, 'wb') as f:
                f.write(img_data)

        file_size = os.path.getsize(filepath)
        img_dim = f"{img.size[0]}x{img.size[1]}" if 'img' in dir() else "?"
        log(f"  SAVED: {filepath} ({file_size} bytes, {img_dim}) from {source}")
        results[slug] = f"OK ({file_size} bytes, {img_dim}, {source})"

        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in results.values() if v.startswith('OK'))
    fail = sum(1 for v in results.values() if v.startswith('FAIL'))
    log(f"OK: {ok}, FAIL: {fail}")
    for slug, r in results.items():
        log(f"  {slug}: {r}")

    # Write report
    with open(OUTPUT_DIR / "report.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
