"""Add left-side sticky AdSense ad to all article pages. Handles 4 layout patterns."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEFT_AD = '<aside class="hidden xl:block w-40 shrink-0"><div class="sticky top-20"><div class="ad-unit">\n<span class="ad-label">Advertisement</span>\n<ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2595917642864488" data-ad-slot="9112825459" data-ad-format="vertical" data-full-width-responsive="true"></ins>\n<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>\n</div></div></aside>'

def process(html):
    """Apply first matching pattern, return (html, changed)."""
    original = html

    # Pattern A: max-w-6xl wrapper + flex-row gap-10 (old articles: pets/healthy/finance/tech 1-15)
    html = re.sub(
        r'(<div class="max-w-6xl mx-auto px-4 py-8">)\s*(<div class="flex flex-col lg:flex-row gap-10">)',
        r'<div class="max-w-7xl mx-auto px-4 py-8"><div class="flex flex-col lg:flex-row gap-6">'
        + LEFT_AD + r'\2',
        html, count=1
    )
    if html != original:
        return html, True

    # Pattern B: main max-w-4xl (newer articles: 16+ across all sites)
    html = re.sub(
        r'<main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">',
        r'<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"><div class="flex gap-6">'
        + LEFT_AD
        + r'<div class="flex-1 min-w-0">',
        html, count=1
    )
    if html != original:
        html = html.replace('</main>', '</div></div></main>', 1)
        return html, True

    # Pattern C: main flex-grow max-w-7xl w-full (travel articles)
    html = re.sub(
        r'(<main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 py-12 w-full">)',
        r'\1<div class="flex gap-6">'
        + LEFT_AD
        + r'<div class="flex-1 min-w-0">',
        html, count=1
    )
    if html != original:
        html = html.replace('</main>', '</div></div></main>', 1)
        return html, True

    # Pattern D: main flex-grow max-w-7xl lg:px-8 py-10 (home articles with w-2/3 sidebar)
    html = re.sub(
        r'(<main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">)',
        r'\1<div class="flex gap-6">'
        + LEFT_AD
        + r'<div class="flex-1 min-w-0">',
        html, count=1
    )
    if html != original:
        html = html.replace('</main>', '</div></div></main>', 1)
        return html, True

    return html, False


def main():
    dry_run = "--dry-run" in sys.argv
    sites = ["sub-pets", "sub-healthy", "sub-home", "sub-finance", "sub-tech", "sub-travel"]
    updated = 0
    total = 0
    unmatched = []

    for site in sites:
        site_path = ROOT / site
        if not site_path.exists():
            continue
        for article in sorted(site_path.glob("article-*.html")):
            total += 1
            html = article.read_text(encoding="utf-8")
            _, ok = process(html)
            if ok:
                if not dry_run:
                    article.write_text(process(html)[0], encoding="utf-8")
                updated += 1
            else:
                unmatched.append(f"{site}/{article.name}")

    label = "Would update" if dry_run else "Updated"
    print(f"{label} {updated}/{total} articles")
    if unmatched:
        print(f"Unmatched ({len(unmatched)}):")
        for u in unmatched:
            print(f"  {u}")

if __name__ == "__main__":
    main()
