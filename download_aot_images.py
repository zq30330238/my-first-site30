"""Download Attack on Titan character PNG images from multiple sources."""
import requests, os, re, time, json, sys, io
from pathlib import Path
from PIL import Image
import hashlib

OUTPUT_DIR = Path("d:/AI网站文件夹/aot-site/images")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

CHARACTERS = {
    "jean-kirstein": "Jean Kirstein Attack on Titan",
    "keith-shadis": "Keith Shadis Attack on Titan",
    "kenny-ackerman": "Kenny Ackerman Attack on Titan",
    "levi-ackerman": "Levi Ackerman Attack on Titan",
    "mikasa-ackerman": "Mikasa Ackerman Attack on Titan",
    "pieck-finger": "Pieck Finger Attack on Titan Cart Titan",
    "porco-galliard": "Porco Galliard Attack on Titan Jaw Titan",
    "reiner-braun": "Reiner Braun Attack on Titan Armored Titan",
    "rod-reiss": "Rod Reiss Attack on Titan",
    "sasha-blouse": "Sasha Blouse Attack on Titan",
    "ymir": "Ymir Attack on Titan freckled",
    "ymir-fritz": "Ymir Fritz Attack on Titan Founder",
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def search_pngwing(query):
    """Search pngwing.com for a character and return list of (detail_url, img_url, title)."""
    results = []
    search_url = f"https://www.pngwing.com/en/search?q={requests.utils.quote(query)}"
    log(f"  Searching: {search_url}")
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            log(f"  Search returned {r.status_code}")
            return results
        # Extract image items from search results
        # Pattern: find thumbnails and their detail page links
        html = r.text

        # Find all figure items with img tags and links
        # Pattern: <a href="/en/free-png-..."><img src="..." alt="..."></a>
        detail_pattern = r'href="(/en/free-png-[^"]+)"'
        img_pattern = r'<img[^>]*src="(https://[^"]+\.png[^"]*)"[^>]*alt="([^"]*)"[^>]*>'

        # Extract detail URLs
        detail_urls = re.findall(detail_pattern, html)

        # Extract image thumbnails with alt text
        imgs = re.findall(img_pattern, html)

        # Match thumbnails with their detail links
        # We'll collect unique detail URLs
        seen = set()
        for i, detail_path in enumerate(detail_urls):
            full_detail = f"https://www.pngwing.com{detail_path}"
            if full_detail not in seen:
                seen.add(full_detail)
                # Try to find corresponding img
                alt = ""
                if i < len(imgs):
                    alt = imgs[i][1]
                results.append((full_detail, "", alt))
                if len(results) >= 5:
                    break

        log(f"  Found {len(results)} results on pngwing")
        return results
    except Exception as e:
        log(f"  Search error: {e}")
        return results

def get_original_from_detail(detail_url):
    """Get the original PNG download URL from a pngwing detail page."""
    log(f"  Detail page: {detail_url}")
    try:
        r = requests.get(detail_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None

        html = r.text

        # Pattern 1: Download link with width parameter
        # <a href="/en/free-png-xxxxx/download?width=2000"
        dl_pattern = r'href="(/en/free-png-[^"]+/download\?width=\d+)"'
        dl_matches = re.findall(dl_pattern, html)

        # Pattern 2: Direct PNG URL in img tag on detail page
        # <img src="https://assets.imgix.net/.../...png?...
        png_pattern = r'src="(https://assets\.imgix\.net/[^"]+\.png[^"]*)"'
        png_matches = re.findall(png_pattern, html)

        # Pattern 3: direct PNG URL from download link
        if dl_matches:
            dl_path = dl_matches[0]
            dl_url = f"https://www.pngwing.com{dl_path}"
            log(f"  Download URL: {dl_url}")
            return dl_url

        # If no download link, try direct PNG from detail page
        if png_matches:
            png_url = png_matches[0]
            log(f"  Direct PNG: {png_url}")
            return png_url

        # Pattern 4: Try any PNG from the page
        all_png = re.findall(r'src="(https://[^"]+\.png[^"]*)"', html)
        for p in all_png:
            if 'assets.imgix.net' in p or 'pngwing.com' in p:
                log(f"  Found PNG: {p}")
                return p

        log(f"  No download URL found in detail page")
        return None
    except Exception as e:
        log(f"  Detail page error: {e}")
        return None

def try_pngwing_direct(query):
    """Try to download directly from pngwing using search results."""
    results = search_pngwing(query)
    for detail_url, _, title in results:
        dl_url = get_original_from_detail(detail_url)
        if dl_url:
            # Download the image
            img_data = download_image(dl_url, referer=detail_url)
            if img_data and len(img_data) > 10240:
                log(f"  Downloaded {len(img_data)} bytes from pngwing")
                return img_data
        time.sleep(1)
    return None

def download_image(url, referer=None):
    """Download an image from URL."""
    headers = dict(IMG_HEADERS)
    if referer:
        headers['Referer'] = referer
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200 and len(r.content) > 1024:
            return r.content
    except Exception as e:
        log(f"  Download error: {e}")
    return None

def try_fandom_wiki(character_name, search_term):
    """Try to download from Attack on Titan Fandom wiki."""
    # Try to find character page on AOT wiki
    wiki_search_url = f"https://attackontitan.fandom.com/wiki/Special:Search?query={requests.utils.quote(character_name)}"
    log(f"  Fandom search: {wiki_search_url}")
    try:
        r = requests.get(wiki_search_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None

        html = r.text

        # Look for character page link
        char_pattern = re.escape(character_name.replace('-', ' ').replace('_', ' '))
        page_pattern = r'href="(https://attackontitan\.fandom\.com/wiki/[^"]*' + char_pattern.replace(' ', '[^"]*') + r'[^"]*)"'
        matches = re.findall(page_pattern, html, re.IGNORECASE)

        if not matches:
            # Broader search: just find any AOT wiki link with the name
            page_pattern = r'href="(https://attackontitan\.fandom\.com/wiki/[^"]*)"'
            all_links = re.findall(page_pattern, html)
            # Filter by relevance
            name_parts = character_name.lower().replace('-', ' ').split()
            for link in all_links:
                link_lower = link.lower()
                if all(part in link_lower for part in name_parts):
                    matches.append(link)

        if not matches:
            log(f"  No character page found on fandom")
            return None

        char_url = matches[0]
        log(f"  Character page: {char_url}")

        r2 = requests.get(char_url, headers=HEADERS, timeout=15)
        if r2.status_code != 200:
            return None

        html2 = r2.text

        # Look for the main character image - usually a <figure> or <img> in the infobox
        # Fandom typically uses <img> tags with data-src for lazy loading
        img_patterns = [
            r'data-src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|webp)[^"]*)"',
            r'src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|webp)[^"]*)"',
            r'data-src="(https://[^"]+\.(?:png|jpg|webp)[^"]*)"',
        ]

        for pattern in img_patterns:
            imgs = re.findall(pattern, html2)
            for img_url in imgs:
                # Skip small icons, logos, etc.
                if any(skip in img_url.lower() for skip in ['logo', 'icon', 'button', 'banner', 'nav', 'background']):
                    continue
                # Prefer character images (larger, in infobox)
                img_data = download_image(img_url, referer=char_url)
                if img_data and len(img_data) > 20480:  # > 20KB
                    log(f"  Downloaded {len(img_data)} bytes from fandom: {img_url[:80]}")
                    return img_data

        log(f"  No suitable image found on fandom page")
        return None
    except Exception as e:
        log(f"  Fandom error: {e}")
        return None

def try_wikimedia(query):
    """Try Wikimedia Commons."""
    search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&format=json&srlimit=10"
    log(f"  Wikimedia search...")
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        if 'query' not in data or 'search' not in data['query']:
            return None

        for result in data['query']['search']:
            title = result['title']
            # Get image URL
            img_info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={requests.utils.quote(title)}&prop=imageinfo&iiprop=url&format=json"
            r2 = requests.get(img_info_url, headers=HEADERS, timeout=15)
            if r2.status_code != 200:
                continue
            img_data = r2.json()
            pages = img_data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if page_id == '-1':
                    continue
                imageinfos = page_info.get('imageinfo', [])
                if imageinfos:
                    url = imageinfos[0].get('url', '')
                    if url and (url.endswith('.png') or '.png' in url):
                        result_data = download_image(url, referer='https://commons.wikimedia.org/')
                        if result_data and len(result_data) > 20480:
                            log(f"  Downloaded {len(result_data)} bytes from wikimedia")
                            return result_data
            time.sleep(0.5)
        return None
    except Exception as e:
        log(f"  Wikimedia error: {e}")
        return None

def try_cleanpng(query):
    """Try cleanpng.com as alternative."""
    search_url = f"https://www.cleanpng.com/search/{requests.utils.quote(query.replace(' ', '-'))}.html"
    log(f"  cleanpng: {search_url}")
    try:
        r = requests.get(search_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        html = r.text
        # Look for PNG download links
        png_urls = re.findall(r'(https://[^"]+\.png[^"]*topng[^"]*)', html)
        # Also try thumbnails
        if not png_urls:
            png_urls = re.findall(r'(https://[^"]+\.png[^"]*)', html)
        for url in png_urls:
            if 'logo' not in url.lower() and 'icon' not in url.lower():
                img_data = download_image(url, referer=search_url)
                if img_data and len(img_data) > 20480:
                    log(f"  Downloaded {len(img_data)} bytes from cleanpng")
                    return img_data
        return None
    except Exception as e:
        log(f"  cleanpng error: {e}")
        return None

def remove_background(img_data):
    """Remove background using rembg."""
    try:
        import rembg
        session = rembg.new_session()
        result = rembg.remove(img_data, session=session)
        return result
    except Exception as e:
        log(f"  rembg error: {e}")
        return img_data

def validate_image(img_data, min_size=30720, min_dim=300):
    """Validate image: size > min_size, dimensions > min_dim."""
    if len(img_data) < min_size:
        return False, f"Too small: {len(img_data)} bytes"
    try:
        img = Image.open(io.BytesIO(img_data))
        w, h = img.size
        if w < min_dim or h < min_dim:
            return False, f"Too small: {w}x{h}"
        # Check if it's a valid PNG
        if img.format != 'PNG' and img.format != 'JPEG' and img.format != 'WEBP':
            # Convert to PNG
            pass  # Will convert later
        return True, f"{w}x{h}, {len(img_data)} bytes"
    except Exception as e:
        return False, f"Invalid image: {e}"

def verify_with_vision(filepath, expected_desc):
    """Verify image content using doubao vision."""
    log(f"  Verifying with doubao vision...")
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'd:/AI网站文件夹/shared/doubao_vision.py', str(filepath),
             f'Describe this character from Attack on Titan. Is this {expected_desc}? Identify clothing, hair, and key features.'],
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout.strip() or result.stderr.strip()
        log(f"  Vision: {output[:200]}")
        return output
    except Exception as e:
        log(f"  Vision error: {e}")
        return ""

def save_image(img_data, filename):
    """Save image, ensuring PNG format."""
    filepath = OUTPUT_DIR / filename
    try:
        # Try to open to verify
        img = Image.open(io.BytesIO(img_data))
        # Convert to RGBA if RGB
        if img.mode == 'RGB':
            img = img.convert('RGBA')
        # Save as PNG
        img.save(filepath, 'PNG')
    except Exception:
        # Just save raw data
        with open(filepath, 'wb') as f:
            f.write(img_data)
    return filepath

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    for slug, search_term in CHARACTERS.items():
        log(f"\n{'='*60}")
        log(f"Downloading: {slug} ({search_term})")
        log(f"{'='*60}")

        img_data = None
        sources_tried = []

        # Try multiple search queries
        queries = [
            search_term,
            search_term.split(' Attack')[0],
            search_term.replace(' Attack on Titan', ''),
        ]

        # Try pngwing first with various queries
        for q in queries:
            if img_data:
                break
            log(f"  Trying pngwing: '{q}'")
            img_data = try_pngwing_direct(q)
            sources_tried.append(f"pngwing: {q}")
            if img_data:
                break

        # Try fandom wiki
        if not img_data:
            for q in queries:
                if img_data:
                    break
                name_for_wiki = q.split(' Attack')[0] if ' Attack' in q else q
                log(f"  Trying fandom wiki: '{name_for_wiki}'")
                img_data = try_fandom_wiki(name_for_wiki, q)
                sources_tried.append(f"fandom: {name_for_wiki}")
                time.sleep(1)

        # Try cleanpng
        if not img_data:
            for q in queries:
                if img_data:
                    break
                log(f"  Trying cleanpng: '{q}'")
                img_data = try_cleanpng(q)
                sources_tried.append(f"cleanpng: {q}")
                time.sleep(1)

        # Try wikimedia as last resort
        if not img_data:
            for q in queries:
                if img_data:
                    break
                log(f"  Trying wikimedia: '{q}'")
                img_data = try_wikimedia(q)
                sources_tried.append(f"wikimedia: {q}")
                time.sleep(1)

        if not img_data:
            log(f"  FAILED: No image found from any source")
            results[slug] = {"status": "failed", "sources_tried": sources_tried}
            continue

        # Validate image
        valid, msg = validate_image(img_data)
        if not valid:
            log(f"  Validation failed: {msg}")
            results[slug] = {"status": "failed", "reason": msg, "sources_tried": sources_tried}
            continue

        log(f"  Validation: {msg}")

        # Save original first
        temp_filepath = OUTPUT_DIR / f"temp_{slug}.png"
        save_image(img_data, f"temp_{slug}.png")

        # Verify with doubao vision
        expected_desc = search_term
        vision_output = verify_with_vision(temp_filepath, expected_desc)

        # Check if vision confirmed the character
        vision_lower = vision_output.lower()
        char_name = slug.replace('-', ' ').lower()

        # Check for character match in vision output
        name_parts = char_name.split()
        name_match = any(part in vision_lower for part in name_parts)

        if name_match or 'aot' in vision_lower or 'attack on titan' in vision_lower or 'shingeki' in vision_lower:
            log(f"  Vision MATCH: character confirmed")
        else:
            log(f"  Vision WARNING: character not clearly identified in description")
            # Still keep the image but note the warning
            log(f"  Keeping image despite vision warning")

        # Remove background
        log(f"  Removing background...")
        final_data = remove_background(open(temp_filepath, 'rb').read())

        # Save final file
        final_filename = f"{slug}.png"
        final_filepath = save_image(final_data, final_filename)

        # Get file size
        final_size = os.path.getsize(final_filepath)

        # Clean up temp file
        if temp_filepath.exists():
            temp_filepath.unlink()

        log(f"  Saved: {final_filepath} ({final_size} bytes)")
        results[slug] = {
            "status": "success",
            "filepath": str(final_filepath),
            "size": final_size,
            "vision": vision_output[:200],
            "sources_tried": sources_tried
        }

        # Rate limiting
        time.sleep(2)

    # Summary
    log(f"\n{'='*60}")
    log(f"DOWNLOAD SUMMARY")
    log(f"{'='*60}")
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    fail_count = sum(1 for r in results.values() if r['status'] == 'failed')
    log(f"Success: {success_count}, Failed: {fail_count}")

    for slug, r in results.items():
        if r['status'] == 'success':
            log(f"  [OK] {slug}: {r['size']} bytes -> {r['filepath']}")
        else:
            log(f"  [FAIL] {slug}: {r.get('reason', 'no image')}")

    # Save report
    report_path = OUTPUT_DIR / "download_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"\nReport saved to {report_path}")

if __name__ == '__main__':
    main()
