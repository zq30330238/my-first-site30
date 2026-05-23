"""Replace Unsplash background images in index.html article cards with local category images."""
import re

CATEGORY_MAP = [
    ("article-1.html", "movies-category.jpg"),
    ("article-2.html", "tv-category.jpg"),
    ("article-3.html", "movies-category.jpg"),
    ("article-4.html", "celebrity-category.jpg"),
    ("article-5.html", "tv-category.jpg"),
    ("article-6.html", "celebrity-category.jpg"),
    ("article-7.html", "music-category.jpg"),
    ("article-8.html", "movies-category.jpg"),
    ("article-9.html", "celebrity-category.jpg"),
    ("article-10.html", "tv-category.jpg"),
    ("article-11.html", "music-category.jpg"),
    ("article-12.html", "celebrity-category.jpg"),
    ("article-13.html", "movies-category.jpg"),
    ("article-14.html", "tv-category.jpg"),
    ("article-15.html", "tv-category.jpg"),
    ("article-16.html", "celebrity-category.jpg"),
    ("article-17.html", "movies-category.jpg"),
    ("article-18.html", "music-category.jpg"),
    ("article-19.html", "music-category.jpg"),
    ("article-20.html", "music-category.jpg"),
    ("article-21.html", "tv-category.jpg"),
    ("article-22.html", "movies-category.jpg"),
    ("article-23.html", "celebrity-category.jpg"),
    ("article-24.html", "movies-category.jpg"),
    ("article-25.html", "movies-category.jpg"),
    ("article-26.html", "celebrity-category.jpg"),
    ("article-27.html", "music-category.jpg"),
    ("article-28.html", "tv-category.jpg"),
    ("article-29.html", "celebrity-category.jpg"),
    ("article-30.html", "celebrity-category.jpg"),
    ("article-31.html", "music-category.jpg"),
    ("article-32.html", "movies-category.jpg"),
    ("article-33.html", "tv-category.jpg"),
]

fpath = r"d:\AI网站文件夹\entertainment\index.html"
with open(fpath, encoding="utf-8") as f:
    html = f.read()

# Process in reverse order (last article first) to avoid position shifting
offset = 0
for article_file, cat_img in reversed(CATEGORY_MAP):
    href_pos = html.find(f'href="{article_file}"', 0, len(html) + offset if offset < 0 else None)
    if href_pos == -1:
        print(f"SKIP {article_file}: not found")
        continue

    bg_pos = html.find("background-image:url(", href_pos)
    if bg_pos == -1:
        print(f"SKIP {article_file}: no background-image")
        continue

    paren_start = bg_pos + len("background-image:url(")
    paren_end = html.find(")", paren_start)
    if paren_end == -1:
        continue

    old_url = html[paren_start:paren_end]
    new_url = f"images/{cat_img}"
    html = html[:paren_start] + new_url + html[paren_end:]
    print(f"  {article_file}: replaced bg image -> {new_url}")

print(f"\nDone! All cards updated.")
