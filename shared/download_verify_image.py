"""Global image download + Doubao verification pipeline.

Usage:
  python shared/download_verify_image.py "Miao traditional clothing" clothing-site/images/miao_hero.jpg --check "Does this show traditional Miao Hmong clothing with silver headdress? Full body shot?"
  python shared/download_verify_image.py --batch clothing-site/download_tasks.json --out clothing-site/images/
  python shared/download_verify_image.py --verify-only clothing-site/images/miao_hero.jpg --check "..."
"""

import sys, os, json, random, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from PIL import Image

# Allow importing sibling modules in shared/
_SELF_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SELF_DIR))
import doubao_vision

PEXELS_API_KEY = "QpCSbvN6HrNuL2bYBy7090p5VI2zTqEsqeSvQF92sxMG0bcmhrhJ0OL8"
SEEDREAM_API_KEY = os.environ.get("ARK_API_KEY") or "ark-71e489d9-8720-4ce9-ac4b-30c178333e33-02a59"
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
RETRY_SUFFIXES = ["portrait", "traditional", "festival", "full body", "close-up", "costume", "folk costume"]

# Compression defaults
COMPRESS_MAX_WIDTH = 1200
COMPRESS_QUALITY = 85


def download_image(keywords, output_path, size="800x500"):
    """Download from Pexels API (high quality CC0). Falls back to LoremFlickr if API fails."""
    kw_encoded = keywords.replace(" ", "+")
    url = f"https://api.pexels.com/v1/search?query={kw_encoded}&per_page=5&orientation=portrait"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Authorization": PEXELS_API_KEY
    })

    data = None
    try:
        resp = urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        photos = result.get("photos", [])
        if photos:
            # Pick a random photo from top 5 results
            photo = random.choice(photos)
            img_url = photo["src"]["large"]
            alt_text = photo.get("alt", "")
            photographer = photo.get("photographer", "")
            print(f"    Pexels: {alt_text[:80].encode('ascii','replace').decode()} (by {photographer})")
            req2 = Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            data = urlopen(req2, timeout=30).read()
    except Exception as e:
        print(f"    Pexels failed: {e}, trying fallback...")

    if data is None:
        # Fallback to LoremFlickr/Picsum
        w, h = size.split("x")
        kw_fallback = keywords.replace(" ", ",")
        rand = random.randint(1, 999999)
        fallback_url = f"https://loremflickr.com/{w}/{h}/{kw_fallback}?random={rand}"
        try:
            req2 = Request(fallback_url, headers={"User-Agent": "Mozilla/5.0"})
            data = urlopen(req2, timeout=30).read()
        except Exception as e2:
            try:
                fallback_url2 = f"https://picsum.photos/{w}/{h}?random={rand}"
                req3 = Request(fallback_url2, headers={"User-Agent": "Mozilla/5.0"})
                data = urlopen(req3, timeout=30).read()
            except Exception as e3:
                raise RuntimeError(f"All sources failed: pexels={e}, loremflickr={e2}, picsum={e3}")

    if len(data) < 5000:
        raise RuntimeError(f"File too small ({len(data)} bytes), likely placeholder")

    output_path.write_bytes(data)
    return str(output_path)


def compress_image(image_path, max_width=COMPRESS_MAX_WIDTH, quality=COMPRESS_QUALITY):
    """Compress image: resize if too wide, strip EXIF, optimize JPEG. Overwrites original."""
    path = Path(image_path)
    img = Image.open(path)
    # Convert RGBA/P to RGB for JPEG
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    # Resize if wider than max
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    img.save(path, "JPEG", quality=quality, optimize=True)
    return path


def verify_with_doubao(image_path, check_prompt):
    """Verify image content via doubao_vision.analyze_image().
    Returns (passed: bool, detail: str)
    """
    prompt = f"{check_prompt}\n\nAnswer with YES or NO first, then briefly explain why."
    try:
        result = doubao_vision.analyze_image(str(image_path), prompt)
        text = (result or {}).get("text", "")
        if not text:
            return False, "No response from API"
        first_word = text.strip().split()[0].upper().rstrip(".,!?")
        if first_word == "YES":
            return True, text
        elif first_word == "NO":
            return False, text
        # If ambiguous, check for keywords
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["yes,", "yes ", "yes!"]):
            return True, text
        return False, f"Unclear response: {text[:200]}"
    except Exception as e:
        return False, f"Verification error: {e}"


