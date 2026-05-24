"""
Content article cover image collector.
Scans content site directories for article-*.html files, extracts H1 titles,
searches DuckDuckGo for relevant images, downloads and compresses them,
then updates the HTML to reference the local image.

Usage:
    python shared/collect_content_images.py --site sub-travel
    python shared/collect_content_images.py --all
    python shared/collect_content_images.py --site sub-travel --limit 5
"""

import argparse
import io
import os
import re
import sys
import time
from pathlib import Path

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    from PIL import Image
except ImportError:
    Image = None


CONTENT_SITES = [
    'sub-healthy', 'sub-pets', 'sub-home', 'sub-finance',
    'sub-tech', 'sub-travel', 'entertainment',
    'rightsdaily', 'dailymedadvice', 'sub-auto',
]

# Unsplash fallback photo IDs (safe, generic stock photos)
UNSPLASH_FALLBACKS = [
    '1493976040374-85c8e12f0c0e',  # aerial landscape
    '1504672433874-a59e4c52cfa7',  # food
    '1491553895911-0055eca6402d',  # shoes on ground
    '1682685797229-b2930538da47',  # phone on table
    '1507525429019-5d8d02fedc4e',  # beach
    '1497366216548-37526070297c',  # office
    '1512918721392-37e3a7e2cbc3',  # building
    '1507003211169-0a1dd7228f2d',  # nature
    '1470079546665-1f4c0e5f9f0c',  # ocean
    '1469477566145-7b8c5e9e8b0c',  # sunset
    '1518173946687-9276550b5f8c',  # mountains
    '1526374965328-7f61d4dc18c5',  # city
    '1540208137-0b2f0f0b0f0b',  # landscape
    '1559128010-cd3e0c0b3c0b',  # forest
    '1564013799919-ab600027f5d1',  # house
    '1596394516099-6f5c7a5c5b5c',  # abstract
    '1504384308090-c894fdcc538d',  # workspace
    '1460925895917-afdab827c52f',  # laptop
    '1498050108023-c5249f4df085',  # tech
    '1522202176988-66273c2e55e5',  # people
]

BASE_DIR = Path(__file__).resolve().parent.parent


def h1_from_html(html: str) -> str:
    """Extract the first H1 text from HTML body."""
    # Try to find H1 after <body to avoid nav/brand H1
    body = html[html.find('<body'):]
    m = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.DOTALL)
    if m:
        # Strip HTML tags within H1
        title = re.sub(r'<[^>]+>', '', m.group(1))
        return title.strip()
    return ''


def article_number(filename: str) -> str:
    """Extract the numeric part from article-N.html."""
    m = re.search(r'article-(\d+)', filename)
    return m.group(1) if m else ''


def search_images(query: str, max_results: int = 5):
    """Search DuckDuckGo for images. Returns list of URLs."""
    if DDGS is None:
        print("  WARN: ddgs not installed, skipping search")
        return []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=max_results))
            return [r['image'] for r in results if r.get('image')]
    except Exception as e:
        print(f"  WARN: DDGS search failed: {e}")
        return []


def download_image(url: str, timeout: int = 15) -> bytes | None:
    """Download image bytes from URL."""
    import urllib.request
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                )
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if len(data) < 1024 * 100:  # < 100KB = too small
                return None
            return data
    except Exception:
        return None


def compress_image(data: bytes, max_width: int = 1200, quality: int = 85, max_size: int = 200 * 1024) -> bytes:
    """Resize and compress JPEG image to fit constraints."""
    if Image is None:
        # No Pillow, return original (limited fallback)
        return data

    img = Image.open(io.BytesIO(data))
    # Convert to RGB if needed
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Resize maintaining aspect ratio
    w, h = img.size
    if w > max_width:
        ratio = max_width / w
        new_w = max_width
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    # Try to compress within max_size
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    result = buf.getvalue()

    # If still too large, reduce quality iteratively
    while len(result) > max_size and quality > 30:
        quality -= 10
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        result = buf.getvalue()

    return result


