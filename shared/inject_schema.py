"""Batch inject JSON-LD Schema.org structured data into all HTML pages."""
import re, json, os, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(r"d:\AI网站文件夹")

SITE_MAP = {
    "main-site":     ("jycsd.com",         "江阴车速递"),
    "sub-healthy":   ("healthy.jycsd.com", "HealthyEats"),
    "sub-pets":      ("pets.jycsd.com",    "PetCare Hub"),
    "sub-home":      ("home.jycsd.com",    "HomeJoy"),
    "sub-finance":   ("finance.jycsd.com", "MoneyWise"),
    "sub-tech":      ("tech.jycsd.com",    "TechNest"),
    "sub-travel":    ("travel.jycsd.com",  "TripRoute"),
}

AUTHOR_PATTERNS = [
    re.compile(r'<p[^>]*class="[^"]*font-medium[^"]*"[^>]*>([^<]+)</p>'),
    re.compile(r'<span[^>]*>By\s+([^<]+)</span>'),
    re.compile(r'<div[^>]*class="[^"]*author[^"]*"[^>]*>.*?<p[^>]*>([^<]+)</p>', re.DOTALL),
]

DATE_PATTERNS = [
    re.compile(r'(?:Updated\s+)?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s*\d{4})'),
]

CATEGORY_PATTERNS = [
    re.compile(r'&rsaquo;\s*<a[^>]*>([^<]+)</a>\s*&rsaquo;'),
    re.compile(r'<span[^>]*class="[^"]*tag[^"]*"[^>]*>([^<]+)</span>'),
    re.compile(r'<span[^>]*class="[^"]*(?:category|badge)[^"]*"[^>]*>([^<]+)</span>'),
    re.compile(r'Home</a>\s*<span[^>]*>[^<]*</span>\s*<a[^>]*>([^<]+)</a>'),
    re.compile(r'<span[^>]*class="[^"]*uppercase[^"]*tracking-wider[^"]*"[^>]*>([^<]+)</span>'),
    re.compile(r'<a[^>]*class="[^"]*(?:bg-brand-\d+|border-b-2 border-\[)[^"]*"[^>]*>([^<]+)</a>'),
]

MONTH_MAP = {m: i for i, m in enumerate(["January","February","March","April","May","June",
    "July","August","September","October","November","December"], 1)}
for abbr in ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]:
    MONTH_MAP[abbr] = MONTH_MAP[[k for k in MONTH_MAP if k.startswith(abbr)][0]]


def parse_date(text):
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            raw = m.group(1)
            for name, num in MONTH_MAP.items():
                if name in raw:
                    day = re.search(r'\d{1,2}', raw).group()
                    year = re.search(r'\d{4}', raw).group()
                    return f"{year}-{num:02d}-{int(day):02d}"
    return datetime.now().strftime("%Y-%m-%d")


def parse_author(html, site_name):
    for pat in AUTHOR_PATTERNS:
        m = pat.search(html)
        if m:
            return m.group(1).strip()
    return site_name + " Editorial Team"


def parse_category(html):
    for pat in CATEGORY_PATTERNS:
        m = pat.search(html)
        if m:
            return m.group(1).strip()
    return None


def parse_title(html):
    m = re.search(r'<title>([^<]+)</title>', html)
    if not m:
        return "Untitled"
    title = m.group(1).strip()
    site_names = {v[1] for v in SITE_MAP.values()}
    for sep in [" — ", " - ", " | "]:
        if sep in title:
            parts = title.split(sep)
            suffix = parts[-1].strip()
            if len(parts) >= 2 and suffix in site_names:
                title = sep.join(parts[:-1]).strip()
    return title


def parse_description(html):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r"<meta\s+name='description'\s+content='([^']+)'", html)
    if m:
        return m.group(1)
    return ""


def get_site_info(html_path):
    rel = str(html_path.relative_to(ROOT))
    for dir_name, (domain, site_name) in SITE_MAP.items():
        if rel.startswith(dir_name + os.sep) or rel.startswith(dir_name + "/"):
            return domain, site_name
    return "jycsd.com", "江阴车速递"