def generate_with_seedream(prompt, output_path):
    """Generate image via Seedream 4.0 API (fallback when Pexels has no matching images).
    Returns (success: bool, path: str, detail: str)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Seedream prompt length limit ~500 chars, keep it concise
    short_prompt = prompt[:300] if len(prompt) > 300 else prompt
    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": f"A high-quality photograph of {short_prompt}. Realistic, well-lit, professional photography style.",
        "size": "2K",
        "watermark": False,
    }

    req = Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SEEDREAM_API_KEY}",
        },
    )

    try:
        resp = urlopen(req, timeout=120)
        resp_body = resp.read().decode()
        data = json.loads(resp_body)
        if "error" in data:
            err_code = data["error"].get("code", "")
            err_msg = data["error"].get("message", "")
            # If content filter triggered, retry with sanitized prompt
            if "SensitiveContent" in err_code or "sensitive" in err_msg.lower():
                clean = prompt[:250]
                for word in ["Blang","Buyei","Dongxiang","Gelao","Jing","Jino","Hani","Hezhen",
                             "Lisu","Maonan","Nu","Qiang","She","Tujia","Xibe","Dai","Lahu",
                             "Lhoba","Monba","Mulao","Naxi","Evenki","Daur","Deang","Derung",
                             "Bonan","Kyrgyz","Kazakh","Yugur","Salar","Tajik","Tatar","Uzbek",
                             "Xishuangbanna","Yunnan","Guizhou","Guangxi","Gansu","Sichuan",
                             "Heilongjiang","Xinjiang","Liaoning","Fujian","Zhejiang","Hunan",
                             "Honghe","Nujiang","Qapqal","Huanjiang"]:
                    clean = clean.replace(word, "traditional")
                clean = clean.replace(" ethnic group ", " ").replace("  ", " ").strip()
                payload["prompt"] = f"A high-quality photograph of {clean[:250]}. Traditional fashion style."
                req2 = Request(url, data=json.dumps(payload).encode(),
                    headers={"Content-Type":"application/json","Authorization":f"Bearer {SEEDREAM_API_KEY}"})
                resp2 = urlopen(req2, timeout=120)
                data = json.loads(resp2.read().decode())
                if "error" in data:
                    return False, str(output_path), f"Seedream API error (after sanitize): {data['error'].get('message', str(data['error']))}"
            else:
                return False, str(output_path), f"Seedream API error: {err_msg}"

        image_url = data.get("data", [{}])[0].get("url", "")
        if not image_url:
            return False, str(output_path), f"No image URL in Seedream response: {resp_body[:300]}"

        img_req = Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urlopen(img_req, timeout=60).read()
        if len(img_data) < 5000:
            return False, str(output_path), f"Seedream generated image too small ({len(img_data)} bytes)"

        output_path.write_bytes(img_data)
        return True, str(output_path), f"Generated by Seedream from prompt: {short_prompt[:150]}"
    except HTTPError as e:
        err_body = e.read().decode()[:500]
        # If sensitive content filter triggered (HTTP 400), retry with sanitized prompt
        if "SensitiveContent" in err_body or "sensitive" in err_body.lower():
            clean = prompt[:250]
            for word in ["Blang","Buyei","Dongxiang","Gelao","Jing","Jino","Hani","Hezhen",
                         "Lisu","Maonan","Nu","Qiang","She","Tujia","Xibe","Dai","Lahu",
                         "Lhoba","Monba","Mulao","Naxi","Evenki","Daur","Deang","Derung",
                         "Bonan","Kyrgyz","Kazakh","Yugur","Salar","Tajik","Tatar","Uzbek",
                         "Xishuangbanna","Yunnan","Guizhou","Guangxi","Gansu","Sichuan",
                         "Heilongjiang","Xinjiang","Liaoning","Fujian","Zhejiang","Hunan",
                         "Honghe","Nujiang","Qapqal","Huanjiang"]:
                clean = clean.replace(word, "traditional")
            clean = clean.replace(" ethnic group ", " ").replace("  ", " ").strip()
            sanitized_payload = {
                "model": SEEDREAM_MODEL,
                "prompt": f"A high-quality photograph of {clean[:250]}. Traditional fashion style.",
                "size": "2K",
                "watermark": False,
            }
            try:
                req2 = Request(url, data=json.dumps(sanitized_payload).encode(),
                    headers={"Content-Type":"application/json","Authorization":f"Bearer {SEEDREAM_API_KEY}"})
                resp2 = urlopen(req2, timeout=120)
                data2 = json.loads(resp2.read().decode())
                if "error" in data2:
                    return False, str(output_path), f"Seedream error after sanitize: {data2['error'].get('message','')}"
                image_url = data2.get("data", [{}])[0].get("url", "")
                if not image_url:
                    return False, str(output_path), "No image URL after sanitize retry"
                img_req = Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
                img_data = urlopen(img_req, timeout=60).read()
                if len(img_data) < 5000:
                    return False, str(output_path), "Image too small after sanitize"
                output_path.write_bytes(img_data)
                return True, str(output_path), f"Generated by Seedream (sanitized prompt): {clean[:150]}"
            except Exception as e2:
                return False, str(output_path), f"Seedream sanitize retry failed: {e2}"
        return False, str(output_path), f"Seedream HTTP {e.code}: {err_body}"
    except Exception as e:
        return False, str(output_path), f"Seedream generation failed: {e}"


def download_and_verify(keywords, output_path, check_prompt, max_retries=5):
    """Download -> verify -> delete & retry on failure. Returns (success, final_path, detail).
    Smart skip: if doubao identifies the image as a DIFFERENT ethnic group (e.g. Miao not Blang),
    we skip remaining Pexels retries and go straight to Seedream — Pexels simply doesn't have it.
    """
    output_path = Path(output_path)
    detail = ""
    # Ethnic group names that doubao might identify — if seen, Pexels returned wrong group
    KNOWN_WRONG_INDICATORS = [
        "Miao", "Hmong", "African", "Tibetan", "Mongolian", "Vietnamese",
        "Thai", "Indian", "Korean", "Japanese kimono", "Mexican", "costume",
    ]

    for attempt in range(max_retries):
        # Build keywords with variation on retry
        kw = keywords
        if attempt > 0:
            suffix_idx = (attempt - 1) % len(RETRY_SUFFIXES)
            kw = f"{keywords} {RETRY_SUFFIXES[suffix_idx]}"

        # Clean up failed file from previous attempt
        if output_path.exists():
            output_path.unlink()

        try:
            download_image(kw, output_path)
        except RuntimeError as e:
            detail = str(e)
            print(f"  [FAIL] {output_path.name} -- download failed ({e}) (retry {attempt+1}/{max_retries})")
            continue

        # Verify
        passed, detail = verify_with_doubao(output_path, check_prompt)
        if passed:
            compress_image(output_path)
            final_size = output_path.stat().st_size
            print(f"[OK] {output_path.name} ({final_size//1024}KB) -- {detail.strip()[:100]}")
            return True, str(output_path), detail
        else:
            print(f"  [FAIL] {output_path.name} -- {detail.strip()[:100]} (retry {attempt+1}/{max_retries})")
            if output_path.exists():
                output_path.unlink()
            # Smart skip: if doubao identified this as a different known group, Pexels won't have it
            detail_lower = detail.lower()
            if attempt == 0:  # Only check on first failure to avoid false positives
                for indicator in KNOWN_WRONG_INDICATORS:
                    if indicator.lower() in detail_lower:
                        print(f"  [SMART-SKIP] Doubao identified '{indicator}' — Pexels has no matching images, jumping to Seedream")
                        break
                else:
                    continue  # No indicator found, keep retrying Pexels
                break  # Indicator found, exit retry loop → fall through to Seedream

    # All Pexels retries exhausted — fallback to Seedream AI generation
    print(f"  [SEEDREAM] Generating {output_path.name} from prompt: {keywords[:80]}...")
    success, fpath, detail = generate_with_seedream(keywords, output_path)
    if success:
        compress_image(output_path)
        final_size = output_path.stat().st_size
        print(f"[OK] {output_path.name} ({final_size//1024}KB) — Seedream generated")
        return True, str(output_path), detail
    print(f"  [FAIL] {output_path.name} — Seedream also failed: {detail[:150]}")
    return False, str(output_path), detail


def batch_download(task_list, output_dir):
    """Process a list of download tasks serially with 1s interval.
    task_list: [{"keywords": ..., "filename": ..., "check": ...}, ...]
    Writes download_log.json to output_dir.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    total = len(task_list)
    passed = 0
    failed = 0

    for i, task in enumerate(task_list, 1):
        output_path = (output_dir / task["filename"]).resolve()
        print(f"\n[{i}/{total}] {task['filename']}")
        success, fpath, detail = download_and_verify(
            task["keywords"], output_path, task["check"]
        )
        results.append({
            "filename": task["filename"],
            "keywords": task["keywords"],
            "success": success,
            "path": fpath,
            "detail": detail[:300] if detail else "",
        })
        if success:
            passed += 1
        else:
            failed += 1
        if i < total:
            time.sleep(1)

    # Write log
    log_path = output_dir / "download_log.json"
    log_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== Batch Complete ===")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    print(f"Log written to: {log_path}")
    return results


