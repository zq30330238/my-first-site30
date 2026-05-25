#!/usr/bin/env python3
"""RightsDaily Image Fix Script

1. Scans article-1.html ~ article-36.html
2. For articles missing <img>: extracts h1, calls Seedream API, injects img tag
3. Downloads & resizes images to 1280x720
4. Updates index.html to replace Unsplash URLs with local image paths
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image

BASE_DIR = r"d:\AI网站文件夹\rightsdaily"
IMAGES_DIR = os.path.join(BASE_DIR, "images")

SEEDREAM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_API_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
SEEDREAM_MODEL = "doubao-seedream-4-5-251128"

os.makedirs(IMAGES_DIR, exist_ok=True)


def extract_title(html):
    """Extract article title from <h1> tag."""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    return m.group(1).strip() if m else None


def has_img_tag(html):
    """Check if article already has an <img> tag."""
    return bool(re.search(r'<img\s', html, re.IGNORECASE))


def call_seedream(prompt, retries=2):
    """Call Seedream 5.0 API to generate an image. Returns image URL."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SEEDREAM_API_KEY}"
    }
    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "2560x1440"
    }

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                SEEDREAM_API_URL,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode())
                img_url = data["data"][0]["url"]
                return img_url
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  API HTTP {e.code}: {body[:200]}")
            if attempt < retries:
                wait = 5 * (attempt + 1)
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            print(f"  API error: {e}")
            if attempt < retries:
                time.sleep(5)
            else:
                raise


def download_and_resize(url, save_path, max_width=1200):
    """Download image, resize to max_width, save as JPEG quality 85."""
    with urllib.request.urlopen(url, timeout=120) as resp:
        img_data = resp.read()
    img = Image.open(BytesIO(img_data))
    if img.mode == "RGBA":
        img = img.convert("RGB")
    w, h = img.size
    if w > max_width:
        ratio = max_width / w
        new_h = int(h * ratio)
        img = img.resize((max_width, new_h), Image.LANCZOS)
    img.save(save_path, "JPEG", quality=85)
    print(f"  Saved: {save_path} ({img.size[0]}x{img.size[1]})")


def inject_img_tag(html, img_path, alt_text):
    """Inject <img> tag after article </header>, before article-content div."""
    img_tag = (
        f'<img src="{img_path}" alt="{alt_text}" '
        f'class="w-full h-full object-cover" loading="lazy">'
    )
    # Match </header> followed by <div class="article-content">
    # This uniquely identifies the article header (not the page header)
    pattern = r'(</header>\s*)(<div class="article-content">)'
    replacement = r'\1        ' + img_tag + r'\n        \2'
    new_html = re.sub(pattern, replacement, html, count=1)
    return new_html


def process_articles():
    """Process all article files, generate images, inject img tags."""
    generated = 0
    skipped = 0
    updated_html = 0

    for i in range(1, 37):
        article_file = os.path.join(BASE_DIR, f"article-{i}.html")
        img_file = os.path.join(IMAGES_DIR, f"article-{i}.jpg")

        if not os.path.exists(article_file):
            print(f"[{i:02d}] File not found, skipping")
            continue

        with open(article_file, "r", encoding="utf-8") as f:
            html = f.read()

        # Check if article already has img tag
        if has_img_tag(html):
            print(f"[{i:02d}] Already has <img>, skipping")
            skipped += 1
            continue

        # Extract title from h1
        title = extract_title(html)
        if not title:
            print(f"[{i:02d}] Could not find <h1> title, skipping")
            skipped += 1
            continue

        print(f"[{i:02d}] Processing: {title}")

        # Generate image if not already exists
        if os.path.exists(img_file):
            print(f"  Image already exists: {img_file}")
        else:
            prompt = (
                f"Stock photography style image on the topic of: {title}. "
                f"Professional, natural lighting, suitable for legal rights website article header."
            )
            print(f"  Calling Seedream API...")
            try:
                img_url = call_seedream(prompt)
                print(f"  Got image URL: {img_url[:80]}...")
                time.sleep(1)  # rate limit courtesy
                download_and_resize(img_url, img_file)
                generated += 1
            except Exception as e:
                print(f"  FAILED to generate image: {e}")
                skipped += 1
                continue

        # Inject img tag into HTML
        img_rel_path = f"images/article-{i}.jpg"
        # Escape quotes in title for use in HTML attribute
        safe_title = title.replace('"', '&quot;')
        new_html = inject_img_tag(html, img_rel_path, safe_title)

        if new_html != html:
            with open(article_file, "w", encoding="utf-8") as f:
                f.write(new_html)
            print(f"  Updated HTML: {article_file}")
            updated_html += 1
        else:
            print(f"  WARNING: HTML injection pattern not found")
            skipped += 1

        print()

    return generated, skipped, updated_html


def update_index():
    """Update index.html: replace Unsplash URLs with local image paths."""
    index_file = os.path.join(BASE_DIR, "index.html")

    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()

    def replace_card_bg(match):
        """Replace background-image URL in an article card with local path."""
        card_html = match.group(0)
        article_num = match.group(1)
        local_path = f"images/article-{article_num}.jpg"
        card_html = re.sub(
            r'background-image:url\([^)]*\)',
            f'background-image:url({local_path})',
            card_html
        )
        return card_html

    # Match each article-card block with its href article number
    pattern = (
        r'<a href="article-(\d+)\.html[^>]*'
        r'class="article-card[^"]*"[^>]*>.*?</a>'
    )
    new_html = re.sub(pattern, replace_card_bg, html, flags=re.DOTALL)

    if new_html != html:
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"Updated: {index_file}")
        return True
    else:
        print("Index.html: no changes made (all URLs already local)")
        return False


def main():
    print("=" * 60)
    print("  RightsDaily Image Fix Script")
    print("=" * 60)
    print()

    # Step 1: Process articles
    print("--- Step 1: Processing articles ---")
    generated, skipped, updated_html = process_articles()

    print()
    print("=" * 60)
    print("  Summary:")
    print(f"    Images generated:     {generated}")
    print(f"    Articles skipped:     {skipped}")
    print(f"    HTML files updated:   {updated_html}")
    print()

    # Step 2: Update index.html
    print("--- Step 2: Updating index.html ---")
    update_index()

    print()
    print("Done!")


if __name__ == "__main__":
    main()
