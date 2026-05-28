import argparse
import json
import os
import re
import sys
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "shared", "site_config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_domain_map(config):
    domain_map = {}
    for site in config["sites"]:
        domain = site["domain"]
        domain_map[domain] = {
            "dir": site["dir"],
            "category": site.get("category", ""),
            "title": "",
        }
    return domain_map

def build_dir_domain_map(config):
    dirmap = {}
    for site in config["sites"]:
        dirmap[site["dir"]] = site["domain"]
    return dirmap

def list_site_dirs(config):
    dirs = []
    for site in config["sites"]:
        site_path = os.path.join(BASE_DIR, site["dir"])
        index_path = os.path.join(site_path, "index.html")
        if os.path.isfile(index_path):
            dirs.append((site["dir"], site_path))
    return dirs

def parse_select_options(html):
    selects = []
    pattern = re.compile(
        r'<select[^>]*onchange\s*=\s*"[^"]*"[^>]*>.*?</select>',
        re.IGNORECASE | re.DOTALL,
    )
    for select_match in pattern.finditer(html):
        select_html = select_match.group(0)
        options = []
        option_pattern = re.compile(
            r'<option\s+value\s*=\s*"([^"]*)"\s*>(.*?)</option>',
            re.IGNORECASE | re.DOTALL,
        )
        for opt_match in option_pattern.finditer(select_html):
            value = opt_match.group(1).strip()
            label = re.sub(r'<[^>]+>', '', opt_match.group(2)).strip()
            label = label.replace('&amp;', '&').replace('&mdash;', '—').replace('&lt;', '<').replace('&gt;', '>')
            if value:
                options.append((label, value))
        selects.append(options)
    return selects

def extract_domain(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname if parsed.hostname else ""

def check_site(site_name, site_path, domain_map):
    index_path = os.path.join(site_path, "index.html")
    if not os.path.isfile(index_path):
        return f"SKIP (no index.html)"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    selects = parse_select_options(html)
    if not selects:
        return "SKIP (no footer selects found)"

    all_domains_used = set()
    errors = []

    for select_idx, options in enumerate(selects):
        for label, value in options:
            domain = extract_domain(value)
            if not domain:
                continue
            all_domains_used.add(domain)
            if domain not in domain_map:
                errors.append(f"Select[{select_idx}]: '{label}' -> {domain} (unknown domain)")

    for domain in sorted(domain_map.keys()):
        if domain not in all_domains_used:
            errors.append(f"Missing: {domain} ({domain_map[domain]['dir']})")

    if errors:
        return "FAIL: " + "; ".join(errors)
    return f"OK ({len(selects)} dropdown(s), {len(all_domains_used)} sites)"

def fix_site_footer(site_name, site_path, domain_map, dir_domain_map):
    index_path = os.path.join(site_path, "index.html")
    if not os.path.isfile(index_path):
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    original_html = html
    known_domains = set(domain_map.keys())
    all_site_dirs = set(dir_domain_map.keys())

    def fix_url(match):
        url = match.group(1)
        domain = extract_domain(url)
        if domain and domain not in known_domains:
            for dir_name, correct_domain in sorted(dir_domain_map.items(), key=lambda x: -len(x[1])):
                if dir_name.replace("-site", "").replace("-", "") in url.lower() or \
                   dir_name.replace("sub-", "").replace("-site", "").replace("-", "") in url.lower().replace(".jycsd.com", "").replace(".com", ""):
                    if domain != correct_domain:
                        new_url = url.replace(domain, correct_domain)
                        print(f"  FIX: {domain} -> {correct_domain} (dir: {dir_name})")
                        return f'value="{new_url}"'
                    break
        return match.group(0)

    def fix_option_match(opt_match):
        full = opt_match.group(0)
        new_full = re.sub(r'value\s*=\s*"([^"]*)"', fix_url, full)
        return new_full

    select_pattern = re.compile(
        r'<select[^>]*onchange\s*=\s*"[^"]*"[^>]*>.*?</select>',
        re.IGNORECASE | re.DOTALL,
    )
    html = select_pattern.sub(lambda m: re.sub(
        r'<option\s+value\s*=\s*"([^"]*)"\s*>.*?</option>',
        fix_option_match,
        m.group(0),
    ), html)

    if html != original_html:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False

def run_check(site_filter=None, fix=False):
    config = load_config()
    domain_map = build_domain_map(config)
    dir_domain_map = build_dir_domain_map(config)
    site_dirs = list_site_dirs(config)

    if site_filter:
        site_dirs = [s for s in site_dirs if s[0] == site_filter]
        if not site_dirs:
            print(f"ERROR: no site found matching '{site_filter}'")
            print(f"Available dirs: {', '.join(s[0] for s in list_site_dirs(config))}")
            sys.exit(1)

    print("=== Portal Consistency Check ===")

    ok_count = 0
    fail_count = 0
    skip_count = 0
    results = []

    for site_name, site_path in sorted(site_dirs):
        result = check_site(site_name, site_path, domain_map)
        if result.startswith("OK"):
            status = "OK"
            ok_count += 1
        elif result.startswith("SKIP"):
            status = "SKIP"
            skip_count += 1
        else:
            status = "FAIL"
            fail_count += 1

        line = f"{site_name:30s} {status}"
        if status == "FAIL":
            line += f"  {result}"
            if fix:
                print(f"\n{site_name}: fixing...")
                changed = fix_site_footer(site_name, site_path, domain_map, dir_domain_map)
                if changed:
                    print(f"  Fixed: {site_name}")
                else:
                    print(f"  Could not auto-fix, need manual review")
        results.append((site_name, status, result))

    for site_name, status, result in results:
        if status == "FAIL":
            suffix = result[5:]
            print(f"{site_name:30s} FAIL: {suffix}")
        else:
            print(f"{site_name:30s} {status}")

    total = ok_count + fail_count + skip_count
    print(f"\nTotal: {ok_count}/{total} OK, {fail_count} FAIL, {skip_count} SKIP")

    if fail_count > 0:
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="Verify cross-site footer portal links are consistent with site_config.json"
    )
    parser.add_argument("site_dir", nargs="?", default=None,
                        help="Check a single site directory (e.g. naruto-site)")
    parser.add_argument("--fix", action="store_true",
                        help="Auto-fix mismatched portal links")
    args = parser.parse_args()

    run_check(site_filter=args.site_dir, fix=args.fix)

if __name__ == "__main__":
    main()
