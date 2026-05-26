#!/usr/bin/env python3
"""Download AOT character PNGs - pngwing + imgur, with proper verification."""
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

# ====== PNGWING ======
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

def score(alt_low, name_parts):
    """Score relevance. CRITICAL: must contain target name parts."""
    parts_found = sum(1 for p in name_parts if p in alt_low)

    # REJECT if no name part matches
    if parts_found < len(name_parts) - 1:
        return 0

    s = 10  # base for name match
    others = ['eren','mikasa','armin','reiner','annie','bertholdt','hange','erwin',
              'sasha','connie','jean','historia','porco','pieck','zeke','rod','keith',
              'kenny','floch','galliard','kirstein','kirschtein','blouse','finger',
              'braun','shadis','reiss']
    oc = sum(1 for c in others if c in alt_low and c not in name_parts)
    if oc == 0: s += 15
    elif oc == 1: s += 8
    elif oc == 2: s += 3
    if 'attack on titan' in alt_low or 'shingeki' in alt_low: s += 3
    if 'chibi' in alt_low: s -= 2
    if 'logo' in alt_low: s -= 3
    return s

def dl_pngwing(name, slug):
    name_parts = name.lower().split()
    for q in [f"{name} Attack on Titan", name]:
        items = pngwing_search(q)
        cands = []
        seen = set()
        for du, fu, al in items:
            if fu in seen: continue
            seen.add(fu)
            sc = score(al, name_parts)
            if sc >= 10:
                cands.append((sc, fu, du, al))
        if cands:
            cands.sort(key=lambda x: -x[0])
            for sc, fu, du, al in cands[:5]:
                log(f"  pngwing candidate ({sc}): {al[:60]}")
                data = dl(fu, du)
                if data and len(data) >= 10240:
                    log(f"  Got {len(data)} bytes from pngwing")
                    return data
                time.sleep(1)
    return None

# ====== IMGUR ======
def dl_imgur(name):
    cid = "546c25a59c58ad7"
    q = urllib.parse.quote(f"{name} Attack on Titan")
    url = f"https://api.imgur.com/3/gallery/search/viral/all?q={q}"
    log(f"  Imgur: {url[:80]}")
    try:
        r = requests.get(url, headers={'Authorization': f'Client-ID {cid}'}, proxies=PROXIES, timeout=15)
        if r.status_code != 200:
            log(f"  Imgur HTTP {r.status_code}")
            return None
        data = r.json().get('data', [])
        log(f"  {len(data)} results")
        for item in data[:10]:
            if item.get('is_album'):
                for img in item.get('images', [])[:3]:
                    link = img.get('link', '')
                    if link:
                        d = dl(link)
                        if d and len(d) > 20480: return d
            else:
                link = item.get('link', '')
                if link:
                    d = dl(link)
                    if d and len(d) > 20480: return d
            time.sleep(0.3)
        return None
    except Exception as e:
        log(f"  Imgur err: {e}")
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
        # Convert RGBA for transparency support
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
        out = (r.stdout or r.stderr).strip()
        # Get the actual output - it might be in a file
        result_file = Path("C:/Users/Administrator/AppData/Local/Temp/doubao_vision_output.txt")
        if result_file.exists():
            out2 = result_file.read_text(encoding='utf-8')
            log(f"  Vision: {out2[:200]}")
            return out2
        log(f"  Vision: {out[:200]}")
        return out
    except Exception as e:
        log(f"  Vision err: {e}")
        return ""

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  {'OK' if r and r.status_code==200 else 'FAIL'}")

    chars = {
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

    res = {}
    for slug, name in chars.items():
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({name})")
        log(f"{'='*60}")

        data = None
        src = None

        # 1. pngwing
        log(f"  Source 1: pngwing...")
        data = dl_pngwing(name, slug)
        if data: src = "pngwing"

        # 2. imgur
        if not data:
            log(f"  Source 2: imgur...")
            data = dl_imgur(name)
            if data: src = "imgur"

        if not data:
            log(f"  FAILED: no image from any source")
            res[slug] = "FAILED"
            continue

        fp, msg = save_img(data, slug)
        if not fp:
            log(f"  FAILED: {msg}")
            res[slug] = f"FAILED ({msg})"
            continue
        log(f"  SAVED: {msg} from {src}")

        # Background removal
        with open(fp, 'rb') as f:
            raw = f.read()
        cleaned = rm_bg(raw)
        if cleaned != raw:
            Image.open(io.BytesIO(cleaned)).save(fp, 'PNG')
            log(f"  After rembg: {os.path.getsize(fp)}b")

        # Verify with doubao vision
        vision = verify(fp, name)

        # Check if verification says YES (character confirmed)
        vision_lower = vision.lower()
        is_correct = 'yes' in vision_lower and 'no' not in vision_lower[:10]
        if 'yes' in vision_lower and 'no' not in vision_lower[:30]:
            is_correct = True

        if is_correct:
            log(f"  VERIFIED: character confirmed")
        else:
            log(f"  WARNING: character NOT confirmed by vision")
            # Keep the image anyway - it's the best we have from pngwing/imgur

        res[slug] = {"status":"OK","file":str(fp),"size":os.path.getsize(fp),
                      "src":src,"verified":is_correct,"vision":vision[:200]}
        time.sleep(2)

    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    ok = sum(1 for v in res.values() if isinstance(v, dict))
    fail = sum(1 for v in res.values() if isinstance(v, str))
    log(f"OK: {ok}, FAIL: {fail}")
    for s, r in res.items():
        if isinstance(r, dict):
            v = "V" if r.get('verified') else "?"
            log(f"  [{v}] {s}: {r['size']}b from {r['src']}{' (unverified)' if not r.get('verified') else ''}")
        else:
            log(f"  [X] {s}: {r}")

    with open(OUTPUT_DIR / "report.json", 'w') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
