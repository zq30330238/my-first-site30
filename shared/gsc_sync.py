"""Google Search Console API工具：同步站点 + 提交sitemap + 查看状态 + 前置审计

用法:
    python shared/gsc_sync.py              # 默认: check → sync → sitemap
    python shared/gsc_sync.py --check      # 只审计，不提交
    python shared/gsc_sync.py --sync       # 只同步站点（跳过检查）
    python shared/gsc_sync.py --sitemap    # 只提交sitemap（跳过检查）
    python shared/gsc_sync.py --force      # 跳过检查直接提交
    python shared/gsc_sync.py --status     # 查看SC状态
"""

import os, sys, json, time, urllib.parse, re, xml.etree.ElementTree as ET, random
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "shared", "site_config.json")

sys.path.insert(0, SCRIPT_DIR)
from gsc_auth import get_token

BASE_URL = "https://www.googleapis.com/webmasters/v3"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

# 阻塞规则: 哪些检查项会阻止提交
BLOCK_RULES = {
    "sitemap": "BLOCK",
    "sitemap_incomplete": "BLOCK",
    "robots": "WARN",
    "canonical": "BLOCK",
    "seo": "BLOCK",
    "dead_links": "BLOCK",
    "bad_images": "BLOCK",
    "noindex": "BLOCK",
    "favicon": "WARN",
}

# 政策类页面basename，应设noindex
POLICY_PAGES = {"about", "contact", "privacy-policy", "terms", "cookie-policy", "sitemap"}


def load_sites():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)["sites"]


def domain_to_site_url(domain):
    return f"https://{domain}/"


def get_headers():
    return {"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"}


def encode_url(url):
    return urllib.parse.quote(url, safe="")


def get_existing_sites(headers):
    """获取Search Console中已有站点的URL集合"""
    resp = requests.get(f"{BASE_URL}/sites", headers=headers, timeout=15)
    resp.raise_for_status()
    return {s["siteUrl"] for s in resp.json().get("siteEntry", [])}


def add_site(site_url, headers):
    """添加站点到Search Console，返回(状态码, 是否成功)"""
    resp = requests.put(f"{BASE_URL}/sites/{encode_url(site_url)}", headers=headers, timeout=15)
    return resp.status_code, resp.status_code in (200, 204)


def submit_sitemap(site_url, headers):
    """提交sitemap到Search Console，返回(状态码, 是否成功)"""
    sitemap_url = f"{site_url}sitemap.xml"
    encoded_site = encode_url(site_url)
    encoded_sitemap = encode_url(sitemap_url)
    resp = requests.put(
        f"{BASE_URL}/sites/{encoded_site}/sitemaps/{encoded_sitemap}",
        headers=headers, timeout=15,
    )
    return resp.status_code, resp.status_code in (200, 204)


