"""Fast batch download: Pexels (no verify) → Seedream fallback for failed."""
import json, time, os, sys
from pathlib import Path
import requests
from urllib.parse import quote

PEXELS_KEY = "QpCSbvN6HrNuL2bYBy7090p5VI2zTqEsqeSvQF92sxMG0bcmhrhJ0OL8"
ARK_KEY = "ark-71e489d9-8720-4ce9-ac4b-30c178333e33-02a59"
ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

def pexels_download(keywords, output_path):
    headers = {"Authorization": PEXELS_KEY}
    params = {"query": keywords, "per_page": 5, "orientation": "portrait", "size": "large"}
    r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
    if r.status_code != 200:
        return False, f"Pexels API {r.status_code}"
    photos = r.json().get("photos", [])
    if not photos:
        return False, "No Pexels results"
    for photo in photos:
        src = photo["src"].get("portrait") or photo["src"].get("large2x") or photo["src"].get("large")
        try:
            img_data = requests.get(src, timeout=30).content
            if len(img_data) > 5000:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                Path(output_path).write_bytes(img_data)
                return True, f"Pexels: {photo['photographer']}"
        except:
            continue
    return False, "All Pexels download attempts failed"

def seedream_generate(prompt, output_path):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ARK_KEY}"}
    payload = {"model": "doubao-seedream-5-0-260128", "prompt": prompt, "size": "1024x1024", "n": 1}
    r = requests.post(ARK_URL, headers=headers, json=payload, timeout=120)
    if r.status_code != 200:
        return False, f"Seedream API {r.status_code}: {r.text[:200]}"
    data = r.json()
    img_url = data.get("data", [{}])[0].get("url")
    if not img_url:
        return False, f"No URL in response: {r.text[:200]}"
    img_data = requests.get(img_url, timeout=60).content
    if len(img_data) < 3000:
        return False, f"Seedream img too small: {len(img_data)}"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_bytes(img_data)
    return True, f"Seedream: {prompt[:100]}"

def main():
    tasks = json.load(open(r'd:\AI网站文件夹\temp_ethnic_tasks.json'))
    out_dir = Path(r'd:\AI网站文件夹\clothing-site\images')
    results = []
    passed = 0
    failed = 0
    remaining = []

    for i, task in enumerate(tasks, 1):
        fname = task["filename"]
        opath = out_dir / fname
        if opath.exists() and opath.stat().st_size > 5000:
            print(f"[{i}/{len(tasks)}] SKIP {fname} (exists)")
            passed += 1
            continue

        print(f"[{i}/{len(tasks)}] {fname} ...", end=" ", flush=True)
        success, detail = pexels_download(task["keywords"], opath)
        if not success:
            print(f"Pexels FAIL → Seedream...", end=" ", flush=True)
            seed_prompt = task["keywords"].replace("Chinese ethnic minority traditional", "traditional Chinese").replace("costume", "costume, full body shot, studio lighting, clean background")
            success, detail = seedream_generate(seed_prompt, opath)

        if success:
            print("OK", detail[:60])
            passed += 1
        else:
            print("FAIL", detail[:80])
            failed += 1
            remaining.append(task)

        results.append({"filename": fname, "success": success, "detail": detail})
        if i < len(tasks):
            time.sleep(0.5)

    log = out_dir / "download_log.json"
    log.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. Passed: {passed}, Failed: {failed}, Total: {len(tasks)}")
    if remaining:
        print(f"Failed tasks saved to log for retry")
        with open(r'd:\AI网站文件夹\temp_ethnic_retry.json', 'w') as f:
            json.dump(remaining, f, indent=2)

if __name__ == '__main__':
    main()
