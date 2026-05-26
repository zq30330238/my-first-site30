#!/usr/bin/env python3
"""Retry rod-reiss and sasha-blouse with better fandom scraping."""
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

def scrape_fandom_infobox(character_name):
    """Scrape the fandom wiki page directly to get the character infobox image."""
    titles = character_name.replace(' ', '_')
    url = f"https://aot.fandom.com/wiki/{urllib.parse.quote(titles)}"
    log(f"  Scraping: {url}")
    r = fetch(url)
    if not r or r.status_code != 200:
        log(f"  Fetch failed: {r.status_code if r else 'None'}")
        return None
    html = r.text

    # Save HTML for debugging (optional)
    # with open(f"debug_{character_name}.html", 'w', encoding='utf-8') as f:
    #     f.write(html)

    # Pattern 1: pi-image-thumbnail class (standard fandom infobox)
    pats = [
        r'<img[^>]*class="[^"]*pi-image-thumbnail[^"]*"[^>]*src="([^"]+)"',
        r'<img[^>]*class="[^"]*pi-image[^"]*"[^>]*src="([^"]+)"',
        r'<figure[^>]*class="pi-item[^>]*>.*?<img[^>]*src="([^"]+)"',
        r'<a[^>]*class="image[^>]*>.*?<img[^>]*src="([^"]+)"',
    ]

    for pat in pats:
        matches = re.findall(pat, html, re.DOTALL)
        for m in matches:
            # Clean URL - remove query params to get full res
            clean_url = m.split('/revision')[0] + '/revision/latest'
            if 'wikia.nocookie.net' in clean_url:
                log(f"  Found infobox img: {clean_url[:100]}")
                return clean_url

    # Pattern 5: Any wikia.nocookie.net image in the page (first one)
    wikia_imgs = re.findall(r'(https://static\.wikia\.nocookie\.net/[^"\'\\]+)', html)
    if wikia_imgs:
        for img_url in wikia_imgs:
            clean_url = img_url.split('/revision')[0] + '/revision/latest'
            log(f"  Found wikia img: {clean_url[:100]}")
            return clean_url

    return None

def try_pngwing_direct(name):
    """Try pngwing search with specific queries."""
    import urllib
    queries = [
        f"{name} Attack on Titan",
        name,
    ]

    for q in queries:
        url = f"https://www.pngwing.com/en/search?q={urllib.parse.quote_plus(q)}"
        r = fetch(url)
        if not r or r.status_code != 200:
            continue
        html = r.text
        links = re.findall(r'href="(https://www\.pngwing\.com/en/free-png-[^"]+)"', html)
        thumbs = re.findall(r'data-src="(https://w7\.pngwing\.com/pngs/[^"]+-thumbnail\.png)"', html)
        alts = re.findall(r'<img[^>]*itemprop="thumbnail"[^>]*alt="([^"]*)"', html)

        name_parts = name.lower().split()
        for du, fu, al in zip(links, thumbs, alts):
            al_low = al.lower()
            parts_found = sum(1 for p in name_parts if p in al_low)
            if parts_found >= 1:
                full_url = fu.replace('-thumbnail.png', '.png')
                log(f"  pngwing candidate: {al[:60]}")
                data = dl(full_url, du)
                if data and len(data) >= 10240:
                    log(f"  Got {len(data)} bytes from pngwing")
                    return data
                time.sleep(1)
        time.sleep(1)
    return None

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  {'OK' if r and r.status_code==200 else 'FAIL'}")

    # Retry Rod Reiss and Sasha Blouse
    chars = [
        ("rod-reiss", "Rod Reiss", "Rod_Reiss"),
        ("sasha-blouse", "Sasha Blouse", "Sasha_Blouse"),
    ]

    results = {}
    for slug, name, fandom_title in chars:
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        data = None
        src = None

        # Source 1: Scrape fandom infobox directly
        log(f"  Source: fandom scrape...")
        img_url = scrape_fandom_infobox(fandom_title)
        if img_url:
            data = dl(img_url, "https://aot.fandom.com/")
            if data:
                if len(data) >= 10240:
                    log(f"  Got {len(data)} bytes from fandom scrape")
                    src = "fandom-scrape"
                else:
                    log(f"  Fandom image too small: {len(data)} bytes")
                    data = None

        # Source 2: Pngwing
        if not data:
            log(f"  Source: pngwing...")
            data = try_pngwing_direct(name)
            if data: src = "pngwing"

        if not data:
            log(f"  FAILED")
            results[slug] = "FAILED"
            continue

        fp, msg = save_img(data, slug)
        if not fp:
            results[slug] = f"FAIL ({msg})"
            continue
        log(f"  SAVED: {msg} from {src}")

        # Background removal
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
    log(f"FINAL RETRY SUMMARY")
    log(f"{'='*60}")
    for s, r in results.items():
        if isinstance(r, dict):
            v = "V" if r.get('verified') else "?"
            log(f"  [{v}] {s}: {r['size']}b from {r['src']}")
        else:
            log(f"  [X] {s}: {r}")

    with open(OUTPUT_DIR / "final_retry.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