def get_sitemaps(site_url, headers):
    """获取站点的sitemap列表"""
    encoded = encode_url(site_url)
    resp = requests.get(f"{BASE_URL}/sites/{encoded}/sitemaps", headers=headers, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("sitemap", [])
    return []


# ─── 功能1: 同步站点 ────────────────────────────────

def sync_sites():
    print("=" * 60)
    print("功能1: 同步站点到 Search Console")
    print("=" * 60)

    all_sites = load_sites()
    headers = get_headers()

    print("\n获取Search Console已有站点列表...")
    existing = get_existing_sites(headers)
    print(f"已有站点: {len(existing)} 个")

    new_sites = [s for s in all_sites if domain_to_site_url(s["domain"]) not in existing]

    if not new_sites:
        print("所有站点已在 Search Console 中，无需添加。")
        return

    print(f"\n待添加站点: {len(new_sites)} 个")

    added = []
    failed = []
    for s in new_sites:
        site_url = domain_to_site_url(s["domain"])
        print(f"  添加 {site_url} ... ", end="", flush=True)
        try:
            status, ok = add_site(site_url, headers)
            if ok:
                print("OK")
                added.append(site_url)
            else:
                print(f"失败 (HTTP {status})")
                failed.append(site_url)
        except requests.RequestException as e:
            print(f"异常: {e}")
            failed.append(site_url)

    if added:
        print("\n等待5秒后验证新站点...")
        time.sleep(5)
        try:
            existing_after = get_existing_sites(headers)
            verified = [u for u in added if u in existing_after]
            print(f"验证: {verified}/{len(added)} 新站点已确认")
            unverified = [u for u in added if u not in existing_after]
            for u in unverified:
                print(f"  未确认: {u}")
        except requests.RequestException as e:
            print(f"验证失败: {e}")

    print(f"\n结果汇总:")
    print(f"  已存在: {len(existing)}")
    print(f"  新加入: {len(added)}")
    if failed:
        print(f"  失败: {len(failed)}")
        for u in failed:
            print(f"    - {u}")


# ─── 功能2: 提交sitemap ──────────────────────────────

# 独立域名在SC中验证的是www版本，提交sitemap需用www
WWW_DOMAINS = {"rightsdaily.com", "dailymedadvice.com"}

def submit_sitemaps():
    print("=" * 60)
    print("功能2: 批量提交 Sitemap")
    print("=" * 60)

    all_sites = load_sites()
    headers = get_headers()

    results = []
    for i, s in enumerate(all_sites, 1):
        site_url = domain_to_site_url(s["domain"])
        # 独立域名SC验证的是www版本
        if s["domain"] in WWW_DOMAINS:
            site_url = f"https://www.{s['domain']}/"
        print(f"  [{i}/{len(all_sites)}] {site_url} ... ", end="", flush=True)
        try:
            status, ok = submit_sitemap(site_url, headers)
            label = "OK" if ok else f"HTTP {status}"
            print(label)
            results.append((site_url, label))
        except requests.RequestException as e:
            print(f"异常: {e}")
            results.append((site_url, f"ERROR: {e}"))

    ok = sum(1 for _, st in results if st == "OK")
    fail = [r for r in results if r[1] != "OK"]
    print(f"\n成功: {ok}/{len(all_sites)}")
    if fail:
        print(f"失败: {len(fail)}")
        for url, st in fail:
            print(f"  - {url} {st}")


# ─── 功能3: 查看状态 ────────────────────────────────

def status():
    print("=" * 60)
    print("功能3: Search Console 站点状态")
    print("=" * 60)

    all_sites = load_sites()
    headers = get_headers()

    print("\n获取Search Console已有站点...")
    existing = get_existing_sites(headers)

    print(f"\n{'站点':<28} {'在SC':<12} {'sitemap':<7} {'URL数':<8} {'最后抓取':<25}")
    print("-" * 80)

    in_sc = 0
    total_subs = 0
    total_urls = 0

    for s in all_sites:
        site_url = domain_to_site_url(s["domain"])
        present = site_url in existing
        if present:
            in_sc += 1

        sm_status = "-"
        url_cnt = "-"
        last_dl = "-"

        # 独立域名SC验证的是www版本，查非www会403
        check_url = site_url
        if s["domain"] in WWW_DOMAINS:
            check_url = f"https://www.{s['domain']}/"
            # www版本可能在existing里
            if check_url in existing:
                present = True

        if present or s["domain"] in WWW_DOMAINS:
            sitemaps = get_sitemaps(check_url, headers)
            if sitemaps:
                sm = sitemaps[0]
                sm_status = "Y"
                contents = sm.get("contents", [])
                if contents:
                    url_cnt = contents[0].get("submitted", "-")
                    if isinstance(url_cnt, int):
                        total_urls += url_cnt
                last_dl = (sm.get("lastDownloaded", "") or "")[:19]
                if last_dl:
                    total_subs += 1

        label = s["domain"]
        in_sc_str = "YES" if present else (f"YES(www)" if s["domain"] in WWW_DOMAINS else "NO")
        print(f"{label:<28} {in_sc_str:<12} {sm_status:<7} {str(url_cnt):<8} {last_dl:<25}")

    print("-" * 80)
    print(f"总计: {len(all_sites)} 站点, {in_sc} 在SC, {total_subs} sitemaps, {total_urls} URLs")


# ─── 功能4: 前置审计 ────────────────────────────────

def get_all_html_files(site_path):
    """获取站点目录下所有HTML文件路径"""
    html_files = []
    for root, dirs, files in os.walk(site_path):
        for f in files:
            if f.endswith(".html") or f.endswith(".htm"):
                html_files.append(os.path.join(root, f))
    return sorted(html_files)


def read_file_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            return ""


def has_noindex(content):
    return bool(re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']noindex', content, re.I))


