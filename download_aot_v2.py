#!/usr/bin/env python3
"""Download AOT character images using cloudscraper to bypass Cloudflare."""
import cloudscraper, os, re, time, json, sys, io
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("/root/aot_images")
scraper = cloudscraper.create_scraper()

IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

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

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def dl(url, referer=None):
    """Download using cloudscraper."""
    hdrs = dict(IMG_HEADERS)
    if referer:
        hdrs['Referer'] = referer
    try:
        r = scraper.get(url, headers=hdrs, timeout=30)
        if r.status_code == 200 and len(r.content) > 1024:
            return r.content
        log(f"  HTTP {r.status_code}, len={len(r.content) if r.content else 0}")
        return None
    except Exception as e:
        log(f"  DL error: {e}")
        return None

def search_pngwing(query):
    """Search pngwing with cloudscraper."""
    out = []
    for base in ['https://www.pngwing.com/en/search', 'https://www.pngwing.com/search']:
        url = f"{base}?q={requests.utils.quote(query)}" if 'requests' in dir() else \
              f"{base}?q={__import__('urllib.parse').quote(query)}"
        log(f"  Search: {url}")
        try:
            r = scraper.get(url, timeout=15)
            if r.status_code != 200:
                continue
            html = r.text
            paths = re.findall(r'href="(/en/free-png-[^"]+)"', html)
            if not paths:
                paths = re.findall(r'href="(/free-png-[^"]+)"', html)
            seen = set()
            for p in paths:
                fu = f"https://www.pngwing.com{p}" if not p.startswith('http') else p
                if fu not in seen:
                    seen.add(fu)
                    out.append(fu)
                if len(out) >= 5:
                    break
            if out:
                break
        except Exception as e:
            log(f"  Search error: {e}")
    log(f"  Found {len(out)} results")
    return out

def get_pngwing_original(detail_url):
    """Extract original download URL from pngwing detail page."""
    try:
        r = scraper.get(detail_url, timeout=15)
        if r.status_code != 200:
            return None
        html = r.text

        # Pattern 1: download link
        for pat in [r'href="(/en/free-png-[^"]+/download\?width=\d+)"',
                     r'href="(/free-png-[^"]+/download\?width=\d+)"']:
            m = re.findall(pat, html)
            if m:
                return f"https://www.pngwing.com{m[0]}"

        # Pattern 2: direct imgix link
        for pat in [r'(https://assets\.imgix\.net/[^"\']+\.png[^"\']*)',
                     r'(https?://[^"\']+\.png[^"\']*(?:download|dl)[^"\']*)']:
            m = re.findall(pat, html)
            if m:
                for u in m:
                    if 'logo' not in u.lower():
                        return u

        # Pattern 3: first large PNG on page
        all_png = re.findall(r'(https?://[^"\']+\.png[^"\']*)', html)
        for u in all_png:
            if 'logo' not in u.lower() and 'icon' not in u.lower():
                return u
        return None
    except Exception as e:
        log(f"  Detail error: {e}")
        return None

def try_pngwing(slug):
    """Try all pngwing queries."""
    queries_map = {
        "jean-kirstein": ["Jean Kirstein AOT", "Jean Kirstein"],
        "keith-shadis": ["Keith Shadis AOT", "Keith Shadis"],
        "kenny-ackerman": ["Kenny Ackerman AOT", "Kenny Ackerman"],
        "levi-ackerman": ["Levi Ackerman AOT", "Levi Ackerman"],
        "mikasa-ackerman": ["Mikasa Ackerman AOT", "Mikasa Ackerman"],
        "pieck-finger": ["Pieck Finger AOT", "Pieck Finger Cart Titan"],
        "porco-galliard": ["Porco Galliard AOT", "Porco Galliard Jaw Titan"],
        "reiner-braun": ["Reiner Braun AOT", "Reiner Braun Armored Titan"],
        "rod-reiss": ["Rod Reiss AOT", "Rod Reiss Titan"],
        "sasha-blouse": ["Sasha Blouse AOT", "Sasha Blouse"],
        "ymir": ["Ymir AOT freckled", "Ymir AOT", "Ymir Attack on Titan"],
        "ymir-fritz": ["Ymir Fritz AOT", "Ymir Fritz Founder"],
    }
    queries = queries_map.get(slug, [slug.replace('-', ' ')])
    for q in queries:
        details = search_pngwing(q)
        for du in details:
            dl_url = get_pngwing_original(du)
            if dl_url:
                data = dl(dl_url, referer=du)
                if data and len(data) > 10240:
                    log(f"  Got {len(data)} bytes from pngwing")
                    return data
            time.sleep(1)
        time.sleep(1)
    return None

