#!/usr/bin/env python3
"""Download Unsplash images from clothing-site HTML files and update references to local paths."""

import os
import re
import requests
from collections import defaultdict, OrderedDict

BASE_DIR = r"d:\AI网站文件夹\clothing-site"
IMAGE_DIR = os.path.join(BASE_DIR, "images")


def get_file_key(html_file):
    """Generate a unique key for naming images based on the HTML file path."""
    rel_path = os.path.relpath(html_file, BASE_DIR)
    filename = os.path.basename(html_file)
    stem = os.path.splitext(filename)[0]
    dirpath = os.path.dirname(rel_path)

    if stem == "index":
        # Use the parent directory name as the key
        if not dirpath or dirpath == ".":
            return "home"
        # Flatten the last segment of the directory path
        parts = dirpath.replace("\\", "/").split("/")
        return parts[-1]
    return stem


def main():
    # 1. Scan all HTML files, excluding images directory
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        rel = os.path.relpath(root, BASE_DIR).replace("\\", "/")
        if rel.startswith("images") or rel.startswith("__pycache__"):
            continue
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    html_files.sort()
    print(f"Found {len(html_files)} HTML files")

    # 2. Extract all Unsplash URLs
    # unique_photos: photo_base_url -> (first_full_url, {set of referencing files})
    unique_photos = OrderedDict()
    file_url_map = OrderedDict()  # html_file -> [(base_url, full_url), ...]

    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()

        urls = re.findall(
            r'https://images\.unsplash\.com/photo-[a-zA-Z0-9-]+(?:\?[^"\' \t>]*)?',
            content,
        )

        entries = []
        for url in urls:
            base_url = url.split("?")[0]
            entries.append((base_url, url))
            if base_url not in unique_photos:
                unique_photos[base_url] = (url, set())
            unique_photos[base_url][1].add(html_file)

        if entries:
            file_url_map[html_file] = entries

    unique_count = len(unique_photos)
    total_occurrences = sum(len(v) for v in file_url_map.values())
    print(f"Found {unique_count} unique Unsplash photos in {total_occurrences} total references")

    # 3. Assign local filenames
    # Strategy: each file gets sequential naming (_hero, _1, _2, ...)
    # for the unique photos it references, BUT photos already named by an
    # earlier-file keep their existing name.
    photo_to_filename = {}  # base_url -> local filename

    for html_file, entries in file_url_map.items():
        key = get_file_key(html_file)
        local_idx = 0
        for base_url, _ in entries:
            if base_url in photo_to_filename:
                continue
            if local_idx == 0:
                photo_to_filename[base_url] = f"{key}_hero.jpg"
            else:
                photo_to_filename[base_url] = f"{key}_{local_idx}.jpg"
            local_idx += 1

    # 4. Download images
    os.makedirs(IMAGE_DIR, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}

    downloaded = 0
    skipped = 0
    failed = 0

    print(f"\nDownloading {unique_count} images to {IMAGE_DIR} ...")
    for base_url, (first_full_url, ref_files) in unique_photos.items():
        local_name = photo_to_filename[base_url]
        local_path = os.path.join(IMAGE_DIR, local_name)

        if os.path.exists(local_path):
            skipped += 1
            continue

        try:
            resp = requests.get(first_full_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                print(f"  [OK]  {local_name}  ({len(resp.content):,} bytes)")
                downloaded += 1
            else:
                print(f"  [FAIL] {local_name}  HTTP {resp.status_code}")
                failed += 1
        except requests.exceptions.RequestException as e:
            print(f"  [FAIL] {local_name}  {e}")
            failed += 1

    print(f"\nDownload summary: {downloaded} OK, {skipped} skipped, {failed} failed")

    # 5. Update HTML files — replace all Unsplash URLs with local /images/ paths
    print(f"\nUpdating HTML files ...")
    updated_count = 0
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        original = content

        for base_url, (first_full_url, _) in unique_photos.items():
            local_name = photo_to_filename[base_url]
            local_path = f"/images/{local_name}"
            # Replace any variant of this photo URL (with or without query params)
            pattern = re.escape(base_url) + r'(?:\?[^"\' \t>]*)?'
            content = re.sub(pattern, local_path, content)

        if content != original:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(content)
            updated_count += 1

    print(f"Updated {updated_count} of {len(html_files)} HTML files")

    # 6. Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  HTML files scanned:   {len(html_files)}")
    print(f"  Unique photos found:  {unique_count}")
    print(f"  Downloaded:           {downloaded}")
    print(f"  Skipped (exist):      {skipped}")
    print(f"  Failed:               {failed}")
    print(f"  HTML files updated:   {updated_count}")

    # Verification hint
    print("\nRun verification:")
    print(f'  ls "{IMAGE_DIR}"/*.jpg 2>/dev/null | wc -l')
    print(f'  grep -r "images.unsplash.com" --include="*.html" "{BASE_DIR}" | wc -l')
    print(f'  grep -r "/images/" --include="*.html" "{BASE_DIR}" | wc -l')


if __name__ == "__main__":
    main()
