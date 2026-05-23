"""Batch generate Seedream cover images for all sub-sites."""
import json, urllib.request, time, re, os, glob

SEEDREAM_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
SEEDREAM_MODEL = "doubao-seedream-5-0-260128"
ROOT = "/root/my-first-site30"

# Site theme mapping for good prompts
SITE_THEMES = {
    "sub-healthy": "healthy food, nutrition, fresh ingredients",
    "sub-pets": "pet care, animals, pets",
    "sub-home": "home improvement, gardening, interior design",
    "sub-finance": "personal finance, money management, investing",
    "sub-tech": "technology, gadgets, digital tools",
    "sub-travel": "travel, destinations, adventure",
}

def generate_and_inject(site_dir, article_num, title, theme):
    """Generate an image for a single article."""
    img_dir = f"{ROOT}/{site_dir}/images"
    os.makedirs(img_dir, exist_ok=True)
    img_path = f"{img_dir}/article-{article_num}.jpg"
    img_rel = f"images/article-{article_num}.jpg"

    prompt = (f"A professional, high-quality {theme} themed photograph: {title[:80]}. "
              f"Clean, well-lit, photorealistic style, 16:9 landscape. "
              f"ABSOLUTELY NO watermark, NO text, NO logo, NO words on the image.")

    body = json.dumps({
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "2560x1440",
        "watermark": False,
    }).encode()

    req = urllib.request.Request(
        SEEDREAM_URL, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SEEDREAM_KEY}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        img_url = data["data"][0]["url"]
        urllib.request.urlretrieve(img_url, img_path)
        size = os.path.getsize(img_path) // 1000

        # Resize
        try:
            from PIL import Image
            img = Image.open(img_path)
            img = img.resize((1200, 675), Image.LANCZOS)
            img = img.convert("RGB")
            img.save(img_path, "JPEG", quality=85)
        except ImportError:
            pass

        # Inject into article HTML
        art_file = f"{ROOT}/{site_dir}/article-{article_num}.html"
        html = open(art_file).read()

        hero = f'\n<div class="w-full h-64 md:h-96 bg-cover bg-center" style="background-image:url({img_rel})"></div>\n'
        html = re.sub(r'(<body[^>]*>)', r'\1' + hero, html, count=1)

        open(art_file, "w").write(html)
        print(f"  OK article-{article_num}: {size}KB")
        return True
    except Exception as e:
        print(f"  FAIL article-{article_num}: {e}")
        return False

# Main: process all 6 sub-sites
total = 0
done = 0
for site_dir in sorted(SITE_THEMES.keys()):
    theme = SITE_THEMES[site_dir]
    article_files = sorted(glob.glob(f"{ROOT}/{site_dir}/article-*.html"))
    missing = []

    for af in article_files:
        html = open(af).read()
        if "images/article-" not in html:
            m = re.search(r"article-(\d+)", af)
            num = int(m.group(1)) if m else 0
            t = re.search(r"<title>(.*?)</title>", html)
            title = t.group(1).split("–")[0].strip() if t else ""
            missing.append((num, title))

    if not missing:
        print(f"\n{site_dir}: ALL {len(article_files)} articles have images, skipping")
        continue

    print(f"\n{site_dir}: {len(missing)}/{len(article_files)} need images")
    total += len(missing)

    for num, title in missing:
        time.sleep(3)  # Rate limit
        if generate_and_inject(site_dir, num, title, theme):
            done += 1

print(f"\n=== DONE: {done}/{total} images generated ===")
