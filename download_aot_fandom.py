#!/usr/bin/env python3
"""Download AOT character images from fandom wiki + other sources."""
import requests, re, time, json, os, io, urllib.parse
from pathlib import Path
from PIL import Image

OUTPUT_DIR = Path("d:/AI网站文件夹/aot-site/images")
PROXY = "http://127.0.0.1:1080"
PROXIES = {"http": PROXY, "https": PROXY}

H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
IMG_H = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fetch(url, to=30):
    try:
        return requests.get(url, headers=H, proxies=PROXIES, timeout=to)
    except Exception as e:
        return None

def dl(url, referer=None):
    hdrs = dict(IMG_H)
    if referer: hdrs['Referer'] = referer
    try:
        r = requests.get(url, headers=hdrs, proxies=PROXIES, timeout=30)
        if r.status_code == 200 and len(r.content) > 2048:
            return r.content
        return None
    except:
        return None

def fandom_api_img(character_name):
    """Get character image from AOT fandom wiki via MediaWiki API."""
    titles = character_name.replace(' ', '_')
    url = f"https://aot.fandom.com/api.php?action=query&titles={urllib.parse.quote(titles)}&prop=pageimages&format=json&pithumbsize=1000"
    log(f"  Fandom API: {character_name}")
    r = fetch(url)
    if not r or r.status_code != 200:
        return None
    try:
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for pid, page in pages.items():
            if pid == '-1':
                continue
            thumbnail = page.get('thumbnail', {})
            source = thumbnail.get('source', '')
            if source:
                log(f"  Got fandom img: {source}")
                # Try to get higher resolution
                hires = re.sub(r'/revision/latest(/.*)?', '/revision/latest', source)
                return hires
    except Exception as e:
        log(f"  Fandom API parse err: {e}")
    return None

def fandom_scrape_img(character_name):
    """Fallback: scrape fandom page for the infobox image."""
    titles = character_name.replace(' ', '_')
    url = f"https://aot.fandom.com/wiki/{urllib.parse.quote(titles)}"
    log(f"  Fandom scrape: {character_name}")
    r = fetch(url)
    if not r or r.status_code != 200:
        return None
    html = r.text
    # Look for infobox image - fandom uses figure with class pi-item
    # Common patterns for fandom infobox images
    patterns = [
        r'<img[^>]*class="pi-image-thumbnail"[^>]*src="([^"]+)"',
        r'<img[^>]*class="[^"]*pi-image[^"]*"[^>]*src="([^"]+)"',
        r'<figure[^>]*class="pi-item[^>]*>.*?<img[^>]*src="([^"]+)"',
        r'<img[^>]*src="(https://static\.wikia\.nocookie\.net/[^"]+)"[^>]*>',
        r'"image":"([^"]+)"',
    ]
    for pat in patterns:
        matches = re.findall(pat, html, re.DOTALL)
        for m in matches:
            # Clean up URL
            url_clean = m.split('?')[0] if '?' in m else m
            if 'wikia.nocookie.net' in url_clean or 'vignette.wikia.nocookie.net' in url_clean:
                # Try to get full resolution
                hires = re.sub(r'/revision/latest(/scale-to-width-down/[^/]+)?', '/revision/latest', url_clean)
                log(f"  Found fandom img: {hires[:100]}")
                return hires
    return None

def try_fandom(name):
    """Try to get character image from fandom wiki."""
    # Map character names to fandom page titles
    fandom_map = {
        "jean-kirstein": "Jean_Kirstein",
        "keith-shadis": "Keith_Shadis",
        "kenny-ackerman": "Kenny_Ackerman",
        "porco-galliard": "Porco_Galliard",
        "rod-reiss": "Rod_Reiss",
        "sasha-blouse": "Sasha_Blouse",
        "ymir-fritz": "Ymir_Fritz",
        "mikasa-ackerman": "Mikasa_Ackerman",
    }
    page_title = fandom_map.get(name, name.replace('-', '_').title())

    # Try API first
    img_url = fandom_api_img(page_title)
    if img_url:
        data = dl(img_url, "https://aot.fandom.com/")
        if data and len(data) >= 10240:
            return data

    time.sleep(1)

    # Try scrape
    img_url = fandom_scrape_img(page_title)
    if img_url:
        data = dl(img_url, "https://aot.fandom.com/")
        if data and len(data) >= 10240:
            return data

    return None