def filepath_to_url_path(filepath, site_path, domain):
    """将绝对文件路径映射为相对URL路径"""
    rel = os.path.relpath(filepath, site_path).replace("\\", "/")
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    if rel.endswith(".html"):
        return "/" + rel
    return "/" + rel


def find_url_files_for_domain(domain, site_path):
    """从sitemap中提取URL集合，便于查找"""
    sitemap_path = os.path.join(site_path, "sitemap.xml")
    if not os.path.isfile(sitemap_path):
        return set()
    content = read_file_content(sitemap_path)
    # 提取loc标签内的实际路径部分（去掉域名）
    urls = set()
    for m in re.finditer(r"<loc>https?://([^<]+)</loc>", content):
        url = m.group(1)
        # strip domain prefix
        if url.startswith(domain) or url.startswith(f"www.{domain}"):
            path_part = url[len(domain):] if url.startswith(domain) else url[len(f"www.{domain}"):]
            urls.add(path_part.rstrip("/"))
        else:
            urls.add(url.rstrip("/"))
    return urls


def href_to_filepath(href, site_path, current_dir=None):
    """将href链接映射到磁盘文件路径，不存在返回None

    支持格式:
      /about.html       → about.html (从site_path解析)
      /guides/char/     → guides/char/index.html (从site_path解析)
      /guides/char      → guides/char.html or guides/char/index.html (从site_path解析)
      /                 → index.html
      ../index.html     → (相对于current_dir解析)
      kirito.html       → (相对于current_dir解析)
    """
    raw = href.strip()

    # 跳过特殊协议和锚点
    if any(raw.startswith(p) for p in ("#", "mailto:", "tel:", "javascript:")):
        return None
    if raw.startswith("//"):
        return None
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlparse(raw)
        raw = parsed.path or "/"

    is_root_absolute = raw.startswith("/")
    # 去掉 hash fragment (#xxx) 后再检查链接
    raw_no_hash = raw.split("#")[0]
    path = raw_no_hash.lstrip("/").replace("\\", "/")

    if not path or path == "/":
        return os.path.join(site_path, "index.html")

    if current_dir and not is_root_absolute:
        # 相对路径 → 从current_dir解析
        # href的原始值可能是 ../kirito.html 或 kirito.html
        candidate = os.path.normpath(os.path.join(current_dir, raw_no_hash))
        if os.path.isfile(candidate):
            return candidate
        # 尝试candidate作为目录（index.html）
        candidate_idx = os.path.join(candidate, "index.html")
        if os.path.isfile(candidate_idx):
            return candidate_idx
        # 尝试加.html
        if "." not in os.path.basename(candidate):
            candidate2 = candidate + ".html"
            if os.path.isfile(candidate2):
                return candidate2
        return None

    # 根绝对路径 → 从site_path解析
    candidate = os.path.join(site_path, path)
    if os.path.isfile(candidate):
        return candidate

    if path.endswith("/"):
        candidate = os.path.join(site_path, path, "index.html")
        if os.path.isfile(candidate):
            return candidate
        candidate = os.path.join(site_path, path.rstrip("/") + ".html")
        if os.path.isfile(candidate):
            return candidate
    else:
        if not path.endswith(".html") and "." not in os.path.basename(path):
            candidate = os.path.join(site_path, path + ".html")
            if os.path.isfile(candidate):
                return candidate
        candidate = os.path.join(site_path, path, "index.html")
        if os.path.isfile(candidate):
            return candidate

    return None