def get_fallback_url(fallback_idx: int) -> str:
    """Get a deterministic Unsplash fallback URL."""
    idx = fallback_idx % len(UNSPLASH_FALLBACKS)
    return (
        f'https://images.unsplash.com/photo-{UNSPLASH_FALLBACKS[idx]}'
        '?w=1200&h=675&fit=crop'
    )


def update_article_html(html: str, img_path: str, h1_text: str) -> str:
    """Update article HTML: replace or insert hero image after header."""
    # First, try to find an existing hero <img> tag near the article header
    # (within the first 1000 chars of the article body after </nav>)
    body_start = html.find('</nav>')
    if body_start == -1:
        body_start = html.find('<body')
    search_region = html[body_start:body_start + 2000] if body_start >= 0 else html[:2000]

    img_tag_match = re.search(r'<img[^>]+src="([^"]*article[^"]*)"[^>]*>', search_region)
    if not img_tag_match:
        img_tag_match = re.search(r'<img[^>]+src="images/article-[^"]*"[^>]*>', search_region)
    if not img_tag_match:
        img_tag_match = re.search(r'<img[^>]+src="[^"]*unsplash[^"]*"[^>]*>', search_region)

    if img_tag_match:
        # Replace existing hero image src
        full_tag = img_tag_match.group(0)
        new_tag = re.sub(
            r'src="[^"]*"',
            f'src="{img_path}"',
            full_tag
        )
        html = html.replace(full_tag, new_tag, 1)
    else:
        # Insert a new hero image after the author/byline block
        # Strategy: find h1, then find the next </div> after author section
        h1_match = re.search(r'<h1[^>]*>.*?</h1>', html[body_start:], re.DOTALL)
        if h1_match:
            h1_end = body_start + h1_match.end()
            # Look for </header> first
            header_close = html.find('</header>', h1_end)
            if header_close != -1 and header_close - h1_end < 500:
                # Insert before </header>
                img_html = (
                    f'\n            <img\n        src="{img_path}"\n        '
                    f'alt="{h1_text} - article hero image"\n        '
                    f'class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"\n        '
                    f'loading="lazy"\n        width="800"\n        height="400">'
                )
                html = html[:header_close] + img_html + '\n            ' + html[header_close:]
            else:
                # Find the author/byline closing div
                after_h1 = html[h1_end:]
                # Track nested divs to find the right closing tag
                depth = 0
                insert_pos = -1
                for m in re.finditer(r'</?div[^>]*>', after_h1):
                    tag = m.group()
                    if tag.startswith('</div'):
                        if depth == 0:
                            insert_pos = h1_end + m.end()
                            break
                        depth -= 1
                    else:
                        depth += 1

                if insert_pos > 0:
                    img_html = (
                        f'\n\n                <img\n        src="{img_path}"\n        '
                        f'alt="{h1_text} - article hero image"\n        '
                        f'class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"\n        '
                        f'loading="lazy"\n        width="800"\n        height="400">\n'
                    )
                    html = html[:insert_pos] + img_html + html[insert_pos:]
                else:
                    # Last resort: insert after </header> if exists, otherwise after <h1> block
                    header_close = html.find('</header>', body_start)
                    if header_close != -1:
                        img_html = (
                            f'\n            <img\n        src="{img_path}"\n        '
                            f'alt="{h1_text} - article hero image"\n        '
                            f'class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"\n        '
                            f'loading="lazy"\n        width="800"\n        height="400">'
                        )
                        html = html[:header_close] + img_html + '\n            ' + html[header_close:]
                    else:
                        # Insert after the h1 closing tag
                        insert_pos = h1_end
                        img_html = (
                            f'\n\n                <img\n        src="{img_path}"\n        '
                            f'alt="{h1_text} - article hero image"\n        '
                            f'class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"\n        '
                            f'loading="lazy"\n        width="800"\n        height="400">\n'
                        )
                        html = html[:insert_pos] + img_html + html[insert_pos:]
        else:
            # No H1 found, insert after <main
            main_match = re.search(r'<main[^>]*>', html)
            if main_match:
                insert_pos = main_match.end()
                img_html = (
                    f'\n            <img\n        src="{img_path}"\n        '
                    f'alt="{h1_text} - article hero image"\n        '
                    f'class="w-full h-64 md:h-80 object-cover rounded-xl mb-8"\n        '
                    f'loading="lazy"\n        width="800"\n        height="400">\n'
                )
                html = html[:insert_pos] + img_html + html[insert_pos:]

    return html


