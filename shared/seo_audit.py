import os
import glob
import re
from html.parser import HTMLParser
from collections import Counter
from datetime import datetime

ROOT = r"d:/AI网站文件夹"
OUTPUT = os.path.join(ROOT, "shared", "seo-audit-report.md")


class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.meta_desc = None
        self.og_title = None
        self.og_description = None
        self.robots = None
        self.canonical = None
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            prop = attrs.get("property", "").lower()
            content = attrs.get("content", "")
            if name == "description":
                self.meta_desc = content
            elif name == "robots":
                self.robots = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
        elif tag == "link":
            rel = attrs.get("rel", "").lower()
            if rel == "canonical":
                self.canonical = attrs.get("href", "")

    def handle_data(self, data):
        if self._in_title and self.title is None:
            self.title = data.strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False


def safe_len(s):
    return len(s) if s else 0


def icon(ok):
    if ok:
        return "+"
    return "X"


def gather_files():
    files = []
    for subdir in glob.glob(os.path.join(ROOT, "sub-*")):
        if os.path.isdir(subdir):
            for pat in ["article-*.html", "index.html", "about.html", "cookie-policy.html", "privacy-policy.html", "terms-of-service.html"]:
                for f in glob.glob(os.path.join(subdir, pat)):
                    files.append(f)
    for pat in ["index.html", "about.html", "cookie-policy.html", "privacy-policy.html", "terms-of-service.html"]:
        for f in glob.glob(os.path.join(ROOT, "main-site", pat)):
            if os.path.isfile(f):
                files.append(f)
    return sorted(files)


def extract_page(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    parser = MetaExtractor()
    parser.feed(html)
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    return {
        "path": rel,
        "title": parser.title or "",
        "title_len": safe_len(parser.title),
        "meta_desc": parser.meta_desc or "",
        "desc_len": safe_len(parser.meta_desc),
        "og_title": parser.og_title or "",
        "og_description": parser.og_description or "",
        "robots": parser.robots or "",
        "canonical": parser.canonical or "",
        "has_og": bool(parser.og_title or parser.og_description),
    }


def check_title_len(ln):
    if 50 <= ln <= 60:
        return "pass", ""
    elif ln < 50:
        return "warn", f"Too short ({ln} chars, want 50-60)"
    else:
        return "warn", f"Too long ({ln} chars, want 50-60)"


def check_desc_len(ln):
    if 120 <= ln <= 155:
        return "pass", ""
    elif ln < 120:
        return "warn", f"Too short ({ln} chars, want 120-155)"
    else:
        return "warn", f"Too long ({ln} chars, want 120-155)"


def build_report(pages):
    lines = []
    lines.append("# SEO Audit Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Pages scanned:** {len(pages)}")
    lines.append("")

    total = len(pages)
    title_pass = sum(1 for p in pages if check_title_len(p["title_len"])[0] == "pass")
    desc_pass = sum(1 for p in pages if check_desc_len(p["desc_len"])[0] == "pass")
    has_og = sum(1 for p in pages if p["has_og"])
    has_canonical = sum(1 for p in pages if p["canonical"])
    missing_title = sum(1 for p in pages if not p["title"])
    missing_desc = sum(1 for p in pages if not p["meta_desc"])

    lines.append("## Summary")
    lines.append(f"- Title length in 50-60 range: {title_pass}/{total} {icon(title_pass == total)}")
    lines.append(f"- Description length in 120-155 range: {desc_pass}/{total} {icon(desc_pass == total)}")
    lines.append(f"- Pages with OG tags: {has_og}/{total} {icon(has_og == total)}")
    lines.append(f"- Pages with canonical: {has_canonical}/{total} {icon(has_canonical == total)}")
    lines.append(f"- Pages missing title: {missing_title} {icon(missing_title == 0)}")
    lines.append(f"- Pages missing meta description: {missing_desc} {icon(missing_desc == 0)}")
    lines.append("")

    lines.append("## Per-Page Details")
    lines.append("")
    for p in pages:
        t_ok, t_note = check_title_len(p["title_len"])
        d_ok, d_note = check_desc_len(p["desc_len"])
        lines.append(f"### `{p['path']}`")
        lines.append("")
        lines.append("| Field | Value | Check |")
        lines.append("|---|---|---|")
        lines.append(
            f"| Title | {p['title'] or '*--*'} | "
            f"{p['title_len']} chars {icon(t_ok == 'pass')} {t_note} |"
        )
        lines.append(
            f"| Meta Description | {p['meta_desc'] or '*--*'} | "
            f"{p['desc_len']} chars {icon(d_ok == 'pass')} {d_note} |"
        )
        lines.append(f"| og:title | {p['og_title'] or '*--*'} | |")
        lines.append(f"| og:description | {p['og_description'] or '*--*'} | |")
        lines.append(f"| Robots | {p['robots'] or '*--*'} | |")
        lines.append(f"| Canonical | {p['canonical'] or '*--*'} | {icon(bool(p['canonical']))} |")
        lines.append("")

    lines.append("## Duplicate Content Detection")
    lines.append("")

    title_counts = Counter(p["title"] for p in pages if p["title"])
    dup_titles = {t: c for t, c in title_counts.items() if c > 1}
    lines.append("### Duplicate Titles")
    if dup_titles:
        for t, c in sorted(dup_titles.items()):
            dup_pages = [p["path"] for p in pages if p["title"] == t]
            lines.append(f"- **\"{t}\"** appears {c}x:")
            for dp in dup_pages:
                lines.append(f"  - `{dp}`")
    else:
        lines.append("No duplicate titles found. +")
    lines.append("")

    desc_counts = Counter(p["meta_desc"] for p in pages if p["meta_desc"])
    dup_descs = {d: c for d, c in desc_counts.items() if c > 1}
    lines.append("### Duplicate Meta Descriptions")
    if dup_descs:
        for d, c in sorted(dup_descs.items()):
            dup_pages = [p["path"] for p in pages if p["meta_desc"] == d]
            lines.append(f"- Appears {c}x:")
            lines.append(f"  - \"{d}\"")
            for dp in dup_pages:
                lines.append(f"  - `{dp}`")
    else:
        lines.append("No duplicate descriptions found. +")
    lines.append("")

    lines.append("## Action Items")
    lines.append("")
    issues = []
    for p in pages:
        t_ok, t_note = check_title_len(p["title_len"])
        d_ok, d_note = check_desc_len(p["desc_len"])
        if t_ok != "pass":
            issues.append(f"- `{p['path']}` -- Title {t_note}")
        if d_ok != "pass":
            issues.append(f"- `{p['path']}` -- Meta description {d_note}")
        if not p["title"]:
            issues.append(f"- `{p['path']}` -- Missing `<title>`")
        if not p["meta_desc"]:
            issues.append(f"- `{p['path']}` -- Missing meta description")
        if not p["has_og"]:
            issues.append(f"- `{p['path']}` -- Missing og:title and og:description")
        if not p["canonical"]:
            issues.append(f"- `{p['path']}` -- Missing canonical link")

    if issues:
        for i in issues:
            lines.append(i)
    else:
        lines.append("All checks passed! +")

    return "\n".join(lines)


def main():
    files = gather_files()
    print(f"Scanning {len(files)} files...")
    pages = [extract_page(f) for f in files]
    report = build_report(pages)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {OUTPUT}")
    print(f"Pages: {len(pages)}")


if __name__ == "__main__":
    main()