# ====== PNGWING (improved) ======
def pngwing_search(query):
    url = f"https://www.pngwing.com/en/search?q={urllib.parse.quote_plus(query)}"
    r = fetch(url)
    if not r or r.status_code != 200:
        return []
    html = r.text
    links = re.findall(r'href="(https://www\.pngwing\.com/en/free-png-[^"]+)"', html)
    thumbs = re.findall(r'data-src="(https://w7\.pngwing\.com/pngs/[^"]+-thumbnail\.png)"', html)
    alts = re.findall(r'<img[^>]*itemprop="thumbnail"[^>]*alt="([^"]*)"', html)
    out = []
    for a, b, c in zip(links, thumbs, alts):
        out.append((a, b.replace('-thumbnail.png', '.png'), c.lower()))
    return out

def word_in_alt(word, alt):
    return bool(re.search(r'\b' + re.escape(word) + r'\b', alt))

def score2(alt_low, name_parts):
    parts_found = sum(1 for p in name_parts if word_in_alt(p, alt_low))
    if parts_found < len(name_parts) - 1:
        return 0
    s = 10
    others = ['eren','mikasa','armin','reiner','annie','bertholdt','hange','erwin',
              'sasha','connie','jean','historia','porco','pieck','zeke','rod','keith',
              'kenny','floch','galliard','kirstein','kirschtein','blouse','finger',
              'braun','shadis','reiss','fritz']
    oc = sum(1 for c in others if word_in_alt(c, alt_low) and c not in name_parts)
    if oc == 0: s += 15
    elif oc == 1: s += 8
    elif oc == 2: s += 3
    if 'attack on titan' in alt_low or 'shingeki' in alt_low: s += 3
    if 'chibi' in alt_low: s -= 2
    return s

def try_pngwing_more(name, search_queries):
    """More aggressive pngwing search - look at ALL candidates, not just scored ones."""
    name_parts = name.lower().split()
    all_cands = []
    seen = set()

    for q in search_queries:
        items = pngwing_search(q)
        log(f"  Pngwing '{q}': {len(items)} items")
        for du, fu, al in items:
            if fu in seen: continue
            seen.add(fu)
            sc = score2(al, name_parts)
            if sc >= 10:
                all_cands.append((sc, fu, du, al))

    if not all_cands:
        # Last resort: lower threshold to 5
        log(f"  Low threshold...")
        for q in search_queries[:2]:
            items = pngwing_search(q)
            for du, fu, al in items:
                if fu in seen: continue
                seen.add(fu)
                sc = score2(al, name_parts)
                if sc >= 5:
                    all_cands.append((sc, fu, du, al))

    if not all_cands:
        return None

    all_cands.sort(key=lambda x: -x[0])
    for sc, fu, du, al in all_cands[:5]:
        log(f"  Candidate ({sc}): {al[:60]}")
        data = dl(fu, du)
        if data and len(data) >= 10240:
            log(f"  Got {len(data)} bytes")
            return data
        time.sleep(1)
    return None

# ====== STICKPNG ======
def try_stickpng(name):
    """Try stickpng.com for character images."""
    # Map character names to stickpng search queries
    query = urllib.parse.quote(f"{name} attack on titan")
    search_url = f"https://www.stickpng.com/search?q={query}"
    log(f"  Stickpng search...")
    r = fetch(search_url)
    if not r or r.status_code != 200:
        return None
    html = r.text
    # Find PNG links on stickpng
    img_urls = re.findall(r'<img[^>]*src="(https://www\.stickpng\.com/assets[^"]+\.png)"', html)
    if not img_urls:
        img_urls = re.findall(r'<img[^>]*src="(https://(?:www\.)?stickpng\.com[^"]+\.png)"', html)
    if not img_urls:
        # Try thumbnail patterns
        img_urls = re.findall(r'data-src="(https://[^"]*stickpng[^"]+\.png)"', html)

    if img_urls:
        for url in img_urls[:5]:
            log(f"  Stickpng img: {url[:80]}")
            data = dl(url)
            if data and len(data) >= 10240:
                log(f"  Got {len(data)} bytes from stickpng")
                return data
            time.sleep(0.5)
    return None

# ====== COMMON ======
def save_img(data, slug):
    if len(data) < 10240:
        return None, "too small"
    try:
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        if w < 200 or h < 200:
            return None, f"{w}x{h}"
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        fp = OUTPUT_DIR / f"{slug}.png"
        img.save(fp, 'PNG')
        return fp, f"{os.path.getsize(fp)}b {w}x{h}"
    except Exception as e:
        return None, str(e)

def rm_bg(d):
    try:
        import rembg
        return rembg.remove(d, session=rembg.new_session())
    except:
        return d

