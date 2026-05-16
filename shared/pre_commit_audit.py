"""Pre-commit audit: check ad slots, placeholders, SEO basics before push."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel"]
VALID_SLOTS = {"9112825459", "4397738132", "9739511410"}
BAD_SLOTS = {"6452093175", "7928829977", "9405566373"}
REQUIRED_META = ["google-adsense-account", "description", "og:title", "og:description"]
MIN_WORDS = 800

errors = []
warnings = []

def check_article(filepath):
    html = filepath.read_text(encoding="utf-8", errors="ignore")
    name = f"{filepath.parent.name}/{filepath.name}"

    # 1. Ad slots check
    slots = re.findall(r'data-ad-slot="(\d+)"', html)
    bad = [s for s in slots if s in BAD_SLOTS]
    if bad:
        errors.append(f"{name}: BAD ad slots found: {bad}")
    slot_count = len(slots)
    if slot_count != 3:
        errors.append(f"{name}: expected 3 ad slots, found {slot_count}")

    # 2. No ad-container placeholders
    containers = len(re.findall(r'class="ad-container', html))
    if containers > 0:
        errors.append(f"{name}: {containers} ad-container placeholders remain")

    # 3. Ad block integrity: each adsbygoogle ins must have matching close
    ad_ins_open = len(re.findall(r'<ins class="adsbygoogle"[^>]*>', html))
    ad_ins_close = len(re.findall(r'</ins>', html))
    if ad_ins_open != ad_ins_close:
        errors.append(f"{name}: mismatched <ins> tags ({ad_ins_open} open vs {ad_ins_close} close)")
    ad_push = len(re.findall(r'\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\)', html))
    if ad_push != slot_count:
        errors.append(f"{name}: {slot_count} ad units but {ad_push} push scripts")

    # 4. Required meta tags
    meta_checks = {
        "google-adsense-account": 'google-adsense-account',
        "description": 'name="description"',
        "og:title": 'property="og:title"',
        "og:description": 'property="og:description"',
    }
    for meta, pattern in meta_checks.items():
        if pattern not in html:
            errors.append(f"{name}: missing {meta}")

    # 5. Auto Ads script
    if 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' not in html:
        errors.append(f"{name}: missing Auto Ads script")

    # 6. Canonical URL
    if 'rel="canonical"' not in html:
        warnings.append(f"{name}: missing canonical URL")

    # 7. Word count (rough: count text in article-content div)
    content_match = re.search(r'class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>\s*(?:<!--|\n\s*<div)', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'class="[^"]*article-content[^"]*"[^>]*>(.*?)</(?:div|main)>', html, re.DOTALL)
    if content_match:
        text = re.sub(r'<[^>]+>', ' ', content_match.group(1))
        text = re.sub(r'\s+', ' ', text).strip()
        word_count = len(text.split())
        if word_count < MIN_WORDS:
            warnings.append(f"{name}: only {word_count} words (min {MIN_WORDS})")


def main():
    modified = set()
    for site in SITES:
        site_dir = ROOT / site
        for f in site_dir.glob("article-*.html"):
            # Only check files modified in working tree
            check_article(f)
            modified.add(str(f))

    if not modified:
        print("No article files to audit.")
        return 0

    print(f"Audited {len(modified)} article files across {len(SITES)} sites.\n")

    if warnings:
        print("=== WARNINGS ===")
        for w in warnings:
            print(f"  WARN:{w}")
        print()

    if errors:
        print(f"=== {len(errors)} ERRORS FOUND ===")
        for e in errors:
            print(f"  FAIL:{e}")
        print("\nCommit BLOCKED. Fix errors before pushing.")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