def get_page_url(html_path, domain, is_index):
    rel = str(html_path.relative_to(ROOT))
    dir_name = rel.split(os.sep)[0]
    filename = html_path.name
    if is_index:
        return f"https://{domain}/"
    return f"https://{domain}/{filename}"


def get_index_url(html_path, domain):
    return f"https://{domain}/"


def get_category_url(html_path, domain, category):
    return f"https://{domain}/"


def has_schema(html):
    return 'application/ld+json' in html


def build_article_schema(title, description, author, date_str, site_name, domain, page_url):
    return {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": description,
        "author": {"@type": "Person", "name": author},
        "datePublished": date_str,
        "dateModified": date_str,
        "publisher": {
            "@type": "Organization",
            "name": site_name,
            "url": f"https://{domain}"
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url}
    }


def build_breadcrumb_schema(home_url, category, category_url, article_title):
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": home_url},
    ]
    if category:
        items.append({"@type": "ListItem", "position": 2, "name": category, "item": category_url})
        items.append({"@type": "ListItem", "position": 3, "name": article_title})
    else:
        items.append({"@type": "ListItem", "position": 2, "name": article_title})
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }


def build_org_schema(site_name, domain):
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site_name,
        "url": f"https://{domain}",
        "logo": f"https://{domain}/favicon.ico"
    }


def build_website_schema(site_name, domain):
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site_name,
        "url": f"https://{domain}",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"https://{domain}/?s={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }


def make_script_tag(schema_obj):
    return f'<script type="application/ld+json">\n{json.dumps(schema_obj, indent=2, ensure_ascii=False)}\n</script>'


def inject_schemas(html, schemas):
    scripts = "\n".join(make_script_tag(s) for s in schemas)
    return html.replace("</head>", scripts + "\n</head>")


def process_article(filepath, dry_run=False):
    html = filepath.read_text(encoding="utf-8")
    if has_schema(html):
        return "skipped"

    domain, site_name = get_site_info(filepath)
    title = parse_title(html)
    description = parse_description(html)
    author = parse_author(html, site_name)
    date_str = parse_date(html)
    category = parse_category(html)
    page_url = get_page_url(filepath, domain, False)
    home_url = get_index_url(filepath, domain)
    category_url = get_category_url(filepath, domain, category)

    article_schema = build_article_schema(title, description, author, date_str, site_name, domain, page_url)
    breadcrumb_schema = build_breadcrumb_schema(home_url, category, category_url, title)
    schemas = [article_schema, breadcrumb_schema]

    if not dry_run:
        new_html = inject_schemas(html, schemas)
        filepath.write_text(new_html, encoding="utf-8")

    return f"injected: [{site_name}] {title[:60]} | author={author} | date={date_str} | cat={category}"


def process_index(filepath, dry_run=False):
    html = filepath.read_text(encoding="utf-8")
    if has_schema(html):
        return "skipped"

    domain, site_name = get_site_info(filepath)
    org_schema = build_org_schema(site_name, domain)
    website_schema = build_website_schema(site_name, domain)
    schemas = [org_schema, website_schema]

    if not dry_run:
        new_html = inject_schemas(html, schemas)
        filepath.write_text(new_html, encoding="utf-8")

    return f"injected: [{site_name}] index page"


def main():
    dry_run = "--dry-run" in sys.argv
    files = list(ROOT.glob("sub-*/article-*.html")) + \
            list(ROOT.glob("sub-*/index.html")) + \
            list(ROOT.glob("main-site/index.html"))

    stats = {"injected": 0, "skipped": 0, "errors": 0}

    for f in sorted(files):
        try:
            if f.name == "index.html":
                result = process_index(f, dry_run)
            else:
                result = process_article(f, dry_run)

            if result == "skipped":
                stats["skipped"] += 1
            else:
                stats["injected"] += 1
                print(f"  {result}")
        except Exception as e:
            stats["errors"] += 1
            print(f"  ERROR [{f.name}]: {e}")

    print(f"\nTotal: {stats['injected']} injected, {stats['skipped']} skipped, {stats['errors']} errors")
    if dry_run:
        print("DRY RUN - no files modified. Remove --dry-run to actually inject.")


if __name__ == "__main__":
    main()
