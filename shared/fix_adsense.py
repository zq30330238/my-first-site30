"""Replace ad placeholders with real AdSense units across all sub-sites.
Adds 3 responsive ad units (top/mid/bottom) to each article.
"""
import re
from pathlib import Path

ROOT = Path(r"d:\AI网站文件夹")
SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel"]
PUB_ID = "ca-pub-2595917642864488"

AD_SLOTS = {
    "article_top": "9112825459",
    "article_mid": "4397738132",
    "article_bottom": "9739511410",
}

def make_ad_unit(slot_name):
    slot_id = AD_SLOTS[slot_name]
    return (
        '<div class="ad-unit">'
        '<span class="ad-label">Advertisement</span>\n'
        '<ins class="adsbygoogle" '
        'style="display:block; min-height:280px" '
        f'data-ad-client="{PUB_ID}" '
        f'data-ad-slot="{slot_id}" '
        'data-ad-format="auto" '
        'data-full-width-responsive="true"></ins>\n'
        '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
        '</div>'
    )

NEW_AD_CSS = """.ad-unit {
    background: #f9fafb;
    border-radius: 8px;
    text-align: center;
    margin: 2.5rem 0;
    padding: 0.5rem 0 1.5rem 0;
    overflow: hidden;
}
.ad-label {
    display: block;
    text-align: center;
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
"""


def fix_article(filepath):
    html = filepath.read_text(encoding="utf-8", errors="ignore")

    # 1. Replace old ad-container CSS block with new ad-unit CSS
    html = re.sub(
        r'\.ad-container\s*\{[^}]*\}',
        NEW_AD_CSS,
        html,
        flags=re.DOTALL
    )

    # 2. Remove old placeholder div and replace with bottom ad unit
    old_div = re.compile(
        r'<div\s+class="[^"]*ad-container[^"]*"[^>]*>\s*<span>Advertisement</span>\s*</div>',
        re.DOTALL
    )
    bottom_ad = make_ad_unit("article_bottom")
    html = old_div.sub(bottom_ad, html)

    # 3. Insert top ad after first <p> in content
    article_match = re.search(r'<(?:article|main)[ >]', html)
    if not article_match:
        return 0

    # Find first paragraph after article/main start
    after_content = html[article_match.start():]
    p_match = re.search(r'<p[ >]', after_content)
    if not p_match:
        return 1  # only bottom ad

    abs_p_start = article_match.start() + p_match.start()
    p_end = html.find('</p>', abs_p_start)
    if p_end == -1:
        return 1

    p_end += 4
    top_ad = make_ad_unit("article_top")
    html = html[:p_end] + '\n' + top_ad + '\n' + html[p_end:]

    # 4. Insert mid ad — count paragraphs, insert after halfway
    all_p = list(re.finditer(r'<p[ >]', html))
    if len(all_p) >= 5:
        mid_idx = len(all_p) // 2
        mid_p_start = all_p[mid_idx].start()
        mid_p_end = html.find('</p>', mid_p_start) + 4
        if mid_p_end > 4:
            mid_ad = make_ad_unit("article_mid")
            html = html[:mid_p_end] + '\n' + mid_ad + '\n' + html[mid_p_end:]

    filepath.write_text(html, encoding="utf-8")
    return 3


def main():
    total = 0
    for site in SITES:
        site_dir = ROOT / site
        site_count = 0
        for f in sorted(site_dir.glob("article-*.html")):
            n = fix_article(f)
            if n > 0:
                site_count += 1
        print(f"{site}: {site_count} articles fixed")
        total += site_count

    print(f"\nTotal: {total} articles updated (~3 ad units each)")
    print(f"Publisher: {PUB_ID}")
    print("\nSlot IDs (create in AdSense dashboard):")
    for name, sid in AD_SLOTS.items():
        print(f"  {name}: {sid}")
    print("\nNEXT: https://adsense.google.com → Ads → Ad units → Create")


if __name__ == "__main__":
    main()
