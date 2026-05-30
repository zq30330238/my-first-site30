"""全量视觉审计 — 豆包视觉API验证所有游戏/动漫站图片是否匹配页面内容"""
import os, re, json, base64, time, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from io import BytesIO
from PIL import Image

DOUBAO_KEY = "ark-3ee1e357-732f-484b-b341-d1757c95bfb4-4cdd8"
MODEL = "doubao-seed-1-6-vision-250815"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

GAME_ANIME = [
    'lol-site','fortnite-site','valorant-site','eldenring-site','minecraft-site',
    'games-site','naruto-site','onepiece-site','dragonball-site','anime-site',
    'aot-site','demonslayer-site','bleach-site','hxh-site','jjk-site','jojo-site',
    'sao-site','tokyoghoul-site'
]

ROOT = Path(__file__).resolve().parent.parent

def call_doubao(prompt, img_b64):
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": prompt},
            ]
        }],
        "max_tokens": 20,
    }
    req = Request(API_URL, data=json.dumps(payload, ensure_ascii=True).encode(), headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_KEY}",
    })
    resp = urlopen(req, timeout=45)
    data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def collect_page_images(site_dir):
    """Collect (html_path, title, image_path, image_bytes_b64) for all pages"""
    results = []
    for root, dirs, files in os.walk(site_dir):
        for f in files:
            if not f.endswith('.html'): continue
            fpath = os.path.join(root, f)
            try:
                with open(fpath, encoding='utf-8') as fh:
                    content = fh.read()
            except:
                continue

            title_m = re.search(r'<title>(.*?)</title>', content)
            title = title_m.group(1).strip() if title_m else f

            imgs = re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', content, re.DOTALL)
            found_img = None
            for src in imgs:
                if src.startswith('/images/'):
                    img_path = os.path.join(site_dir, src.lstrip('/'))
                elif '/images/' in src:
                    page_dir = os.path.dirname(fpath)
                    img_path = os.path.normpath(os.path.join(page_dir, src))
                else:
                    continue
                if os.path.exists(img_path):
                    found_img = (src, img_path)
                    break
            if found_img:
                src, img_path = found_img
                try:
                    img = Image.open(img_path).convert('RGB')
                    img.thumbnail((256, 256), Image.LANCZOS)
                    buf = BytesIO()
                    img.save(buf, format='JPEG', quality=60)
                    img_b64 = base64.b64encode(buf.getvalue()).decode()
                    buf.close()
                except:
                    with open(img_path, 'rb') as fh:
                        img_b64 = base64.b64encode(fh.read()).decode()
                rel_path = str(Path(fpath).relative_to(site_dir))
                results.append((site_dir, rel_path, title, src, img_b64, len(img_b64)))
            else:
                rel_path = str(Path(fpath).relative_to(site_dir))
                results.append((site_dir, rel_path, title, None, None, 0))
    return results


def main():
    all_pages = []
    for site in GAME_ANIME:
        if not os.path.isdir(site):
            continue
        pages = collect_page_images(site)
        all_pages.extend(pages)
        print(f"  {site}: {len(pages)} pages")

    to_verify = []
    no_images = []
    for site, rel_path, title, img_src, img_b64, img_size in all_pages:
        if not img_b64:
            no_images.append(f"{site}/{rel_path}")
            continue
        # Normalize Windows backslash for filtering
        norm_path = rel_path.replace('\\', '/').lower()
        if any(x in norm_path for x in ['privacy', 'terms', 'cookie', 'contact', 'about', 'sitemap', 'blog/']):
            continue
        short_title = re.split(r'\s*[—–|-]\s*', title)[0].strip()
        if len(short_title) < 3:
            short_title = title.split(' — ')[0] if ' — ' in title else title
        to_verify.append((site, rel_path, title, img_src, img_b64, short_title))

    total = len(to_verify)
    print(f"\nTotal pages: {len(all_pages)}, to verify: {total}, no images: {len(no_images)}\n")

    mismatches = []
    verified = 0
    errors = 0

    time.sleep(1)  # small startup delay
    retry_delay = 3
    for site, rel_path, title, img_src, img_b64, short_title in to_verify:
        prompt = f'Does this image show {short_title}? Answer ONLY YES or NO.'
        try:
            answer = call_doubao(prompt, img_b64[:30000])
            verified += 1
            retry_delay = 1.5  # reset on success
            if "NO" in answer.upper() and "YES" not in answer.upper():
                mismatches.append((site, rel_path, title, img_src, answer))
                print(f"  MISMATCH: {site}/{rel_path} — {short_title}")
            elif verified % 50 == 0:
                print(f"  Progress: {verified}/{total} OK")
        except Exception as e:
            errors += 1
            err_msg = str(e)[:100]
            print(f"  ERROR #{errors}: {site}/{rel_path}: {err_msg}")
            if errors > 10 and verified < 3:
                print(f"  TOO MANY EARLY ERRORS, aborting")
                break
            # Exponential backoff on rate limit
            if '429' in err_msg or 'Too Many' in err_msg:
                retry_delay = min(retry_delay * 1.5, 10)
                print(f"  (rate limited, sleep {retry_delay:.0f}s)")
                time.sleep(retry_delay)
                continue  # retry same page
            retry_delay = 1.5

        # Save incremental report every 30 pages
        if verified % 30 == 0:
            report = {
                "verified": verified, "errors": errors, "total": total,
                "mismatches": [{"site": s, "page": p, "title": t, "image": i, "reason": r} for s,p,t,i,r in mismatches],
                "no_images": no_images,
            }
            with open(ROOT / "visual_audit_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        time.sleep(0.5)

    # Final report
    print(f"\n=== VISUAL AUDIT RESULTS ===")
    print(f"Verified: {verified}, Errors: {errors}, Total: {total}")
    print(f"No images: {len(no_images)}")
    print(f"Mismatches: {len(mismatches)}")

    if mismatches:
        print(f"\n=== TOP MISMATCHES ===")
        for site, rel_path, title, img_src, reason in mismatches[:20]:
            print(f"  {site}/{rel_path} — {title[:60]}")

    report = {
        "verified": verified, "errors": errors, "total": total,
        "mismatches": [{"site": s, "page": p, "title": t, "image": i, "reason": r} for s,p,t,i,r in mismatches],
        "no_images": no_images,
    }
    report_path = ROOT / "visual_audit_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    if "--dry" in sys.argv:
        for site in GAME_ANIME:
            if not os.path.isdir(site): continue
            pages = collect_page_images(site)
            with_img = [p for p in pages if p[4]]
            without = [p for p in pages if not p[4]]
            print(f"{site}: {len(pages)} pages, {len(with_img)} with images, {len(without)} no images")
            for p in without[:3]:
                print(f"  NO IMG: {p[1]}")
    else:
        main()
