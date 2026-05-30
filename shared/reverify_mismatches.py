"""Re-verify visual audit mismatches with improved prompt"""
import json, base64, time, sys, os, io
from urllib.request import Request, urlopen
from PIL import Image
from io import BytesIO

MODEL = "doubao-seed-1-6-vision-250815"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
KEY = "ark-3ee1e357-732f-484b-b341-d1757c95bfb4-4cdd8"
REPORT_PATH = "d:/AI网站文件夹/visual_audit_report.json"

def call_doubao(prompt, img_b64):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {"type": "text", "text": prompt},
        ]}],
        "max_tokens": 20,
    }
    req = Request(API_URL, data=json.dumps(payload, ensure_ascii=True).encode(), headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {KEY}",
    })
    resp = urlopen(req, timeout=45)
    data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()

def get_image_b64(site_dir, img_src, page_path):
    """Get base64 of image, trying multiple path resolutions"""
    if img_src.startswith('/images/'):
        img_path = os.path.join(site_dir, img_src.lstrip('/'))
    elif '/images/' in img_src:
        page_dir = os.path.dirname(os.path.join(site_dir, page_path))
        img_path = os.path.normpath(os.path.join(page_dir, img_src))
    else:
        return None

    if not os.path.exists(img_path):
        return None

    try:
        img = Image.open(img_path).convert('RGB')
        img.thumbnail((256, 256), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=60)
        return base64.b64encode(buf.getvalue()).decode()
    except:
        with open(img_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()

def main():
    r = json.load(open(REPORT_PATH, 'r', encoding='utf-8'))
    mismatches = r['mismatches']
    print(f"Re-verifying {len(mismatches)} mismatches with improved prompt...\n")

    confirmed = []
    false_positives = []
    errors = []

    for i, m in enumerate(mismatches):
        site = m['site']
        page = m['page']
        title = m['title']
        img_src = m['image']

        # Extract short title/character name
        short = title.split('|')[0].split('—')[0].split('—')[0].strip()
        # Remove suffix like "Guide & Profile", " | JJK Guides"
        for suffix in [' Guide & Profile', ' | Bleach Wiki', ' | JJK Guides', ' | Hunter x Hunter Wiki',
                       ' | One Piece Wiki', ' | Naruto Wiki', ' | Dragon Ball Wiki', ' | Attack on Titan Wiki',
                       ' | SAO Wiki', ' | Tokyo Ghoul Wiki', ' | JoJo Wiki']:
            if short.endswith(suffix):
                short = short[:-len(suffix)].strip()
                break

        site_dir = f"d:/AI网站文件夹/{site}"
        img_b64 = get_image_b64(site_dir, img_src, page)

        if not img_b64:
            confirmed.append({**m, 'reason': 'IMAGE_MISSING'})
            print(f"  MISSING: {site}/{page} — {short}")
            continue

        # IMPROVED PROMPT — ask about the image content directly
        prompt = f'Does this image show {short}? Answer ONLY YES or NO.'

        try:
            answer = call_doubao(prompt, img_b64[:30000])
            if "NO" in answer.upper() and "YES" not in answer.upper():
                confirmed.append({**m, 'reason': answer})
                print(f"  REAL: {site}/{page} — {short}")
            else:
                false_positives.append({**m, 'reason': answer})
                print(f"  FALSE: {site}/{page} — {short} → {answer}")
        except Exception as e:
            errors.append({**m, 'reason': str(e)[:100]})
            print(f"  ERROR: {site}/{page} — {e}")

        time.sleep(0.5)

        if (i+1) % 30 == 0:
            print(f"  Progress: {i+1}/{len(mismatches)}")

    # Save results
    result = {
        "total_audited": r['verified'],
        "original_mismatches": len(mismatches),
        "confirmed_real": len(confirmed),
        "false_positives": len(false_positives),
        "errors_during_reverify": len(errors),
        "confirmed": confirmed,
        "false_positives": false_positives,
    }

    out_path = "d:/AI网站文件夹/visual_audit_verified.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n=== RE-VERIFICATION RESULTS ===")
    print(f"Original mismatches: {len(mismatches)}")
    print(f"Confirmed real: {len(confirmed)}")
    print(f"False positives: {len(false_positives)}")
    print(f"Errors: {len(errors)}")
    print(f"\nSaved to: {out_path}")

if __name__ == "__main__":
    main()
