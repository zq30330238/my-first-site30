"""下载SAO正确图片替换错误文件"""
import os
import requests
import re
import io
import sys
from urllib.parse import unquote

SAVE_DIR = r"d:\AI网站文件夹\sao-site\images"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ============================================================
# 1. Akihiko Kayaba
# ============================================================
def download_kayaba():
    """Try multiple sources for Akihiko Kayaba"""
    dest = os.path.join(SAVE_DIR, "akihiko-kayaba.png")

    sources = [
        # Fandom CDN: common Kayaba image paths
        "https://static.wikia.nocookie.net/sword-art-online/images/0/06/Akihiko_Kayaba.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/0/06/Akihiko_Kayaba.png/revision/latest?cb=20200101000000",
        "https://static.wikia.nocookie.net/sword-art-online/images/0/06/Akihiko_Kayaba.png/revision/latest/scale-to-width-down/1000",
        "https://static.wikia.nocookie.net/sword-art-online/images/a/a4/Kayaba_Akihiko.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/a/a4/Kayaba_Akihiko.png/revision/latest",
        # Heathcliff (Kayaba's in-game avatar)
        "https://static.wikia.nocookie.net/sword-art-online/images/6/6e/Heathcliff_%28SAO%29.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/6/6e/Heathcliff_%28SAO%29.png/revision/latest",
        # Alternative filenames
        "https://static.wikia.nocookie.net/sword-art-online/images/9/97/Kayaba.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/9/97/Kayaba.png/revision/latest",
    ]

    for url in sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 5000:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct or r.content[:4] in [b'\x89PNG', b'\xff\xd8\xff']:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    print(f"[KAYABA] Downloaded from: {url}")
                    print(f"[KAYABA] Size: {len(r.content)} bytes, Type: {ct}")
                    return True
            else:
                print(f"[KAYABA] Failed: {url} -> status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"[KAYABA] Error: {url} -> {e}")

    # Try hiclipart
    try:
        url = "https://www.hiclipart.com/free-transparent-background-png-clipart-icben"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            # Find image URL in page
            img_urls = re.findall(r'https?://[^"\']+\.(?:png|jpg|jpeg)(?:\?[^"\']*)?', r.text)
            for img_url in img_urls:
                if 'hiclipart' in img_url or 'icben' in img_url:
                    ir = requests.get(img_url, headers=HEADERS, timeout=10)
                    if ir.status_code == 200 and len(ir.content) > 5000:
                        with open(dest, "wb") as f:
                            f.write(ir.content)
                        print(f"[KAYABA] Downloaded from hiclipart: {img_url}")
                        return True
    except Exception as e:
        print(f"[KAYABA] hiclipart error: {e}")

    print("[KAYABA] FAILED - no source worked")
    return False


# ============================================================
# 2. Dark Repulser
# ============================================================
def download_dark_repulser():
    """Try multiple sources for Dark Repulser"""
    dest = os.path.join(SAVE_DIR, "dark-repulser.png")

    sources = [
        "https://static.wikia.nocookie.net/sword-art-online/images/2/2d/Dark_Repulser.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/2/2d/Dark_Repulser.png/revision/latest",
        "https://static.wikia.nocookie.net/sword-art-online/images/2/2d/Dark_Repulser.png/revision/latest/scale-to-width-down/1000",
        "https://static.wikia.nocookie.net/sword-art-online/images/1/1b/Dark_Repulser_%28SAO%29.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/1/1b/Dark_Repulser_%28SAO%29.png/revision/latest",
        "https://static.wikia.nocookie.net/sword-art-online/images/d/d6/Dark_Repulser_%28Anime%29.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/d/d6/Dark_Repulser_%28Anime%29.png/revision/latest",
    ]

    for url in sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 3000:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct or r.content[:4] in [b'\x89PNG', b'\xff\xd8\xff']:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    print(f"[DARK_REPULSER] Downloaded from: {url}")
                    print(f"[DARK_REPULSER] Size: {len(r.content)} bytes, Type: {ct}")
                    return True
            else:
                print(f"[DARK_REPULSER] Failed: {url} -> status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"[DARK_REPULSER] Error: {url} -> {e}")

    # Try toppng
    try:
        url = "https://toppng.com/free-image/28-collection-of-kirito-sword-dark-repulser-drawing-sword-art-online-sword-PNG-free-PNG-Images_226877"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            img_urls = re.findall(r'https?://[^"\']+\.(?:png|jpg|jpeg)(?:\?[^"\']*)?', r.text)
            for img_url in img_urls:
                if 'toppng' in img_url or 'dark' in img_url.lower():
                    ir = requests.get(img_url, headers=HEADERS, timeout=10)
                    if ir.status_code == 200 and len(ir.content) > 3000:
                        with open(dest, "wb") as f:
                            f.write(ir.content)
                        print(f"[DARK_REPULSER] Downloaded from toppng: {img_url}")
                        return True
    except Exception as e:
        print(f"[DARK_REPULSER] toppng error: {e}")

    print("[DARK_REPULSER] FAILED - no source worked")
    return False


# ============================================================
# 3. Fragrant Olive
# ============================================================
def download_fragrant_olive():
    """Try multiple sources for Fragrant Olive"""
    dest = os.path.join(SAVE_DIR, "fragrant-olive.png")

    sources = [
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Fragrant_Olive.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Fragrant_Olive.png/revision/latest",
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Fragrant_Olive.png/revision/latest/scale-to-width-down/1000",
        "https://static.wikia.nocookie.net/sword-art-online/images/1/1a/Fragrant_Olive_Sword.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/1/1a/Fragrant_Olive_Sword.png/revision/latest",
    ]

    for url in sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 3000:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct or r.content[:4] in [b'\x89PNG', b'\xff\xd8\xff']:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    print(f"[FRAGRANT_OLIVE] Downloaded from: {url}")
                    print(f"[FRAGRANT_OLIVE] Size: {len(r.content)} bytes, Type: {ct}")
                    return True
            else:
                print(f"[FRAGRANT_OLIVE] Failed: {url} -> status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"[FRAGRANT_OLIVE] Error: {url} -> {e}")

    print("[FRAGRANT_OLIVE] FAILED - no source worked")
    return False


# ============================================================
# 4. Holy Sword (Excaliber)
# ============================================================
def download_holy_sword():
    """Try multiple sources for Holy Sword / Excaliber"""
    dest = os.path.join(SAVE_DIR, "holy-sword.png")

    sources = [
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Excaliber.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Excaliber.png/revision/latest",
        "https://static.wikia.nocookie.net/sword-art-online/images/8/81/Excaliber.png/revision/latest/scale-to-width-down/1000",
        "https://static.wikia.nocookie.net/sword-art-online/images/5/5e/Excaliber_%28Anime%29.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/5/5e/Excaliber_%28Anime%29.png/revision/latest",
        "https://static.wikia.nocookie.net/sword-art-online/images/5/5e/Excaliber_%28Anime%29.png/revision/latest/scale-to-width-down/1000",
        "https://static.wikia.nocookie.net/sword-art-online/images/7/70/Holy_Sword_Excaliber.png",
        "https://static.wikia.nocookie.net/sword-art-online/images/7/70/Holy_Sword_Excaliber.png/revision/latest",
    ]

    for url in sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 3000:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct or r.content[:4] in [b'\x89PNG', b'\xff\xd8\xff']:
                    with open(dest, "wb") as f:
                        f.write(r.content)
                    print(f"[HOLY_SWORD] Downloaded from: {url}")
                    print(f"[HOLY_SWORD] Size: {len(r.content)} bytes, Type: {ct}")
                    return True
            else:
                print(f"[HOLY_SWORD] Failed: {url} -> status={r.status_code}, size={len(r.content)}")
        except Exception as e:
            print(f"[HOLY_SWORD] Error: {url} -> {e}")

    print("[HOLY_SWORD] FAILED - no source worked")
    return False


if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)

    results = {}
    results["akihiko-kayaba"] = download_kayaba()
    results["dark-repulser"] = download_dark_repulser()
    results["fragrant-olive"] = download_fragrant_olive()
    results["holy-sword"] = download_holy_sword()

    print("\n=== RESULTS ===")
    for name, success in results.items():
        print(f"  {name}: {'OK' if success else 'FAILED'}")

    if not all(results.values()):
        print("\nSome downloads failed!")
        sys.exit(1)
    else:
        print("\nAll downloads successful!")