def verify(fp, name):
    log(f"  Doubao verify...")
    try:
        import subprocess
        r = subprocess.run(['python', 'd:/AI网站文件夹/shared/doubao_vision.py', str(fp),
            f'Answer YES or NO only: Is this {name} from Attack on Titan?'],
            capture_output=True, text=True, timeout=60)
        result_file = Path("C:/Users/Administrator/AppData/Local/Temp/doubao_vision_output.txt")
        if result_file.exists():
            out = result_file.read_text(encoding='utf-8').strip().lower()
            log(f"  Vision: {out[:100]}")
            return out
        return (r.stdout or r.stderr).strip().lower()
    except Exception as e:
        log(f"  Vision err: {e}")
        return ""

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  {'OK' if r and r.status_code==200 else 'FAIL'}")

    # Characters that still need images
    chars = [
        ("jean-kirstein", "Jean Kirstein", ["Jean Kirschtein AOT", "Jean Kirstein AOT", "Jean AOT", "Kirstein AOT"]),
        ("keith-shadis", "Keith Shadis", ["Keith Shadis AOT", "Shadis AOT", "Commander Shadis AOT"]),
        ("kenny-ackerman", "Kenny Ackerman", ["Kenny Ackerman AOT", "Kenny AOT", "Kenny Ackerman"]),
        ("mikasa-ackerman", "Mikasa Ackerman", ["Mikasa Ackerman AOT", "Mikasa AOT", "Mikasa Ackerman"]),
        ("porco-galliard", "Porco Galliard", ["Porco Galliard AOT", "Porco Galliard Jaw Titan", "Porco AOT"]),
        ("rod-reiss", "Rod Reiss", ["Rod Reiss AOT", "Rod Reiss Titan", "Rod Reiss"]),
        ("sasha-blouse", "Sasha Blouse", ["Sasha Blouse AOT", "Sasha Braus AOT", "Sasha AOT"]),
        ("ymir-fritz", "Ymir Fritz", ["Ymir Fritz AOT", "Founder Ymir AOT", "Ymir Fritz Founding Titan"]),
    ]

    results = {}
    for slug, name, queries in chars:
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        data = None
        src = None

        # Source 1: Fandom wiki (most reliable for character art)
        log(f"  Source: fandom wiki...")
        data = try_fandom(slug)
        if data: src = "fandom"

        # Source 2: Pngwing with improved search
        if not data:
            log(f"  Source: pngwing...")
            data = try_pngwing_more(name, queries)
            if data: src = "pngwing"

        # Source 3: Stickpng
        if not data:
            log(f"  Source: stickpng...")
            data = try_stickpng(name)
            if data: src = "stickpng"

        if not data:
            log(f"  FAILED - no image from any source")
            results[slug] = "FAILED"
            # Remove existing wrong file
            fp = OUTPUT_DIR / f"{slug}.png"
            if fp.exists():
                os.remove(fp)
                log(f"  Removed existing wrong file: {fp.name}")
            continue

        # Save
        old_fp = OUTPUT_DIR / f"{slug}.png"
        if old_fp.exists():
            old_size = old_fp.stat().st_size
        else:
            old_size = 0

        fp, msg = save_img(data, slug)
        if not fp:
            log(f"  FAILED to save: {msg}")
            results[slug] = f"FAIL ({msg})"
            continue
        log(f"  SAVED: {msg} from {src}")

        # Remove background
        with open(fp, 'rb') as f:
            raw = f.read()
        cleaned = rm_bg(raw)
        if cleaned != raw:
            Image.open(io.BytesIO(cleaned)).save(fp, 'PNG')
            log(f"  After rembg: {os.path.getsize(fp)}b")

        # Verify
        vision = verify(fp, name)
        is_ok = 'yes' in vision and 'no ' not in vision

        results[slug] = {"status":"OK","file":str(fp),"size":os.path.getsize(fp),
                          "src":src,"verified":is_ok,"vision":vision[:150]}
        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"FANDOM DOWNLOAD SUMMARY")
    log(f"{'='*60}")
    ver_ok = sum(1 for v in results.values() if isinstance(v, dict) and v.get('verified'))
    ver_fail = sum(1 for v in results.values() if isinstance(v, dict) and not v.get('verified'))
    failed = sum(1 for v in results.values() if isinstance(v, str))
    log(f"Verified OK: {ver_ok}, Unverified: {ver_fail}, Failed: {failed}")
    for s, r in results.items():
        if isinstance(r, dict):
            v = "V" if r.get('verified') else "?"
            log(f"  [{v}] {s}: {r['size']}b from {r['src']}")
        else:
            log(f"  [X] {s}: {r}")

    with open(OUTPUT_DIR / "fandom_report.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
