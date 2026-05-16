"""Clean all ad blocks and insert exactly 3 valid AdSense units per article."""
import re
from pathlib import Path

ROOT = Path(r"d:\AI网站文件夹")
SITES = ["sub-healthy", "sub-pets", "sub-home", "sub-finance", "sub-tech", "sub-travel"]
PUB_ID = "ca-pub-2595917642864488"
SLOTS = ["9112825459", "4397738132", "9739511410"]  # top, mid, bottom

AD_UNIT_RE = re.compile(
    r'\n?\s*<div class="ad-unit">.*?</div>\s*',
    re.DOTALL
)
AD_CONTAINER_RE = re.compile(
    r'\n?\s*<div class="ad-container[^"]*"[^>]*>.*?</div>\n?',
    re.DOTALL
)
# Standalone ad push scripts that aren't inside ad-unit divs
AD_SCRIPT_RE = re.compile(
    r'\n?\s*<script>\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\);</script>\s*',
    re.DOTALL
)


def make_ad_unit(slot_id):
    return (
        '<div class="ad-unit">\n'
        '<span class="ad-label">Advertisement</span>\n'
        '<ins class="adsbygoogle" '
        'style="display:block; min-height:280px" '
        f'data-ad-client="{PUB_ID}" '
        f'data-ad-slot="{slot_id}" '
        'data-ad-format="auto" '
        'data-full-width-responsive="true"></ins>\n'
        '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>\n'
        '</div>'
    )


def fix_article(filepath):
    html = filepath.read_text(encoding="utf-8", errors="ignore")

    # Step 1: Remove ALL existing ad-unit blocks
    html = AD_UNIT_RE.sub('', html)
    # Step 2: Remove ALL ad-container placeholders
    html = AD_CONTAINER_RE.sub('', html)
    # Step 3: Remove any standalone ad scripts left over
    html = AD_SCRIPT_RE.sub('', html)
    # Step 4: Clean up double-newlines that may result from removals
    html = re.sub(r'\n{3,}', '\n\n', html)

    # Step 5: Find insertion points
    h2_positions = [m.end() for m in re.finditer(r'</h2>', html)]
    # Fallback: use paragraph positions if not enough h2s
    if len(h2_positions) >= 3:
        total = len(h2_positions)
        indices = sorted([0, total // 2, total - 1])
        insert_positions = sorted(set(h2_positions[i] for i in indices), reverse=True)
    else:
        # Use h2 positions + paragraph positions to get 3 insertion points
        p_positions = [m.end() for m in re.finditer(r'</p>', html)]
        candidates = list(h2_positions)
        # Add paragraph positions spread across the content
        if p_positions:
            step = max(1, len(p_positions) // (4 - len(h2_positions)))
            for i in range(0, len(p_positions), step):
                if len(candidates) >= 3:
                    break
                if p_positions[i] not in candidates:
                    candidates.append(p_positions[i])
        if len(candidates) < 3:
            print(f"  SKIP: {filepath.name} has only {len(candidates)} insertion points")
            filepath.write_text(html, encoding="utf-8")
            return 0
        candidates.sort()
        # Pick first, middle, last
        indices = sorted([0, len(candidates) // 2, len(candidates) - 1])
        insert_positions = sorted(set(candidates[i] for i in indices), reverse=True)

    for i, pos in enumerate(insert_positions):
        # insert_positions is descending (last in file first), so reverse the slot index
        slot_idx = len(insert_positions) - 1 - i
        ad_html = '\n' + make_ad_unit(SLOTS[slot_idx]) + '\n'
        html = html[:pos] + ad_html + html[pos:]

    filepath.write_text(html, encoding="utf-8")

    # Verify
    slots_found = re.findall(r'data-ad-slot="(\d+)"', html)
    bad = set(slots_found) - set(SLOTS)
    if bad:
        print(f"  WARN: {filepath.name} has bad slots: {bad}")
        return 0
    return len(slots_found)


def main():
    total_ok = 0
    total_slots = 0
    for site in SITES:
        site_dir = ROOT / site
        site_ok = 0
        site_slots = 0
        for f in sorted(site_dir.glob("article-*.html")):
            n = fix_article(f)
            if n == 3:
                site_ok += 1
                site_slots += n
            elif n > 0:
                print(f"  WARN: {f.name} has {n} slots (expected 3)")
                site_ok += 1
                site_slots += n
        print(f"{site}: {site_ok} OK, {site_slots} ad slots")
        total_ok += site_ok
        total_slots += site_slots

    print(f"\nTotal: {total_ok} articles, {total_slots} ad slots")
    print(f"Expected: {total_ok * 3} slots")
    print("Slots: top=9112825459, mid=4397738132, bottom=9739511410")


if __name__ == "__main__":
    main()
