"""Batch download + parallel Doubao verify + Seedream fallback."""
import json, time, os, base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib.parse import quote

PEXELS_KEY = "QpCSbvN6HrNuL2bYBy7090p5VI2zTqEsqeSvQF92sxMG0bcmhrhJ0OL8"
ARK_KEY = "ark-71e489d9-8720-4ce9-ac4b-30c178333e33-02a59"
ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
DOUBAO_MODEL = "doubao-seed-1-6-vision-250815"
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
IMAGES_DIR = Path(r'd:\AI网站文件夹\clothing-site\images')

def pexels_download(keywords, output_path, per_page=5):
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get("https://api.pexels.com/v1/search",
                      headers=headers,
                      params={"query": keywords, "per_page": per_page, "orientation": "portrait", "size": "large"},
                      timeout=15)
    if r.status_code != 200:
        return None, f"Pexels API {r.status_code}"
    photos = r.json().get("photos", [])
    if not photos:
        return None, "No results"
    for photo in photos:
        src = photo["src"].get("portrait") or photo["src"].get("large2x") or photo["src"].get("large")
        try:
            img_data = requests.get(src, timeout=30).content
            if len(img_data) > 5000:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                Path(output_path).write_bytes(img_data)
                return str(output_path), f"Pexels: {photo['photographer']}"
        except:
            continue
    return None, "All download attempts failed"

def doubao_verify(image_path, check_prompt):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    prompt = f"{check_prompt}\n\nAnswer with YES or NO first, then briefly explain why."
    payload = {
        "model": DOUBAO_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": prompt}
        ]}],
        "max_tokens": 200
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ARK_KEY}"}
    try:
        r = requests.post(DOUBAO_URL, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return False, f"API {r.status_code}"
        text = r.json()["choices"][0]["message"]["content"].strip().upper()
        return text.startswith("YES"), text[:200]
    except Exception as e:
        return False, str(e)[:100]

def seedream_gen(prompt, output_path):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ARK_KEY}"}
    payload = {"model": "doubao-seedream-5-0-260128", "prompt": prompt, "size": "1024x1024", "n": 1}
    r = requests.post(ARK_URL, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        return False, f"Seedream API {r.status_code}"
    data = r.json()
    img_url = data.get("data", [{}])[0].get("url")
    if not img_url:
        return False, "No URL"
    img_data = requests.get(img_url, timeout=60).content
    if len(img_data) < 3000:
        return False, f"Too small: {len(img_data)}"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_bytes(img_data)
    return True, f"Seedream from: {prompt[:80]}"

def phase1_download(tasks):
    """Download all from Pexels. Returns list of (task, path) for verification."""
    verify_list = []
    for i, task in enumerate(tasks, 1):
        opath = IMAGES_DIR / task["filename"]
        if opath.exists() and opath.stat().st_size > 5000:
            verify_list.append((task, str(opath)))
            print(f"[{i}/{len(tasks)}] SKIP {task['filename']}")
            continue
        print(f"[{i}/{len(tasks)}] DL {task['filename']} ...", end=" ", flush=True)
        path, detail = pexels_download(task["keywords"], opath)
        if path:
            print("OK")
            verify_list.append((task, path))
        else:
            print(f"FAIL ({detail[:50]})")
            verify_list.append((task, None))
        time.sleep(0.3)
    return verify_list

def phase2_verify(verify_list, max_workers=5):
    """Parallel verify downloaded images. Returns list of (task, success, path)."""
    def verify_one(item):
        task, path = item
        if path is None:
            return (task, False, None)
        ok, detail = doubao_verify(path, task["check"])
        print(f"  VERIFY {task['filename']}: {'OK' if ok else 'FAIL — ' + detail[:60]}")
        return (task, ok, path if ok else None)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(verify_one, item): item for item in verify_list}
        for f in as_completed(futures):
            results.append(f.result())
    return results

def phase3_fallback(failed_tasks):
    """Seedream for failed tasks."""
    for task in failed_tasks:
        opath = IMAGES_DIR / task["filename"]
        prompt = task["keywords"].replace("Chinese ethnic minority traditional", "traditional Chinese ethnic").replace("costume", "attire, full body shot, clean white background, studio photography")
        print(f"  SEEDREAM {task['filename']} ...", end=" ", flush=True)
        ok, detail = seedream_gen(prompt, opath)
        print("OK" if ok else f"FAIL: {detail}")
        if not ok and opath.exists():
            opath.unlink()
        time.sleep(0.5)

def main():
    # Rebuild task list
    pages_dir = Path(r'd:\AI网站文件夹\clothing-site\chinese\56-ethnic-groups')
    tasks = []
    for fname in sorted(os.listdir(pages_dir)):
        if fname == 'index.html' or not fname.endswith('.html'):
            continue
        ethnic = fname.replace('.html', '')
        if ethnic == 'han':
            continue
        tasks.append({"filename": f"{ethnic}_male.jpg", "keywords": f"{ethnic} Chinese ethnic minority traditional male clothing costume", "check": f"YES if this image shows traditional male clothing/costume of the {ethnic} ethnic group. NO if wrong ethnic group, wrong gender, or not traditional clothing."})
        tasks.append({"filename": f"{ethnic}_female.jpg", "keywords": f"{ethnic} Chinese ethnic minority traditional female clothing costume", "check": f"YES if this image shows traditional female clothing/costume of the {ethnic} ethnic group. NO if wrong ethnic group, wrong gender, or not traditional clothing."})

    print(f"=== Phase 1: Download {len(tasks)} images from Pexels ===")
    verify_list = phase1_download(tasks)

    print(f"\n=== Phase 2: Verify with Doubao (parallel x5) ===")
    verify_results = phase2_verify(verify_list, max_workers=5)

    passed = sum(1 for _, ok, _ in verify_results if ok)
    failed = [(t, _) for t, ok, _ in verify_results if not ok]
    print(f"\nVerification: {passed}/{len(tasks)} passed, {len(failed)} failed")

    if failed:
        print(f"\n=== Phase 3: Seedream for {len(failed)} failed ===")
        phase3_fallback([t for t, _ in failed])

    # Final tally
    final_ok = 0
    for t in tasks:
        p = IMAGES_DIR / t["filename"]
        if p.exists() and p.stat().st_size > 5000:
            final_ok += 1
    print(f"\n=== DONE: {final_ok}/{len(tasks)} images ready ===")

if __name__ == '__main__':
    main()