def check_sitemap(site_path, domain):
    """检查1: Sitemap有效性"""
    sitemap_path = os.path.join(site_path, "sitemap.xml")
    if not os.path.isfile(sitemap_path):
        return False, "sitemap.xml 文件缺失", "sitemap"

    try:
        tree = ET.parse(sitemap_path)
    except ET.ParseError:
        return False, "sitemap.xml 不是有效XML", "sitemap"

    root = tree.getroot()
    try:
        urls = root.findall(f".//{{{SITEMAP_NS}}}loc")
    except Exception:
        urls = root.findall(".//loc")
    url_count = len(urls)

    if url_count == 0:
        return False, "sitemap.xml 中没有URL", "sitemap"

    # 验证覆盖率: sitemap URL数 >= HTML页数 - noindex页数
    all_html = get_all_html_files(site_path)
    total = len(all_html)
    noindex_count = 0
    for f in all_html:
        content = read_file_content(f)
        if has_noindex(content):
            noindex_count += 1
    expected = total - noindex_count

    # 允许20%偏差: sitemap可能故意排除某些页面
    if url_count < expected * 0.8:
        return False, f"覆盖不足: sitemap {url_count}条 vs 期望{expected} ({total}页-{noindex_count}noindex)", "sitemap_incomplete"

    return True, f"{url_count}条URL ({total}页-{noindex_count}noindex) 匹配", None


def check_robots(site_path, domain):
    """检查2: robots.txt"""
    robots_path = os.path.join(site_path, "robots.txt")
    if not os.path.isfile(robots_path):
        return False, "robots.txt 不存在", "robots"

    content = read_file_content(robots_path)
    expected_line = f"Sitemap: https://{domain}/sitemap.xml"
    if expected_line not in content:
        return False, f"缺少 Sitemap 指向 ({expected_line})", "robots"

    return True, "存在且指向sitemap", None


def check_canonical(site_path):
    """检查3: Canonical标签"""
    all_html = get_all_html_files(site_path)
    if not all_html:
        return False, "没有HTML文件", "canonical"

    # 检查首页
    index_path = os.path.join(site_path, "index.html")
    if os.path.isfile(index_path):
        content = read_file_content(index_path)
        if not re.search(r'<link\s+rel=["\']canonical["\']', content, re.I):
            return False, "首页 index.html 缺少 canonical", "canonical"
    else:
        return False, "首页 index.html 不存在", "canonical"

    # 抽查5个页面
    sample = random.sample(all_html, min(5, len(all_html)))
    missing = []
    for f in sample:
        content = read_file_content(f)
        if not re.search(r'<link\s+rel=["\']canonical["\']', content, re.I):
            rel = os.path.relpath(f, site_path)
            missing.append(rel)

    if missing:
        details = "; ".join(missing[:3])
        return False, f"抽查{len(sample)}页，{len(missing)}页缺canonical: {details}", "canonical"

    checked = min(5, len(all_html))
    return True, f"全部通过 ({checked}/{checked})", None


def check_seo(site_path):
    """检查4: SEO标签 (首页)"""
    index_path = os.path.join(site_path, "index.html")
    if not os.path.isfile(index_path):
        return False, "首页 index.html 不存在", "seo"

    content = read_file_content(index_path)
    issues = []

    title_match = re.search(r"<title>([^<]*)</title>", content, re.I)
    if not title_match or not title_match.group(1).strip():
        issues.append("title缺失或为空")

    desc_match = re.search(
        r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
        content, re.I,
    )
    if not desc_match or not desc_match.group(1).strip():
        issues.append("meta description缺失或为空")

    if not re.search(r'<meta\s+property=["\']og:title["\']', content, re.I):
        issues.append("og:title缺失")
    if not re.search(r'<meta\s+property=["\']og:description["\']', content, re.I):
        issues.append("og:description缺失")
    if not re.search(r'<meta\s+property=["\']og:image["\']', content, re.I):
        issues.append("og:image缺失")

    if issues:
        return False, "; ".join(issues), "seo"

    return True, "title/description/OG 齐全", None