def update_index_html(site_dir: Path, article_num: str, img_path: str):
    """Update the article card's background-image in index.html."""
    index_file = site_dir / 'index.html'
    if not index_file.exists():
        return

    html = index_file.read_text(encoding='utf-8')

    # Find the article card: <a href="article-N" or similar with class article-card
    # Pattern: href="article-N.html" ... style="background-image:url(...)
    old_pattern = re.compile(
        rf'(href="article-{article_num}\.html"[^>]*>.*?'
        rf'style="background-image:url\()([^)]*)(\)")',
        re.DOTALL
    )
    m = old_pattern.search(html)
    if m:
        old_url = m.group(2)
        # Only replace if it's not already pointing to our local image
        if 'images/article-' not in old_url:
            new_html = html.replace(
                f'background-image:url({old_url})',
                f'background-image:url({img_path})',
            )
            index_file.write_text(new_html, encoding='utf-8')
            print(f'      -> updated index.html card for article-{article_num}')
    else:
        # Try simpler pattern (just href match)
        old_pattern2 = re.compile(
            rf'(<a[^>]*href="article-{article_num}\.html"[^>]*>.*?background-image:url\()([^)]*)(\))',
            re.DOTALL
        )
        m2 = old_pattern2.search(html)
        if m2:
            old_url = m2.group(2)
            if 'images/article-' not in old_url:
                new_html = html.replace(
                    f'background-image:url({old_url})',
                    f'background-image:url({img_path})',
                )
                index_file.write_text(new_html, encoding='utf-8')
                print(f'      -> updated index.html card for article-{article_num}')