def cli():
    import argparse
    parser = argparse.ArgumentParser(description="Download + verify images via Unsplash + Doubao")
    parser.add_argument("keywords", nargs="?", help="Search keywords for Unsplash")
    parser.add_argument("output_path", nargs="?", help="Output file path")
    parser.add_argument("--check", help="Verification prompt for Doubao")
    parser.add_argument("--batch", help="JSON task list file")
    parser.add_argument("--out", help="Output directory for batch mode")
    parser.add_argument("--verify-only", help="Only verify existing image, don't download")
    args = parser.parse_args()

    if args.verify_only:
        if not os.path.exists(args.verify_only):
            print(f"[FAIL] File not found: {args.verify_only}")
            sys.exit(1)
        passed, detail = verify_with_doubao(args.verify_only, args.check or "Describe this image")
        tag = "[OK]" if passed else "[FAIL]"
        print(f"{tag} {os.path.basename(args.verify_only)} -- {detail.strip()[:200]}")
        sys.exit(0 if passed else 1)

    if args.batch:
        tasks = json.loads(Path(args.batch).read_text(encoding="utf-8"))
        out_dir = args.out or "."
        batch_download(tasks, out_dir)
        return

    if not args.keywords or not args.output_path:
        parser.print_help()
        sys.exit(1)

    success, path, detail = download_and_verify(
        args.keywords, args.output_path, args.check or "Describe this image"
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cli()