def try_fandom(slug):
    """Direct known fandom page URL."""
    url = FANDOM_PAGES.get(slug)
    if not url:
        return None
    log(f"  Fandom: {url}")
    try:
        r = scraper.get(url, timeout=15)
        if r.status_code != 200:
            log(f"  Fandom HTTP {r.status_code}")
            return None
        html = r.text

        img_urls = []
        for pat in [r'data-src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"',
                     r'src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"',
                     r'src="(https://[^"]+vignette[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"']:
            for m in re.finditer(pat, html):
                img_urls.append(m.group(1))

        if not img_urls:
            # Try broader pattern
            for m in re.finditer(r'src="(https://[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"', html):
                u = m.group(1)
                if any(x in u for x in ['static.wikia', 'vignette', 'nocookie']):
                    img_urls.append(u)

        img_urls = list(dict.fromkeys(img_urls))
        filtered = [u for u in img_urls if not any(x in u.lower() for x in ['logo','icon','button','banner','wordmark','background'])]
        # Prefer /revision/latest (full res)
        filtered.sort(key=lambda u: 0 if '/revision/latest' in u or 'scale-to-width' not in u else 1)

        log(f"  {len(filtered)} candidates")
        for u in filtered[:10]:
            data = dl(u, referer=url)
            if data and len(data) > 20480:
                log(f"  Got {len(data)} bytes from fandom")
                return data
            time.sleep(0.3)
        return None
    except Exception as e:
        log(f"  Fandom error: {e}")
        return None

def try_gelbooru(slug, name):
    """Try Gelbooru for character art (safe only)."""
    tags = f"{name.replace(' ', '_')}_(attack_on_titan) rating:safe"
    url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={__import__('urllib.parse').quote(tags)}&limit=5"
    log(f"  Gelbooru: {url}")
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        posts = data if isinstance(data, list) else data.get('post', [])
        log(f"  {len(posts)} posts")
        for post in posts[:5]:
            file_url = post.get('file_url', '')
            if file_url:
                data = dl(file_url)
                if data and len(data) > 20480:
                    log(f"  Got {len(data)} bytes from gelbooru")
                    return data
                time.sleep(0.5)
        return None
    except Exception as e:
        log(f"  Gelbooru error: {e}")
        return None
    return None

def try_danbooru(slug, name):
    """Try Danbooru."""
    tags = f"{name.replace(' ', '_')}_(attack_on_titan)"
    url = f"https://danbooru.donmai.us/posts.json?tags={__import__('urllib.parse').quote(tags)}&limit=5&rating=safe"
    log(f"  Danbooru: {url}")
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if r.status_code != 200:
            return None
        posts = r.json()
        log(f"  {len(posts)} posts")
        for post in posts[:5]:
            file_url = post.get('file_url', '') or post.get('large_file_url', '') or post.get('source', '')
            if file_url:
                data = dl(file_url)
                if data and len(data) > 20480:
                    log(f"  Got {len(data)} bytes from danbooru")
                    return data
                time.sleep(0.5)
        return None
    except Exception as e:
        log(f"  Danbooru error: {e}")
        return None

def validate_and_save(data, slug):
    """Validate and save image."""
    if len(data) < 10240:
        return None, "too small"
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w < 200 or h < 200:
            return None, f"dimensions {w}x{h}"
        # Convert to PNG RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        fp = OUTPUT_DIR / f"{slug}.png"
        img.save(fp, 'PNG')
        sz = os.path.getsize(fp)
        return fp, f"{sz} bytes, {w}x{h}"
    except Exception as e:
        return None, f"PIL error: {e}"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    import requests as req_mod
    globals()['requests'] = req_mod

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

        data = None
        source = None

        # 1. pngwing
        data = try_pngwing(slug)
        if data:
            source = "pngwing"

        # 2. fandom wiki
        if not data:
            log(f"  Trying fandom wiki...")
            data = try_fandom(slug)
            if data:
                source = "fandom"

        # 3. gelbooru
        if not data:
            log(f"  Trying gelbooru...")
            data = try_gelbooru(slug, name)
            if data:
                source = "gelbooru"

        # 4. danbooru
        if not data:
            log(f"  Trying danbooru...")
            data = try_danbooru(slug, name)
            if data:
                source = "danbooru"

        if not data:
            log(f"  FAILED: all sources exhausted")
            results[slug] = "FAILED"
            continue

        fp, msg = validate_and_save(data, slug)
        if fp:
            log(f"  OK: {fp} ({msg}) from {source}")
            results[slug] = f"OK ({msg}, {source})"
        else:
            log(f"  FAILED: {msg}")
            results[slug] = f"FAILED ({msg})"

        time.sleep(2)

    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in results.values() if v.startswith('OK'))
    fail = sum(1 for v in results.values() if v.startswith('FAIL'))
    log(f"OK: {ok}, FAIL: {fail}")
    for slug, r in results.items():
        log(f"  {slug}: {r}")

    with open(OUTPUT_DIR / "report.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