def process_site(site_name: str, limit: int = 0, force: bool = False):
    """Process all articles in a site directory."""
    site_dir = BASE_DIR / site_name
    if not site_dir.is_dir():
        print(f"  SKIP: {site_name} directory not found")
        return 0

    images_dir = site_dir / 'images'
    images_dir.mkdir(exist_ok=True)

    # Find all article files, sorted
    articles = sorted(site_dir.glob('article-*.html'))
    if not articles:
        print(f"  SKIP: {site_name} has no article files")
        return 0

    # Filter to those missing images (or force re-download)
    to_process = []
    for a in articles:
        num = article_number(a.name)
        if not num:
            continue
        img_path = images_dir / f'article-{num}.jpg'
        if not img_path.exists() or force:
            to_process.append((a, num, img_path))

    if limit > 0:
        to_process = to_process[:limit]

    total = len(to_process)
    if total == 0:
        print(f"  {site_name}: all {len(articles)} articles have images")
    else:
        print(f"\n  {site_name}: {total} images needed ({len(articles)} total articles)")

    ok_count = 0
    fallback_idx = 0
    for i, (article_file, num, img_path) in enumerate(to_process, 1):
        html = article_file.read_text(encoding='utf-8')
        title = h1_from_html(html)
        if not title:
            print(f"  [{i}/{total}] {article_file.name}: SKIP (no H1 found)")
            continue

        print(f"  [{i}/{total}] {article_file.name}: \"{title[:50]}...\"", end='', flush=True)

        # Build search query
        site_lower = site_name.lower()
        if 'travel' in site_lower:
            kw = 'travel'
        elif 'health' in site_lower or 'dailymed' in site_lower:
            kw = 'healthy food lifestyle'
        elif 'pets' in site_lower:
            kw = 'pet animal'
        elif 'home' in site_lower:
            kw = 'home garden'
        elif 'finance' in site_lower:
            kw = 'finance business'
        elif 'tech' in site_lower:
            kw = 'technology'
        elif 'entertainment' in site_lower:
            kw = 'entertainment movie'
        elif 'auto' in site_lower:
            kw = 'car automotive vehicle'
        elif 'rightsdaily' in site_lower:
            kw = 'law justice'
        else:
            kw = 'stock photo'

        query = f'{title} {kw}'

        # Try DDGS search
        img_urls = search_images(query)

        # Also try a shorter query if no results
        if not img_urls:
            short_title = title.split(':')[0].split('—')[0].strip()[:40]
            query2 = f'{short_title} {kw}'
            img_urls = search_images(query2, max_results=5)

        downloaded = False
        for url in img_urls:
            data = download_image(url)
            if data:
                compressed = compress_image(data)
                img_path.write_bytes(compressed)
                size_kb = len(compressed) // 1024
                print(f" OK ({size_kb}KB)")
                downloaded = True
                ok_count += 1
                break
            time.sleep(0.5)  # Small delay between download attempts

        if not downloaded:
            # Fallback: use Unsplash
            fallback_url = get_fallback_url(int(num))
            data = download_image(fallback_url)
            if data:
                compressed = compress_image(data)
                img_path.write_bytes(compressed)
                size_kb = len(compressed) // 1024
                print(f" FALLBACK (Unsplash, {size_kb}KB)")
                downloaded = True
                ok_count += 1
            else:
                print(" FAIL (no image found)")
                fallback_idx += 1
                continue

        if downloaded:
            # Update article HTML
            relative_img = f'images/article-{num}.jpg'
            new_html = update_article_html(html, relative_img, title)
            if new_html != html:
                article_file.write_text(new_html, encoding='utf-8')

            # Update index.html card
            update_index_html(site_dir, num, relative_img)

            # Update og:image meta tag if still pointing to external
            og_pattern = re.compile(
                r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
                re.IGNORECASE
            )
            if og_pattern.search(html):
                og_url = f'https://{site_name}.jycsd.com/images/article-{num}.jpg'
                new_html2 = og_pattern.sub(
                    rf'\g<1>{og_url}\g<2>',
                    html if not downloaded else new_html
                )
                if new_html2 != html and new_html2 != new_html:
                    article_file.write_text(new_html2, encoding='utf-8')

        # Delay between articles to avoid rate limiting
        time.sleep(2)

    # Sync index.html cards for ALL articles with existing images
    index_file = site_dir / 'index.html'
    if index_file.exists():
        for a in articles:
            num = article_number(a.name)
            if not num:
                continue
            img_path = images_dir / f'article-{num}.jpg'
            if img_path.exists():
                update_index_html(site_dir, num, f'images/article-{num}.jpg')

    return ok_count


def main():
    parser = argparse.ArgumentParser(description='Collect article cover images')
    parser.add_argument('--site', type=str, help='Site name to process')
    parser.add_argument('--all', action='store_true', help='Process all content sites')
    parser.add_argument('--limit', type=int, default=0, help='Max articles per site')
    parser.add_argument('--force', action='store_true', help='Re-download existing images')
    args = parser.parse_args()

    if args.site:
        sites = [args.site]
    elif args.all:
        sites = CONTENT_SITES
    else:
        parser.print_help()
        sys.exit(1)

    total_ok = 0
    for site in sites:
        ok = process_site(site, limit=args.limit, force=args.force)
        total_ok += ok

    print(f"\nDone. {total_ok} images collected.")


if __name__ == '__main__':
    main()
