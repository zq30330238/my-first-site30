"""Remove duplicate images placed after the nav header (wrong position).
The correct img is inside <article> - keep only that one.
"""
import re

BASE = r"d:\AI网站文件夹\entertainment"

import glob
for fpath in glob.glob(BASE + r"\article-*.html"):
    with open(fpath, encoding="utf-8") as f:
        html = f.read()

    orig = html

    # Remove img tag that's between nav </header> and <main> (wrong position)
    # Pattern: </header>\n\s*<img ...>\n\s*<main
    html = re.sub(r'</header>\s*\n\s*<img [^>]*>\s*\n\s*<main', '</header>\n<main', html)

    if html != orig:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"CLEANED: {fpath}")
    else:
        print(f"OK: {fpath}")

print("\nDone!")
