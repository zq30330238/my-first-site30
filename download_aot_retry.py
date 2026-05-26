#!/usr/bin/env python3
"""Retry failed AOT character downloads with better strategies."""
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
    """Check if word appears as a whole word (not substring) in alt text."""
    # Use regex word boundary
    return bool(re.search(r'\b' + re.escape(word) + r'\b', alt))

def score2(alt_low, name_parts):
    """Score with word boundary matching."""
    # Each name part must match as a whole word
    parts_found = sum(1 for p in name_parts if word_in_alt(p, alt_low))
    if parts_found < len(name_parts) - 1:
        return 0

    s = 10
    others = ['eren','mikasa','armin','reiner','annie','bertholdt','hange','erwin',
              'sasha','connie','jean','historia','porco','pieck','zeke','rod','keith',
              'kenny','floch','galliard','kirstein','kirschtein','blouse','braun',
              'shadis','reiss','fritz']
    oc = sum(1 for c in others if word_in_alt(c, alt_low) and c not in name_parts)
    if oc == 0: s += 15
    elif oc == 1: s += 8
    elif oc == 2: s += 3
    if 'attack on titan' in alt_low or 'shingeki' in alt_low: s += 3
    if 'chibi' in alt_low: s -= 2
    return s

def fetch_best_pngwing(name, search_queries):
    """Try multiple search queries and return best image."""
    name_parts = name.lower().split()
    all_cands = []
    seen = set()

    for q in search_queries:
        items = pngwing_search(q)
        log(f"  Query '{q}': {len(items)} items")
        for du, fu, al in items:
            if fu in seen: continue
            seen.add(fu)
            sc = score2(al, name_parts)
            if sc >= 10:
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

def dl_imgur(name):
    cid = "546c25a59c58ad7"
    q = urllib.parse.quote(f"{name} Attack on Titan")
    url = f"https://api.imgur.com/3/gallery/search/viral/all?q={q}"
    log(f"  Imgur search...")
    try:
        r = requests.get(url, headers={'Authorization': f'Client-ID {cid}'}, proxies=PROXIES, timeout=15)
        if r.status_code != 200: return None
        data = r.json().get('data', [])
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

def retry_one(slug, name, pngwing_queries):
    """Try to download one character."""
    log(f"\n{'='*60}")
    log(f"Retrying: {slug} ({name})")
    log(f"{'='*60}")

    # 1. Try pngwing with specific queries
    log(f"  pngwing...")
    data = fetch_best_pngwing(name, pngwing_queries)
    if data: return data, "pngwing"

    # 2. Try imgur
    log(f"  imgur...")
    data = dl_imgur(name)
    if data: return data, "imgur"

    return None, None

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log("Testing proxy...")
    r = fetch("https://www.google.com")
    log(f"  {'OK' if r and r.status_code==200 else 'FAIL'}")

    # Characters to retry with better search queries
    retry_list = [
        ("jean-kirstein", "Jean Kirstein", ["Jean Kirschtein AOT", "Jean Kirstein AOT", "Kirstein AOT", "Jean AOT"]),
        ("keith-shadis", "Keith Shadis", ["Keith Shadis AOT", "Shadis AOT", "Commander Shadis AOT"]),
        ("kenny-ackerman", "Kenny Ackerman", ["Kenny Ackerman AOT", "Kenny Ackerman", "Kenny AOT"]),
        ("mikasa-ackerman", "Mikasa Ackerman", ["Mikasa Ackerman AOT", "Mikasa AOT", "Mikasa Ackerman"]),
        ("pieck-finger", "Pieck Finger", ["Pieck AOT", "Pieck Cart Titan", "Pieck Finger AOT"]),
        ("porco-galliard", "Porco Galliard", ["Porco Galliard AOT", "Porco Galliard Jaw Titan", "Porco AOT"]),
        ("rod-reiss", "Rod Reiss", ["Rod Reiss AOT", "Rod Reiss Titan", "Rod Reiss"]),
        ("sasha-blouse", "Sasha Blouse", ["Sasha Blouse AOT", "Sasha Braus AOT", "Sasha AOT",
                                           "Sasha Blouse potato", "Sasha AOT potato girl"]),
        ("ymir-fritz", "Ymir Fritz", ["Ymir Fritz AOT", "Founder Ymir AOT", "Ymir Fritz Founding Titan"]),
    ]

    results = {}
    for slug, name, queries in retry_list:
        data, src = retry_one(slug, name, queries)
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
    log(f"RETRY SUMMARY")
    log(f"{'='*60}")
    for s, r in results.items():
        if isinstance(r, dict):
            v = "V" if r.get('verified') else "?"
            log(f"  [{v}] {s}: {r['size']}b from {r['src']}")
        else:
            log(f"  [X] {s}: {r}")

    with open(OUTPUT_DIR / "retry_report.json", 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