def check_dead_links(site_path):
    """检查5: 死链（仅检查HTML页面间的内部链接）"""
    all_html = get_all_html_files(site_path)
    dead_links = []
    seen = set()

    for f in all_html:
        content = read_file_content(f)
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)
        rel_path = os.path.relpath(f, site_path)
        file_dir = os.path.dirname(f)

        for href in hrefs:
            href = href.strip()

            # 跳过外链和特殊格式
            if (href.startswith("http://") or href.startswith("https://")
                    or href.startswith("//") or href.startswith("#")
                    or href.startswith("mailto:") or href.startswith("tel:")
                    or href.startswith("javascript:")):
                continue

            # 跳过非HTML资源（图片/CSS/JS/favicon等由其他检查覆盖）
            ext = os.path.splitext(href.split("?")[0].split("#")[0])[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
                       ".css", ".js", ".json", ".xml", ".webmanifest", ".woff",
                       ".woff2", ".ttf", ".eot", ".mp4", ".webm", ".pdf"):
                continue
            # 无扩展名且不以/结尾 → 可能指向非HTML文件，跳过
            if not ext and "." in os.path.basename(href.split("?")[0]):
                continue

            if href in seen:
                continue
            seen.add(href)

            filepath = href_to_filepath(href, site_path, file_dir)
            if filepath is None:
                dead_links.append(f"{rel_path} -> {href}")
                if len(dead_links) >= 10:
                    break
        if len(dead_links) >= 10:
            break

    if dead_links:
        detail = "; ".join(dead_links[:5])
        return False, f"{len(dead_links)}个: {detail}", "dead_links"

    return True, "0个", None


def check_bad_images(site_path):
    """检查6: 坏图"""
    all_html = get_all_html_files(site_path)
    bad = []
    seen = set()

    for f in all_html:
        content = read_file_content(f)
        srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        rel_path = os.path.relpath(f, site_path)
        file_dir = os.path.dirname(f)

        for src in srcs:
            src = src.strip()
            if (src.startswith("http://") or src.startswith("https://")
                    or src.startswith("//") or src.startswith("data:")):
                continue

            # 解析路径：相对路径从file_dir解析，绝对路径从site_path解析
            path = src.replace("\\", "/")
            if path.startswith("/"):
                img_path = os.path.join(site_path, path.lstrip("/"))
            else:
                img_path = os.path.normpath(os.path.join(file_dir, path))

            if img_path in seen:
                continue
            seen.add(img_path)

            if not os.path.isfile(img_path):
                bad.append(f"{rel_path} -> {src}")
            elif os.path.getsize(img_path) == 0:
                bad.append(f"{rel_path} -> {src} (空文件)")

            if len(bad) >= 10:
                break
        if len(bad) >= 10:
            break

    if bad:
        detail = "; ".join(bad[:5])
        return False, f"{len(bad)}个: {detail}", "bad_images"

    return True, "0个", None


def check_noindex(site_path, domain):
    """检查7: noindex一致性"""
    all_html = get_all_html_files(site_path)
    sitemap_urls = find_url_files_for_domain(domain, site_path)

    noindex_files = []
    policy_missing_noindex = []

    for f in all_html:
        content = read_file_content(f)
        rel = os.path.relpath(f, site_path).replace("\\", "/")
        basename = os.path.splitext(os.path.basename(f))[0]

        if has_noindex(content):
            noindex_files.append(rel)
        elif basename in POLICY_PAGES:
            policy_missing_noindex.append(rel)

    issues = []

    # 检查noindex页面是否出现在sitemap中
    if sitemap_urls:
        for rel in noindex_files:
            # 将文件路径转为URL路径风格，便于比对
            if rel.endswith("/index.html"):
                url_path = "/" + rel[:-10]  # /path/
            elif rel.endswith(".html"):
                url_path = "/" + rel
            else:
                url_path = "/" + rel

            # 去掉尾部斜杠再比较
            url_path_stripped = url_path.rstrip("/")
            if url_path_stripped in sitemap_urls or url_path in sitemap_urls:
                issues.append(f"noindex页在sitemap中: {rel}")

    # 检查政策类页面是否缺少noindex
    for rel in policy_missing_noindex:
        issues.append(f"政策页缺noindex: {rel}")

    if issues:
        detail = "; ".join(issues[:5])
        return False, f"{len(issues)}项: {detail}", "noindex"

    if noindex_files:
        return True, f"{len(noindex_files)}个页面正确排除", None
    return True, "无noindex页面，跳过检查", None


