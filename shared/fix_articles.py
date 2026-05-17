"""Fix hardcoded Article 1/2/3 sidebar text + broken source.unsplash.com images across all sites.

Usage: py shared/fix_articles.py [--dry-run]
"""

import re
import sys
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Known-good Unsplash photo IDs per category
CATEGORY_PHOTOS = {
    "pets": [
        "1552053831-3a2e697e8eea",  # dog walker
        "1514888286974-6c03e2ca1dba",  # cat face
        "1548199973-03cce0bbc87b",  # dog with toy
        "1601758228041-f3b2795255f1",  # person with dog
        "1583337130417-3346a1be6dee",  # dog eating
        "1587300003388-59208cc962cb",  # vet with dog
        "1583511666407-5f2d7c5b5c46",  # overweight dog
        "1522069169874-c58ec4b76be5",  # aquarium fish
        "1606567595334-d39972c85dbe",  # budgie birds
        "1548199973-03cce0bbc87b",  # dog toy
    ],
    "health": [
        "1490645935967-10de6ba17071",  # healthy food
        "1512621776951-a57141f2eefd",  # salad
        "1505576399279-565b52d4ac71",  # vegetables
        "1498837167922-ddd27525d352",  # fruits
    ],
    "home": [
        "1484154218962-a197022b5858",  # home interior
        "1502672260266-1c1ef2d93688",  # houseplants
        "1558618666-83b2f28bea8f",  # gardening
        "1564013799919-ab600027f443",  # garden
    ],
    "finance": [
        "1554226655-67b1a2f2b5c5",  # money/coins
        "1579621970563-ebec7560ff3e",  # finance chart
        "1551839091-fb60f3b9d9a5",  # piggy bank
        "1450101499163-8feaec89286c",  # credit cards
    ],
    "tech": [
        "1518770660439-4636190af475",  # tech/phone
        "1531297484001-80022131f5a1",  # laptop
        "1496181133206-80ce9b88a853",  # laptop desk
        "1504639725590-34d0984388bd",  # electronics
    ],
    "travel": [
        "1488646953014-3064f3b6b7a0",  # travel/adventure
        "1476514525535-e2521697c7c2",  # mountain landscape
        "1506192209153-aff2f5e6cf42",  # beach
        "1502920917128-1aa500764cbd",  # cityscape
    ],
}

SITE_CATEGORY = {
    "sub-pets": "pets",
    "sub-healthy": "health",
    "sub-home": "home",
    "sub-finance": "finance",
    "sub-tech": "tech",
    "sub-travel": "travel",
}


def extract_title_from_file(filepath):
    """Extract h1 or title from an article HTML file."""
    try:
        html = filepath.read_text(encoding="utf-8")
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            return title[:80]
        m2 = re.search(r'<title>(.*?)</title>', html)
        if m2:
            return m2.group(1).strip()[:80]
    except Exception:
        pass
    return None


def fix_related_articles(html, site_dir):
    """Replace hardcoded 'Article 1/2/3' with real article titles."""
    lines = html.split('\n')
    fixed = []
    changes = 0

    for line in lines:
        # Match <p class="text-gray-700 text-sm mt-1">Article N</p>
        m = re.search(r'(<p class="text-gray-700 text-sm mt-1">)Article (\d+)(</p>)', line)
        if m:
            prefix = m.group(1)
            article_num = m.group(2)
            suffix = m.group(3)

            # Try to find the real article title
            linked_file = ROOT / site_dir / f"article-{article_num}.html"
            real_title = extract_title_from_file(linked_file)

            if real_title and real_title != f"Article {article_num}":
                line = line.replace(
                    f"{prefix}Article {article_num}{suffix}",
                    f"{prefix}{real_title}{suffix}"
                )
                changes += 1
                print(f"  Replaced 'Article {article_num}' → '{real_title[:60]}...'")

        fixed.append(line)

    return '\n'.join(fixed), changes


def fix_broken_images(html, site_dir):
    """Replace source.unsplash.com/800x400/?keyword with real Unsplash photos."""
    category = SITE_CATEGORY.get(site_dir, "pets")
    photos = CATEGORY_PHOTOS.get(category, CATEGORY_PHOTOS["pets"])
    changes = 0

    def replace_url(match):
        nonlocal changes
        keyword = match.group(1) if match.group(1) else "general"
        idx = hash(keyword) % len(photos)
        photo_id = photos[idx]
        new_url = f"https://images.unsplash.com/photo-{photo_id}?w=1200&h=630&fit=crop"
        changes += 1
        print(f"  Replaced source.unsplash.com/{keyword} → photo-{photo_id}")
        return new_url

    html = re.sub(
        r'https://source\.unsplash\.com/800x400/\?([a-zA-Z0-9\-]+)',
        replace_url,
        html
    )
    html = re.sub(
        r'https://source\.unsplash\.com/800x400/\?([^"\s]+)',
        replace_url,
        html
    )

    return html, changes


