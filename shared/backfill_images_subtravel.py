"""Backfill missing cover images for sub-travel articles using Seedream 5.0.

Usage: python shared/backfill_images_subtravel.py
"""
import sys
import os
import re
import time
from pathlib import Path

# Add shared dir to path and import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from create_articles import generate_and_verify_image, ROOT

SITE_DIR = "sub-travel"
DOMAIN = "travel.jycsd.com"

# Articles that need images (from user's list, after filtering out already-complete ones)
MISSING_ARTICLES = [2, 3, 4, 5, 6, 7, 8, 9, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

def extract_title_and_desc(html):
    """Extract h1_title and meta description from article HTML."""
    # H1 title
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "Untitled"

    # Meta description
    desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    description = desc_match.group(1) if desc_match else title

    return title, description


def has_local_image(html, article_num):
    """Check if article HTML already references a local image."""
    pattern = re.compile(r'<img[^>]*src\s*=\s*"images/article-' + str(article_num) + r'\.jpg"')
    return bool(pattern.search(html))


def replace_article_img(html, article_num, image_url):
    """Replace Unsplash/gradient/placeholder img with local image in article HTML.
    Returns updated HTML."""
    local_src = f"images/article-{article_num}.jpg"

    # Case 1: Has <img> with external URL - replace src
    img_pattern = re.compile(r'(<img\s[\s\S]*?src\s*=\s*")[^"]*("[\s\S]*?>)')
    new_html, count = img_pattern.subn(r'\1' + local_src + r'\2', html, count=1)

    if count > 0:
        return new_html

    # Case 2: Has gradient placeholder div - replace it with img
    gradient_pattern = re.compile(
        r'<div\s+class="w-full h-64 rounded-2xl mb-10 bg-gradient-to-br[^"]*"[^>]*>.*?</div>',
        re.DOTALL
    )
    new_html, count = gradient_pattern.subn(
        f'<img src="{local_src}" alt="Travel article image" class="w-full rounded-2xl mb-10" loading="lazy">',
        html, count=1
    )

    if count > 0:
        return new_html

    # Case 3: No image at all - insert after </header>
    new_html = html.replace(
        '</header>',
        f'</header>\n        <img src="{local_src}" alt="Travel article image" class="w-full rounded-2xl mb-10" loading="lazy">',
        1
    )

    return new_html


def update_og_image(html, article_num):
    """Update og:image meta tag to point to local image."""
    local_url = f"https://{DOMAIN}/images/article-{article_num}.jpg"
    pattern = re.compile(r'(<meta\s+property="og:image"\s+content=")[^"]*(")', re.IGNORECASE)
    new_html, count = pattern.subn(r'\1' + local_url + r'\2', html, count=1)
    return new_html


def update_index_card(html, article_num):
    """Update background-image URL in index.html/articles.html card for this article."""
    local_url = f"images/article-{article_num}.jpg"
    # Find card by href
    card_pattern = re.compile(
        rf'(<a\s+href="article-{article_num}\.html"[^>]*>.*?style="background-image:url\()([^)]+)(\)[^>]*>)',
        re.DOTALL
    )
    new_html, count = card_pattern.subn(
        rf'\1{local_url}\3',
        html
    )
    return new_html, count


def main():
    daily_count = 0
    site_dir = ROOT / SITE_DIR
    generated = []
    skipped = []

    for num in MISSING_ARTICLES:
        article_path = site_dir / f"article-{num}.html"
        if not article_path.exists():
            print(f"SKIP: article-{num}.html not found")
            skipped.append((num, "file not found"))
            continue

        html = article_path.read_text(encoding="utf-8")

        # Skip if already has local image referenced
        if has_local_image(html, num):
            print(f"SKIP: article-{num} already has local image")
            skipped.append((num, "already has image"))
            continue

        title, description = extract_title_and_desc(html)
        print(f"\n{'='*60}")
        print(f"Processing article-{num}: {title[:60]}")

        # Generate image via Seedream
        image_url, daily_count = generate_and_verify_image(
            title,
            "Travel",
            description,
            SITE_DIR,
            num,
            daily_count
        )

        if not image_url:
            print(f"FAIL: article-{num} image generation failed")
            skipped.append((num, "generation failed"))
            continue

        print(f"  Image URL: {image_url}")

        # Update article HTML
        html = article_path.read_text(encoding="utf-8")  # re-read (function may not have modified it)
        html = replace_article_img(html, num, image_url)
        html = update_og_image(html, num)
        article_path.write_text(html, encoding="utf-8")
        print(f"  Updated: article-{num}.html with local image")

        # Update index.html card
        index_path = site_dir / "index.html"
        if index_path.exists():
            idx_html = index_path.read_text(encoding="utf-8")
            new_idx, count = update_index_card(idx_html, num)
            if count > 0:
                index_path.write_text(new_idx, encoding="utf-8")
                print(f"  Updated: index.html card for article-{num}")
            else:
                print(f"  Note: article-{num} card not found in index.html")

        # Update articles.html card
        articles_path = site_dir / "articles.html"
        if articles_path.exists():
            art_html = articles_path.read_text(encoding="utf-8")
            new_art, count = update_index_card(art_html, num)
            if count > 0:
                articles_path.write_text(new_art, encoding="utf-8")
                print(f"  Updated: articles.html card for article-{num}")
            else:
                print(f"  Note: article-{num} card not found in articles.html")

        generated.append((num, title))
        print(f"OK: article-{num}.jpg — {title[:50]}")

        # Sleep between generations (respect API rate limits)
        if num != MISSING_ARTICLES[-1]:
            time.sleep(3)

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Generated: {len(generated)} images")
    for num, title in generated:
        print(f"  OK: article-{num}.jpg — {title[:50]}")
    print(f"Skipped: {len(skipped)}")
    for num, reason in skipped:
        print(f"  SKIP: article-{num} — {reason}")
    print(f"Daily count used: {daily_count} / 50")

    return 0


if __name__ == "__main__":
    sys.exit(main())
