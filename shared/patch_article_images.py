"""Add feature images to all 33 entertainment article pages.
Inserts img after the ARTICLE's header (not the page nav header).
"""
import re

CATEGORY_MAP = {
    "article-1.html": "movies-category.jpg",
    "article-3.html": "movies-category.jpg",
    "article-8.html": "movies-category.jpg",
    "article-13.html": "movies-category.jpg",
    "article-17.html": "movies-category.jpg",
    "article-22.html": "movies-category.jpg",
    "article-24.html": "movies-category.jpg",
    "article-25.html": "movies-category.jpg",
    "article-32.html": "movies-category.jpg",
    "article-2.html": "tv-category.jpg",
    "article-5.html": "tv-category.jpg",
    "article-10.html": "tv-category.jpg",
    "article-14.html": "tv-category.jpg",
    "article-15.html": "tv-category.jpg",
    "article-21.html": "tv-category.jpg",
    "article-28.html": "tv-category.jpg",
    "article-33.html": "tv-category.jpg",
    "article-4.html": "celebrity-category.jpg",
    "article-6.html": "celebrity-category.jpg",
    "article-9.html": "celebrity-category.jpg",
    "article-12.html": "celebrity-category.jpg",
    "article-16.html": "celebrity-category.jpg",
    "article-23.html": "celebrity-category.jpg",
    "article-26.html": "celebrity-category.jpg",
    "article-29.html": "celebrity-category.jpg",
    "article-30.html": "celebrity-category.jpg",
    "article-7.html": "music-category.jpg",
    "article-11.html": "music-category.jpg",
    "article-18.html": "music-category.jpg",
    "article-19.html": "music-category.jpg",
    "article-20.html": "music-category.jpg",
    "article-27.html": "music-category.jpg",
    "article-31.html": "music-category.jpg",
}

BASE = r"d:\AI网站文件夹\entertainment"

for fname, cat_img in CATEGORY_MAP.items():
    fpath = f"{BASE}\\{fname}"
    with open(fpath, encoding="utf-8") as f:
        html = f.read()

    m = re.search(r'<h1[^>]*>([^<]+)', html)
    title = m.group(1).strip() if m else cat_img
    img_tag = f'\n        <img src="images/{cat_img}" alt="{title}" class="w-full rounded-2xl mb-10" loading="lazy">'

    # Strategy: find <article>...</article>, then find </header> within it
    article_m = re.search(r'(<article\b[^>]*>)(.*?)(</article>)', html, re.DOTALL)
    if not article_m:
        print(f"SKIP {fname}: no <article>")
        continue

    article_inner = article_m.group(2)
    # Find </header> within the article
    hdr_end = article_inner.find("</header>")
    if hdr_end == -1:
        print(f"SKIP {fname}: no </header> in article")
        continue

    after_hdr = article_inner[hdr_end + 9:]  # after "</header>"

    if after_hdr.lstrip().startswith("<img"):
        # Replace src in existing img
        old_img = re.search(r'<img\s+src="([^"]*)"', after_hdr)
        if old_img:
            new_inner = article_inner[:hdr_end + 9] + after_hdr.replace(
                old_img.group(0), f'<img src="images/{cat_img}"', 1
            )
    else:
        # Insert img after </header>
        new_inner = article_inner[:hdr_end + 9] + img_tag + article_inner[hdr_end + 9:]

    html = html[:article_m.start(2)] + new_inner + html[article_m.end(2):]

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK: {fname} -> {cat_img}")

print("\nDone!")