def fix_fake_unsplash_ids(html, site_dir):
    """Replace AI-generated fake Unsplash photo IDs (short numeric) with real ones."""
    category = SITE_CATEGORY.get(site_dir, "pets")
    photos = CATEGORY_PHOTOS.get(category, CATEGORY_PHOTOS["pets"])
    changes = 0
    used_indices = {}

    def replace_fake(match):
        nonlocal changes
        fake_id = match.group(1)
        # Only match short numeric IDs (1-6 digits) — real Unsplash IDs are 10-11 chars alphanumeric
        if len(fake_id) > 6:
            return match.group(0)
        width = match.group(2) or "1200"
        height = match.group(3) or "630"
        # Consistent replacement per fake ID
        idx = used_indices.get(fake_id, len(used_indices) % len(photos))
        used_indices[fake_id] = idx
        photo_id = photos[idx]
        new_url = f"https://images.unsplash.com/photo-{photo_id}?w={width}&h={height}&fit=crop"
        changes += 1
        print(f"  Replaced fake photo-{fake_id} → photo-{photo_id}")
        return new_url

    html = re.sub(
        r'https://images\.unsplash\.com/photo-(\d{1,6})\?w=(\d+)&h=(\d+)&fit=crop',
        replace_fake,
        html
    )
    return html, changes


def fix_emoji(html, site_dir):
    """Strip all emoji characters from HTML."""
    import re as re_mod
    emoji_re = re_mod.compile(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251'
        r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF'
        r'\U00002600-\U000026FF\U0000FE00-\U0000FE0F]'
    )
    new_html = emoji_re.sub('', html)
    changes = 1 if new_html != html else 0
    if changes:
        print(f"  Stripped emoji from {site_dir}")
    return new_html, changes


def fix_dead_links(html, site_dir):
    """Replace href='#' and href=\"#\" with href='index.html'."""
    count = html.count('href="#"') + html.count("href='#'")
    if count == 0:
        return html, 0
    html = html.replace('href="#"', 'href="index.html"')
    html = html.replace("href='#'", "href='index.html'")
    print(f"  Fixed {count} dead link(s) (href=\"#\")")
    return html, count


def fix_duplicate_h1(html, site_dir):
    """Ensure only one h1 tag — convert extras to h2."""
    h1_matches = list(re.finditer(r'<h1[\s>]', html))
    if len(h1_matches) <= 1:
        return html, 0

    changes = 0
    for m in h1_matches[1:]:
        html = html[:m.start()] + '<h2' + html[m.start() + 3:]
        changes += 1

    # Close tags
    extra_h1_close = list(re.finditer(r'</h1>', html))
    if len(extra_h1_close) > 1:
        for m in extra_h1_close[1:]:
            html = html[:m.start()] + '</h2>' + html[m.start() + 5:]

    if changes:
        print(f"  Fixed {changes} duplicate h1 tag(s) → h2")
    return html, changes


def fix_one_file(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8")
    total_changes = 0

    # Fix 1: Related Articles
    html, changes = fix_related_articles(html, site_dir)
    total_changes += changes

    # Fix 2: source.unsplash.com broken images
    html, changes = fix_broken_images(html, site_dir)
    total_changes += changes

    # Fix 3: Fake AI-generated Unsplash photo IDs (short numeric)
    html, changes = fix_fake_unsplash_ids(html, site_dir)
    total_changes += changes

    # Fix 4: Emoji
    html, changes = fix_emoji(html, site_dir)
    total_changes += changes

    # Fix 5: Dead links (href="#")
    html, changes = fix_dead_links(html, site_dir)
    total_changes += changes

    # Fix 6: Duplicate h1 tags
    html, changes = fix_duplicate_h1(html, site_dir)
    total_changes += changes

    if total_changes > 0:
        filepath.write_text(html, encoding="utf-8")
        print(f"  Fixed: {filepath.name} ({total_changes} changes)")
    return total_changes


def main():
    dry_run = "--dry-run" in sys.argv
    total_fixes = 0

    for site_dir, category in SITE_CATEGORY.items():
        site_path = ROOT / site_dir
        if not site_path.exists():
            continue

        articles = sorted(site_path.glob("article-*.html"))
        index_file = site_path / "index.html"
        files = articles + ([index_file] if index_file.exists() else [])
        if not files:
            continue

        print(f"\n{'='*60}")
        print(f"Site: {site_dir} ({len(files)} files)")
        print(f"{'='*60}")

        for filepath in files:
            changes = fix_one_file(filepath, site_dir)
            total_fixes += changes

    if dry_run:
        print(f"\n[DRY RUN] Would fix {total_fixes} issues across all sites")
    else:
        print(f"\nTotal fixes: {total_fixes} across all sites")


if __name__ == "__main__":
    main()
