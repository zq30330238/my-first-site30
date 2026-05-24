#!/usr/bin/env python3
"""Fix short article titles (< 30 chars) by regenerating with DeepSeek API.

Scans 9 content directories, strips brand suffixes from <title>,
regenerates if the pure title is < 30 characters, and updates
<title>, <h1>, and og:title in the HTML.
"""

import re
import sys
from pathlib import Path

# Add shared to path for reasonix_helper
sys.path.insert(0, str(Path(__file__).resolve().parent))

from reasonix_helper import ark_call_json

# Known brand names per site directory
SITE_BRANDS = {
    "sub-healthy": ["HealthyEats"],
    "sub-pets": ["PetCareHub", "Pet Care Hub"],
    "sub-home": ["HomeJoy"],
    "sub-finance": ["MoneyWise"],
    "sub-tech": ["TechSavvy", "TechNest", "TechSift"],
    "sub-travel": ["TripRoute", "TravelScope"],
    "entertainment": ["EntertainmentBuzz"],
    "rightsdaily": ["RightsDaily"],
    "dailymedadvice": ["DailyMedAdvice"],
}

# Human-readable category for SEO prompt context
SITE_CATEGORIES = {
    "sub-healthy": "health & nutrition",
    "sub-pets": "pet care",
    "sub-home": "home & garden",
    "sub-finance": "personal finance",
    "sub-tech": "technology",
    "sub-travel": "travel",
    "entertainment": "entertainment",
    "rightsdaily": "legal rights",
    "dailymedadvice": "medical & health",
}

SITE_NAMES = {
    "sub-healthy": "HealthyEats",
    "sub-pets": "PetCareHub",
    "sub-home": "HomeJoy",
    "sub-finance": "MoneyWise",
    "sub-tech": "TechSavvy",
    "sub-travel": "TripRoute",
    "entertainment": "EntertainmentBuzz",
    "rightsdaily": "RightsDaily",
    "dailymedadvice": "DailyMedAdvice",
}

SITES = sorted(SITE_BRANDS.keys())


def strip_brand(title: str, brands: list[str]) -> str:
    """Remove known brand suffixes from a title.

    Handles separators: -, --, |, — and brand name repetitions.
    """
    for brand in brands:
        while re.search(
            r"\s*[-–—|]\s*" + re.escape(brand) + r"\s*$", title
        ):
            title = re.sub(
                r"\s*[-–—|]\s*" + re.escape(brand) + r"\s*$", "", title
            )
    # Clean any remaining trailing separator (e.g. stray " - ")
    title = re.sub(r"\s*[-–—|]\s*$", "", title)
    return title.strip()


def extract_pure_title(html: str, brands: list[str]) -> str | None:
    """Extract pure title from HTML (brand suffix stripped)."""
    m = re.search(r"<title>(.*?)</title>", html)
    if not m:
        return None
    return strip_brand(m.group(1), brands)


def branded(pure: str, site_name: str) -> str:
    """Add site brand suffix for display in title/og:title."""
    return f"{pure} - {site_name}"


def rewrite_page(html: str, new_pure: str, site_name: str) -> str:
    """Replace <title>, og:title, and <h1> with new title."""
    new_branded = branded(new_pure, site_name)
    new_branded_esc = re.escape(new_branded)

    # -- <title> --
    # Find the old title, replace its content only
    m_title = re.search(r"<title>(.*?)</title>", html)
    if m_title:
        old = m_title.group(1)
        html = html.replace(f"<title>{old}</title>", f"<title>{new_branded}</title>", 1)

    # -- og:title --
    html = re.sub(
        r'<meta\s+property="og:title"\s+content="[^"]*"',
        f'<meta property="og:title" content="{new_branded}"',
        html,
    )

    # -- <h1> (replace inner text, keep any inner HTML tags) --
    h1_m = re.search(r"(<h1[^>]*>)(.*?)(</h1>)", html, re.DOTALL)
    if h1_m:
        old_h1_text = h1_m.group(2)
        # Preserve inner tags: strip tags for comparison, keep for replacement
        inner_stripped = re.sub(r"<[^>]+>", "", old_h1_text).strip()
        # Replace the text nodes, keeping any inner tags intact
        new_h1_content = old_h1_text.replace(inner_stripped, new_pure, 1)
        html = (
            html[: h1_m.start(2)]
            + new_h1_content
            + html[h1_m.end(2) :]
        )

    return html


def generate_title(old_title: str, site_key: str) -> str:
    """Call DeepSeek API to regenerate a longer, SEO-friendly title (30-60 chars)."""
    system_prompt = (
        "You are an SEO expert. Rewrite this article title to be 30-60 characters, "
        "compelling, and include relevant keywords. "
        "Return JSON: {\"title\": \"new title\"}"
    )
    user_message = (
        f"Current title: {old_title}\n"
        f"Site: {SITE_NAMES[site_key]}\n"
        f"Category: {SITE_CATEGORIES[site_key]}"
    )
    result = ark_call_json(system_prompt, user_message)
    return result["title"].strip()


def main():
    total_short = 0
    total_fixed = 0
    base = Path("d:/AI网站文件夹")

    for site_key in SITES:
        brands = SITE_BRANDS[site_key]
        site_name = SITE_NAMES[site_key]
        site_dir = base / site_key

        if not site_dir.is_dir():
            print(f"[SKIP] {site_key}: directory not found")
            continue

        articles = sorted(site_dir.glob("article-*.html"))
        for ap in articles:
            html = ap.read_text(encoding="utf-8", errors="ignore")
            pure = extract_pure_title(html, brands)
            if pure is None:
                print(f"[SKIP] {site_key}/{ap.name}: no <title> tag")
                continue

            if len(pure) >= 30:
                continue  # title is fine

            total_short += 1
            print(
                f"[SHORT] {site_key}/{ap.name}: "
                f'"{pure}" ({len(pure)} chars)'
            )

            # Generate new title via API
            try:
                new_title = generate_title(pure, site_key)
                if len(new_title) < 30:
                    print(
                        f"  -> API returned short title too ({len(new_title)} chars), "
                        f"retrying..."
                    )
                    new_title = generate_title(pure + " " + site_key, site_key)
                html = rewrite_page(html, new_title, site_name)
                ap.write_text(html, encoding="utf-8")
                total_fixed += 1
                print(
                    f'  -> FIXED: "{pure}" ({len(pure)} chars) -> '
                    f'"{new_title}" ({len(new_title)} chars)'
                )
            except Exception as e:
                print(f"  -> ERROR: {e}")

    print(f"\nDone. {total_short} short titles found, {total_fixed} fixed.")
    return 0 if total_short == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
