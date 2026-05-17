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
        # Try to pick a photo based on keyword hash for consistency
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


def fix_one_file(filepath, site_dir):
    html = filepath.read_text(encoding="utf-8")
    total_changes = 0

    # Fix 1: Related Articles
    html, changes = fix_related_articles(html, site_dir)
    total_changes += changes

    # Fix 2: Broken images
    html, changes = fix_broken_images(html, site_dir)
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
        if not articles:
            continue

        print(f"\n{'='*60}")
        print(f"Site: {site_dir} ({len(articles)} articles)")
        print(f"{'='*60}")

        for article_path in articles:
            changes = fix_one_file(article_path, site_dir)
            total_fixes += changes

    if dry_run:
        print(f"\n[DRY RUN] Would fix {total_fixes} issues across all sites")
    else:
        print(f"\nTotal fixes: {total_fixes} across all sites")


if __name__ == "__main__":
    main()
