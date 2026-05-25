#!/usr/bin/env python3
"""
fix_images.py - Generate Seedream AI images for dailymedadvice.com articles
that are missing <img> tags, and update index.html to use local images.

Usage:  python fix_images.py
"""

import os
import re
import json
import time
import urllib.request
import urllib.error
from io import BytesIO
from PIL import Image

BASE_DIR = r"d:\AI网站文件夹\dailymedadvice"
IMAGES_DIR = os.path.join(BASE_DIR, "images")

SEEDREAM_API_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
SEEDREAM_API_KEY = "ark-bc9c6af0-1813-4842-ae3f-0614d354c375-98727"
SEEDREAM_MODEL = "doubao-seedream-4-5-251128"


def extract_title(html_content):
    """Extract article title from <h1> tag."""
    match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def has_img_tag(html_content):
    """Check if the article already has an <img> tag."""
    return '<img ' in html_content or '<img\n' in html_content or '<img\t' in html_content


def call_seedream_api(title):
    """Call Seedream API to generate an image for the given title."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SEEDREAM_API_KEY}"
    }
    # Clean title for API prompt
    clean_title = re.sub(r'<[^>]+>', '', title).strip()
    prompt = (
        f"Stock photography style image on the topic of: {clean_title}. "
        f"Professional, natural lighting, suitable for health and medical website article header."
    )
    payload = {
        "model": SEEDREAM_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "2560x1440"
    }

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


def download_and_resize(img_url, output_path):
    """Download image, resize width to max 1200px, save as JPEG quality 85."""
    req = urllib.request.Request(img_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        img_data = resp.read()

    img = Image.open(BytesIO(img_data))

    # Resize width to max 1200px, keep aspect ratio
    if img.width > 1200:
        ratio = 1200.0 / img.width
        new_height = int(img.height * ratio)
        img = img.resize((1200, new_height), Image.LANCZOS)

    # Convert to RGB for JPEG saving
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img.save(output_path, 'JPEG', quality=85)


def inject_img_tag(html_content, article_num, title):
    """
    Inject <img> tag after the article header's </header>
    and before <div class="article-content">.

    Important: there are TWO </header> tags in each page:
      1. Nav bar header (followed by <main>)
      2. Article header (followed by <div class="article-content">)
    We must only match #2.
    """
    img_tag = (
        f'<img src="images/article-{article_num}.jpg" '
        f'alt="{title}" '
        f'class="w-full h-full object-cover" loading="lazy">'
    )

    # Match the article-header </header> followed by <div class="article-content">
    result = re.sub(
        r'</header>(?=\s*<div class="article-content")',
        '</header>\n        ' + img_tag,
        html_content
    )

    if result == html_content:
        # Fallback: just insert before <div class="article-content">
        result = re.sub(
            r'(?=<div class="article-content")',
            img_tag + '\n        ',
            html_content
        )

    return result


def process_article(num):
    """Process a single article: generate image + inject img tag."""
    html_path = os.path.join(BASE_DIR, f"article-{num}.html")
    img_path = os.path.join(IMAGES_DIR, f"article-{num}.jpg")

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Skip if already has img tag
    if has_img_tag(html):
        return "already_has_img"

    # Extract title
    title = extract_title(html)
    if not title:
        return "no_title"

    # Inject img tag if image already exists on disk
    if os.path.exists(img_path):
        html = inject_img_tag(html, num, title)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return "injected_only"

    # Call API, download, inject
    print(f"  -> Title: {title[:60]}...")
    img_url = call_seedream_api(title)
    print(f"  -> API returned URL: {img_url[:80] if img_url else 'N/A'}...")

    download_and_resize(img_url, img_path)
    print(f"  -> Saved to {img_path}")

    html = inject_img_tag(html, num, title)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return "generated"


def process_articles():
    """Main article processing loop."""
    os.makedirs(IMAGES_DIR, exist_ok=True)

    stats = {
        "total": 33,
        "already_has_img": 0,
        "generated": 0,
        "injected_only": 0,
        "failed": 0,
        "no_title": 0,
    }

    for i in range(1, 34):
        print(f"\n[{i:02d}/33] Processing article-{i}.html...", end="")
        try:
            result = process_article(i)
            stats[result] = stats.get(result, 0) + 1

            labels = {
                "already_has_img": "Already has <img>, skipped",
                "generated": "Image generated + injected",
                "injected_only": "Image file existed, injected tag only",
                "no_title": "No <h1> found, skipped",
                "failed": "FAILED",
            }
            print(f" {labels.get(result, result)}")

            # Rate limit: 1 second between API calls
            if result == "generated":
                time.sleep(1)

        except Exception as e:
            stats["failed"] += 1
            print(f" FAILED: {e}")
            # Still wait a bit even on failure
            time.sleep(2)

    return stats


def update_index_html():
    """
    Update index.html: replace Unsplash background-image URLs
    with local images/article-N.jpg paths.
    """
    index_path = os.path.join(BASE_DIR, "index.html")

    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    old_html = html

    # Match: href="article-N.html" ... background-image:url(https://images.unsplash.com/...)
    # Replace unsplash URL with local image path for that article
    pattern = (
        r'(href="article-(\d+)\.html"[^>]*>\s*'
        r'<div class="h-48 bg-cover bg-center" style=")'
        r'background-image:url\(https://images\.unsplash\.com/[^)]+\)'
    )

    def replacer(match):
        prefix = match.group(1)
        article_num = match.group(2)
        return f'{prefix}background-image:url(images/article-{article_num}.jpg)'

    new_html = re.sub(pattern, replacer, html)

    # Also handle the sidebar recent-posts if they have unsplash references
    # (unlikely but safe)

    if new_html != old_html:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        # Count replacements
        count = len(re.findall(pattern, html))
        return count
    return 0


def main():
    print("=" * 65)
    print("  DailyMedAdvice - Image Generation via Seedream 5.0")
    print("=" * 65)

    stats = process_articles()

    print("\n" + "=" * 65)
    print("  ARTICLE STATISTICS:")
    print(f"    Total articles:         {stats['total']}")
    print(f"    Already had <img>:      {stats['already_has_img']}")
    print(f"    Generated + injected:   {stats['generated']}")
    print(f"    Injected only (file existed): {stats['injected_only']}")
    print(f"    Failed:                 {stats['failed']}")
    print(f"    No title found:         {stats['no_title']}")

    print("\n" + "=" * 65)
    print("  Updating index.html...")
    replaced = update_index_html()
    if replaced:
        print(f"    Replaced {replaced} Unsplash URLs with local image paths.")
    else:
        print("    No Unsplash URLs found to replace (already updated).")

    print("\n" + "=" * 65)
    print("  DONE!")
    print("=" * 65)


if __name__ == "__main__":
    main()