def check_favicon(site_path):
    """检查8: favicon"""
    png_path = os.path.join(site_path, "favicon.png")
    if os.path.isfile(png_path):
        return True, "存在", None
    ico_path = os.path.join(site_path, "favicon.ico")
    if os.path.isfile(ico_path):
        return True, "存在 (favicon.ico)", None
    return False, "缺失", "favicon"


def check_site(site_dir, domain):
    """对单个站点执行8项审计，返回检查结果列表"""
    site_path = os.path.join(PROJECT_ROOT, site_dir)
    if not os.path.isdir(site_path):
        return None

    checks = [
        ("Sitemap", check_sitemap(site_path, domain)),
        ("robots.txt", check_robots(site_path, domain)),
        ("Canonical", check_canonical(site_path)),
        ("SEO标签", check_seo(site_path)),
        ("死链", check_dead_links(site_path)),
        ("坏图", check_bad_images(site_path)),
        ("noindex", check_noindex(site_path, domain)),
        ("favicon", check_favicon(site_path)),
    ]

    return checks


def check_all_sites():
    """审计所有站点，输出逐站结果和汇总"""
    all_sites = load_sites()
    print("=" * 60)
    print("前置审计: 检查所有站点质量")
    print("=" * 60)

    summary = []
    total_checks = 8

    for s in all_sites:
        site_dir = s["dir"]
        domain = s["domain"]
        print(f"\n=== {site_dir} ({domain}) ===")
        sys.stdout.flush()

        checks = check_site(site_dir, domain)
        if checks is None:
            print(f"  [目录不存在: {site_dir}]")
            summary.append((domain, "DIR_MISSING", 0, []))
            continue

        passed = 0
        blocked = False
        all_messages = []

        for name, (ok, msg, block_key) in checks:
            icon = "OK" if ok else "FAIL"
            if ok:
                passed += 1
                print(f"  [{icon}] {name}: {msg}")
                all_messages.append(f"[{icon}] {name}: {msg}")
            else:
                level = BLOCK_RULES.get(block_key, "BLOCK")
                if level == "BLOCK":
                    blocked = True
                print(f"  [{icon}] {name}: {msg} [{level}]")
                all_messages.append(f"[{icon}] {name}: {msg} [{level}]")

        status_label = "BLOCKED" if blocked else "PASS"
        result_line = f"结果: {passed}/{total_checks} 通过 - {status_label}"
        print(f"---\n{result_line}")
        summary.append((domain, status_label, passed, all_messages))

    # 汇总
    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    passed_sites = [s for s in summary if s[1] == "PASS"]
    blocked_sites = [s for s in summary if s[1] == "BLOCKED"]
    missing_sites = [s for s in summary if s[1] == "DIR_MISSING"]

    print(f"通过: {len(passed_sites)}站")
    print(f"阻塞: {len(blocked_sites)}站")
    if missing_sites:
        print(f"目录缺失: {len(missing_sites)}站")

    if blocked_sites:
        print("\n阻塞站点清单:")
        for domain, status, score, messages in blocked_sites:
            print(f"  - {domain} ({score}/{total_checks})")
            for m in messages:
                print(f"    {m}")

    if missing_sites:
        print(f"\n目录缺失站点:")
        for domain, *_ in missing_sites:
            print(f"  - {domain}")

    print()
    return len(blocked_sites) == 0 and len(missing_sites) == 0


# ─── 入口 ──────────────────────────────────────────────

def main():
    args = set(sys.argv[1:])

    if "--status" in args:
        status()
        return
    if "--check" in args:
        check_all_sites()
        return
    if "--sync" in args:
        sync_sites()
        return
    if "--sitemap" in args:
        submit_sitemaps()
        return
    if "--force" in args:
        sync_sites()
        print()
        submit_sitemaps()
        return

    # 默认流程: check → sync → sitemap
    all_ok = check_all_sites()
    if not all_ok:
        print("部分站点审计未通过，使用 --force 跳过检查直接提交。")
        sys.exit(1)

    print()
    sync_sites()
    print()
    submit_sitemaps()


if __name__ == "__main__":
    main()
