#!/usr/bin/env python3
"""对比本地和线上 CF Pages 站点，检测同步状态。"""
import subprocess, re, sys, json
from pathlib import Path
from datetime import datetime

ROOT = Path("d:/AI网站文件夹")
CONFIG_FILE = ROOT / "shared" / "site_config.json"


def check_site(dir_name, url):
    local_dir = ROOT / dir_name
    index_file = local_dir / "index.html"
    problems = []

    if not index_file.exists():
        return [f"{dir_name}: index.html MISSING locally"]

    local_html = index_file.read_text(encoding="utf-8", errors="ignore")

    # Local metrics
    local_cards = len(re.findall(r'class="[^"]*article-card[^"]*"', local_html))
    local_selects = len(re.findall(r'<select onchange=', local_html))
    local_adsbygoogle = 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in local_html
    local_ads_meta = 'google-adsense-account' in local_html
    local_robots = (local_dir / "robots.txt").exists()
    local_ads_txt = (local_dir / "ads.txt").exists()

    # Fetch live
    live_html = None
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15", url],
            capture_output=True, text=True, encoding="utf-8", timeout=20
        )
        live_html = result.stdout
    except Exception as e:
        problems.append(f"{dir_name}: LIVE FETCH ERROR: {e}")
        return problems

    if not live_html or len(live_html) < 100:
        problems.append(f"{dir_name}: LIVE FETCH FAILED (got {len(live_html) if live_html else 0} bytes)")
        return problems

    # Live metrics
    live_cards = len(re.findall(r'class="[^"]*article-card[^"]*"', live_html))
    live_selects = len(re.findall(r'<select onchange=', live_html))
    live_adsbygoogle = 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in live_html
    live_ads_meta = 'google-adsense-account' in live_html

    # Compare
    if local_cards != live_cards:
        problems.append(f"{dir_name}: article-cards LOCAL={local_cards} LIVE={live_cards}")
    if local_selects != live_selects:
        problems.append(f"{dir_name}: footer-selects LOCAL={local_selects} LIVE={live_selects}")
    if local_adsbygoogle != live_adsbygoogle:
        problems.append(f"{dir_name}: AdSense-script LOCAL={local_adsbygoogle} LIVE={live_adsbygoogle}")
    if local_ads_meta != live_ads_meta:
        problems.append(f"{dir_name}: AdSense-meta LOCAL={local_ads_meta} LIVE={live_ads_meta}")

    if not problems:
        problems.append(f"{dir_name}: OK")

    return problems


def main():
    config_path = CONFIG_FILE
    if not config_path.exists():
        print(f"ERROR: site_config.json not found at {config_path}")
        return 1

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    sites = config.get("sites", [])
    if not sites:
        print("ERROR: site_config.json has no sites list")
        return 1

    print(f"=== Sync Check {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    all_ok = 0
    all_mismatch = 0
    all_error = 0

    for site in sites:
        dir_name = site["dir"]
        url = f"https://{site['domain']}"
        results = check_site(dir_name, url)
        for r in results:
            if "OK" in r:
                all_ok += 1
                print(f"  OK   {r}")
            elif "MISSING" in r or "FETCH" in r:
                all_error += 1
                print(f"  ERR  {r}")
            else:
                all_mismatch += 1
                print(f"  DIFF {r}")

    print(f"\n---")
    print(f"Total: {all_ok} OK, {all_mismatch} DIFF, {all_error} ERROR")

    return 1 if all_mismatch > 0 or all_error > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
