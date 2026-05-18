"""
定时任务 —— 内容收集 → BUG修复 → 站点扩展 → 深度审计
模式:
  --mode light  (默认/PC在线)  仅热点侦察 + 广告监控
  --mode full   (PC离线)       全量四阶段
日志: logs/nightly.log  状态: logs/nightly_state.json
"""
import subprocess, json, os, sys, re, hashlib, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "shared" / "game_site_data.json"
ANIME_DATA_FILE = ROOT / "shared" / "anime_site_data.json"
STATE_FILE = ROOT / "logs" / "nightly_state.json"
LOG_FILE = ROOT / "logs" / "nightly.log"

CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
GA4_ID = "G-GGNWR1X1GV"
ADSENSE_PUB = "ca-pub-2595917642864488"

# 图片最低标准
MIN_IMAGE_SIZE = 10000   # 10KB 最低
MIN_IMAGE_QUALITY = 100000  # 100KB 以上优先（非缩略图）

# ============================================================
# 工具函数
# ============================================================

def log(msg):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    os.makedirs(LOG_FILE.parent, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"last_run": None, "image_downloads": {}, "bug_fixes_applied": 0, "sites_deployed": [], "errors": []}

def save_state(state):
    state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def load_json(path):
    if Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {}

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ============================================================
# 阶段一：内容收集
# ============================================================

def build_image_targets():
    """从JSON数据动态生成所有站点的图片下载目标（不再硬编码）"""
    targets = {}

    # 游戏站
    game_data = load_json(DATA_FILE)
    for site_key, site_info in game_data.items():
        if not isinstance(site_info, dict):
            continue
        chars = site_info.get("characters", [])
        if not chars:
            continue
        site_dir = ROOT / f"{site_key}-site"
        if not site_dir.exists():
            continue
        targets[site_key] = {
            "characters": [
                {
                    "name": c.get("name", "").lower().replace(" ", "_"),
                    "display_name": c.get("name", ""),
                    "keywords": [f"{c.get('name','')} render png transparent",
                                 f"{c.get('name','')} {site_key} png"]
                }
                for c in chars if c.get("image") in (None, "", "__missing__")
            ],
            "image_dir": site_dir / "images"
        }

    # 动漫站
    anime_data = load_json(ANIME_DATA_FILE)
    for site_key, site_info in anime_data.items():
        if not isinstance(site_info, dict):
            continue
        chars = site_info.get("characters", [])
        if not chars:
            continue
        site_dir = ROOT / f"{site_key}-site"
        if not site_dir.exists():
            continue
        targets[site_key] = {
            "characters": [
                {
                    "name": c.get("name", "").lower().replace(" ", "_"),
                    "display_name": c.get("name", ""),
                    "keywords": [f"{c.get('name','')} render png transparent",
                                 f"{c.get('name','')} {site_key} anime png"]
                }
                for c in chars if c.get("image") in (None, "", "__missing__")
            ],
            "image_dir": site_dir / "images"
        }

    return targets

def verify_png(filepath):
    """验证文件是有效PNG且大小合理"""
    if not os.path.exists(filepath):
        return False
    size = os.path.getsize(filepath)
    if size < MIN_IMAGE_SIZE:
        return False
    with open(filepath, "rb") as f:
        header = f.read(8)
    return header[:4] == b'\x89PNG' and header[4:8] == b'\r\n\x1a\n'

def md5_dedup_dir(img_dir):
    """目录内MD5去重，删除重复文件，返回删除数量"""
    hashes = {}
    removed = 0
    if not os.path.exists(img_dir):
        return 0
    for f in sorted(Path(img_dir).glob("*.png")):
        md5 = hashlib.md5(open(f, "rb").read()).hexdigest()
        if md5 in hashes:
            f.unlink()
            removed += 1
        else:
            hashes[md5] = str(f)
    return removed

def pngwing_search(keyword, session):
    """搜索pngwing，返回图片详情页URL列表"""
    try:
        url = f"https://www.pngwing.com/search?q={keyword.replace(' ', '+')}"
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        links = re.findall(r'href="(/en/free-png-[a-z0-9-]+)"', r.text)
        return list(set(f"https://www.pngwing.com{l}" for l in links))[:5]
    except:
        return []

def pngwing_download_from_detail(detail_url, session, dest_path):
    """从pngwing详情页下载原图（非缩略图）"""
    try:
        r = session.get(detail_url, timeout=20)
        if r.status_code != 200:
            return False
        download_match = re.search(
            r'href="(/en/free-png-[^"]+/download\?width=\d+)"', r.text
        )
        if not download_match:
            download_match = re.search(
                r'src="(https://[^"]*pngwing[^"]*\.(?:png|PNG)[^"]*)"', r.text
            )
            if not download_match:
                return False
        img_url = download_match.group(1)
        if not img_url.startswith("http"):
            img_url = "https://www.pngwing.com" + img_url
        r2 = session.get(img_url, timeout=30, allow_redirects=True)
        if r2.status_code == 200 and len(r2.content) > MIN_IMAGE_QUALITY:
            with open(dest_path, "wb") as f:
                f.write(r2.content)
            return verify_png(dest_path)
    except:
        pass
    return False

def try_download_pngegg(keywords, dest_path):
    """pngegg 防爬严格，供未来实现"""
    return False

def try_download_direct(session, url, dest_path):
    """直接下载URL，验证PNG"""
    try:
        r = session.get(url, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > MIN_IMAGE_SIZE:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            if verify_png(dest_path):
                return True
            else:
                os.remove(dest_path)
    except:
        pass
    return False

def try_download_character(session, target_name, keywords, dest_dir, display_name=""):
    """多策略下载角色图（image-pipeline逻辑）"""
    os.makedirs(dest_dir, exist_ok=True)
    slug = display_name.lower().replace(" ", "_") if display_name else target_name
    dest = os.path.join(dest_dir, f"{slug}.png")

    if verify_png(dest) and os.path.getsize(dest) > MIN_IMAGE_QUALITY:
        return "already_ok"

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    })

    # 策略1: pngimg.com
    clean_name = target_name.replace("_", "-")
    if try_download_direct(session, f"https://pngimg.com/uploads/{clean_name}/{clean_name}_PNG.png", dest):
        log(f"  ✓ {target_name}.png ({os.path.getsize(dest)//1024}KB) 来源: pngimg")
        return "downloaded"

    # 策略2: pngwing 搜索→详情页→原图下载
    for kw in keywords[:3]:
        for durl in pngwing_search(kw, session):
            if pngwing_download_from_detail(durl, session, dest):
                log(f"  ✓ {target_name}.png ({os.path.getsize(dest)//1024}KB) 来源: pngwing")
                return "downloaded"
            time.sleep(1.5)

    return "all_failed"

def update_character_image_in_json(site_key, char_name, img_filename, is_anime=False):
    """下载成功后更新JSON中角色的image字段"""
    data_file = ANIME_DATA_FILE if is_anime else DATA_FILE
    data = load_json(data_file)
    if site_key not in data:
        return False
    chars = data[site_key].get("characters", [])
    for c in chars:
        if c.get("name", "").lower() == char_name.lower().replace("_", " "):
            c["image"] = img_filename
            save_json(data_file, data)
            return True
    return False

def download_all_images(state):
    """下载所有站点缺失的角色图（动态从JSON读取，不硬编码）"""
    log("=" * 40)
    log("阶段一：内容收集 —— 角色图下载（image-pipeline）")
    log("=" * 40)

    try:
        import requests
    except ImportError:
        log("✗ requests 库未安装，跳过图片下载")
        return False, {}

    session = requests.Session()
    changed = False
    stats = {"downloaded": 0, "already_ok": 0, "failed": 0, "dedup_removed": 0}

    targets = build_image_targets()
    for site_key, config in targets.items():
        img_dir = config["image_dir"]
        os.makedirs(img_dir, exist_ok=True)

        if site_key not in state["image_downloads"]:
            state["image_downloads"][site_key] = {}

        for char in config["characters"]:
            name = char["name"]
            display = char.get("display_name", name)
            prev = state["image_downloads"][site_key].get(name, "pending")

            if prev == "success":
                dest = os.path.join(img_dir, f"{name}.png")
                if verify_png(dest) and os.path.getsize(dest) > MIN_IMAGE_QUALITY:
                    stats["already_ok"] += 1
                    continue
                state["image_downloads"][site_key][name] = "pending"

            log(f"  下载: {site_key}/{display}...")
            result = try_download_character(
                session, name, char["keywords"], img_dir, display
            )
            state["image_downloads"][site_key][name] = result
            if result == "downloaded":
                changed = True
                stats["downloaded"] += 1
                # 更新JSON中的image字段
                slug = display.lower().replace(" ", "_")
                is_anime = site_key in load_json(ANIME_DATA_FILE)
                update_character_image_in_json(site_key, display, f"{slug}.png", is_anime)
            elif result == "already_ok":
                stats["already_ok"] += 1
            else:
                stats["failed"] += 1

        # MD5去重
        removed = md5_dedup_dir(img_dir)
        if removed > 0:
            stats["dedup_removed"] += removed
            log(f"  {site_key}: MD5去重删除 {removed} 张重复图片")
            changed = True

    log(f"  统计: 新下载{stats['downloaded']} 已存在{stats['already_ok']} 失败{stats['failed']} 去重删除{stats['dedup_removed']}")
    return changed, stats

# ============================================================
# 阶段二：BUG 修复
# ============================================================

AUTO_FIXES = {
    # 死链接替换
    'href="#"': 'href="/"',
    "href='#'": "href='/'",
    # 死图域名替换
    "picsum.photos": "images/placeholder.svg",
    "source.unsplash.com": "images/placeholder.svg",
    # AI陈词滥调 -> 更自然的表达（保留原意）
    "delve into": "explore",
    "in the ever-evolving landscape": "in this field",
    "game-changer": "major shift",
    "revolutionize": "transform",
    "cutting-edge": "advanced",
    "state-of-the-art": "top-tier",
    "unleash the power": "use the full potential",
    "elevate your": "improve your",
    "in this comprehensive guide": "in this guide",
    "without further ado": "",
}

def fix_bugs_in_file(filepath):
    """对单个HTML文件执行自动修复"""
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except:
        return 0

    original = content
    fixes = 0

    for old, new in AUTO_FIXES.items():
        if old in content:
            content = content.replace(old, new)
            fixes += 1

    # 移除表情符号
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF☀-⛿✀-➿]"
    )
    new_content = emoji_pattern.sub("", content)
    if new_content != content:
        fixes += 1
        content = new_content

    # 补全缺失的 google-adsense-account meta
    if 'google-adsense-account' not in content and '<meta' in content:
        ad_meta = f'<meta name="google-adsense-account" content="{ADSENSE_PUB}">'
        content = content.replace('<meta charset="UTF-8">',
                                  '<meta charset="UTF-8">\n    ' + ad_meta)
        fixes += 1

    if content != original:
        Path(filepath).write_text(content, encoding="utf-8")
        return fixes

    return 0

def scan_and_fix_all_sites():
    """扫描所有站点HTML，执行自动修复"""
    log("=" * 40)
    log("阶段二：BUG 修复")
    log("=" * 40)

    total_fixes = 0

    # 遍历所有站点目录
    site_dirs = []
    for d in ROOT.iterdir():
        if d.is_dir() and (d.name.endswith("-site") or d.name.startswith("sub-")):
            site_dirs.append(d)

    for site_dir in sorted(site_dirs):
        site_fixes = 0
        for html_file in site_dir.glob("**/*.html"):
            fixes = fix_bugs_in_file(html_file)
            if fixes > 0:
                site_fixes += fixes
                log(f"  修复: {html_file.relative_to(ROOT)} — {fixes}处")

        if site_fixes > 0:
            total_fixes += site_fixes
            log(f"  {site_dir.name}: {site_fixes}处修复")

    if total_fixes == 0:
        log("  无需修复，全部干净")

    link_result = subprocess.run(
        [sys.executable, str(ROOT / "shared" / "link_check.py")],
        capture_output=True, text=True, cwd=str(ROOT), timeout=60
    )
    log(f"  链接审计: {link_result.stdout.strip()[-300:]}")

    return total_fixes

# ============================================================
# 阶段三：站点扩展
# ============================================================

def update_data_from_images():
    """根据已下载图片更新 game_site_data.json"""
    data = load_json(DATA_FILE)
    if not data:
        return False

    updated = False

    for game_key, config in IMAGE_TARGETS.items():
        if game_key not in data:
            continue

        img_dir = config["image_dir"]
        existing_chars = data[game_key].get("characters", [])

        for char_def in config["characters"]:
            char_name = char_def["name"]
            img_path = img_dir / f"{char_name}.png"

            if verify_png(str(img_path)):
                # 检查是否已在characters列表
                already_exists = any(
                    c.get("image", "").startswith(char_name)
                    for c in existing_chars
                )
                if not already_exists:
                    log(f"  新角色图: {game_key}/{char_name}.png，需手动补充角色数据")
                    updated = True

    if updated:
        save_json(DATA_FILE, data)

    return updated

def check_site_quality(site_dir):
    """内容完整性检查。返回问题列表，空列表=通过"""
    site_path = ROOT / site_dir
    issues = []

    for html_file in site_path.glob("**/*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")

        # 检查占位图/死图源
        if "picsum.photos" in content:
            issues.append(f"{html_file.name}: 含 picsum.photos 占位图")

        # 检查空 src
        if 'src=""' in content or "src=''" in content:
            issues.append(f"{html_file.name}: 含空白src图片")

        # 检查重复banner图 (同一页面内相同src出现多次)
        import re
        img_srcs = re.findall(r'src="([^"]*\.(?:png|jpg|jpeg|webp|svg))"', content)
        if len(img_srcs) > len(set(img_srcs)):
            duplicates = [s for s in img_srcs if img_srcs.count(s) > 1]
            if duplicates:
                issues.append(f"{html_file.name}: 重复图片 {duplicates[0][:60]}")

        # 检查英雄区/banner 图片
        has_hero = bool(re.search(r'<header[^>]*>|<div[^>]*class="[^"]*hero[^"]*"|<div[^>]*class="[^"]*banner[^"]*"', content))
        if has_hero:
            hero_has_img = bool(re.search(
                r'(?:hero|banner).*?<img[^>]+src="(?!data:)[^"]+',
                content, re.DOTALL
            ))
            if not hero_has_img:
                issues.append(f"{html_file.name}: banner/hero区缺图片")

    return issues


def verify_live_site(project, site_dir):
    """部署后线上验证。返回问题列表，空列表=通过"""
    issues = []
    try:
        import urllib.request
        import urllib.error

        url = f"https://{project}.pages.dev"
        req = urllib.request.Request(url, headers={"User-Agent": "NightlyWorker/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)

        if resp.status != 200:
            issues.append(f"HTTP {resp.status}")
            return issues

        html = resp.read().decode("utf-8", errors="ignore")

        # 必需meta标签
        if "google-adsense-account" not in html:
            issues.append("缺少 google-adsense-account meta")
        if "charset" not in html.lower():
            issues.append("缺少 charset meta")

        # 空图片src
        if 'src=""' in html or "src=''" in html:
            issues.append("含空白src图片")

        # 占位图
        if "picsum.photos" in html:
            issues.append("含 picsum.photos 占位图")

        # 空链接href
        if 'href="#"' in html:
            issues.append("含 href=# 空链接")

        # 首页导航检查
        if "<nav" not in html and 'class="nav' not in html.lower():
            issues.append("可能缺少导航栏")

    except urllib.error.HTTPError as e:
        issues.append(f"HTTP {e.code}")
    except Exception as e:
        issues.append(f"验证异常: {str(e)[:100]}")

    return issues


def render_and_deploy(state):
    """重新渲染有变化的站点并部署"""
    log("=" * 40)
    log("阶段三：站点扩展 —— 渲染+部署")
    log("=" * 40)

    # 运行渲染
    render_script = ROOT / "shared" / "render_game_site.py"
    if not render_script.exists():
        log("  render_game_site.py 不存在，跳过渲染")
        return

    result = subprocess.run(
        [sys.executable, str(render_script), "--all"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=120
    )
    log(f"  渲染输出: {result.stdout.strip()[-200:]}")

    if result.returncode != 0:
        log(f"  渲染错误: {result.stderr.strip()[-300:]}")
        return

    # 检查哪些站点被修改（git diff）
    changed = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    changed_files = changed.stdout.strip().split("\n") if changed.stdout.strip() else []
    changed_sites = set()
    for f in changed_files:
        parts = Path(f).parts
        if parts:
            d = parts[0]
            if d.endswith("-site") or d.startswith("sub-"):
                changed_sites.add(d)

    # 也检查 untracked 文件
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    for f in (untracked.stdout.strip().split("\n") if untracked.stdout.strip() else []):
        parts = Path(f).parts
        if parts:
            d = parts[0]
            if d.endswith("-site") or d.startswith("sub-"):
                changed_sites.add(d)

    if not changed_sites:
        log("  无站点变更，跳过部署")
        return

    log(f"  变更站点: {', '.join(sorted(changed_sites))}")

    if not CF_TOKEN:
        log("  CLOUDFLARE_API_TOKEN 未设置，跳过部署")
        return

    # 站点→项目名映射
    PROJECT_MAP = {
        "minecraft-site": "minecraft-jycsd", "fortnite-site": "fortnite-jycsd",
        "valorant-site": "valorant-jycsd", "eldenring-site": "eldenring-jycsd",
        "lol-site": "lol-jycsd", "dragonball-site": "dragonball-jycsd",
        "onepiece-site": "onepiece-jycsd", "naruto-site": "naruto-jycsd",
        "anime-site": "anime-jycsd", "games-site": "games-jycsd",
        "sub-healthy": "healthy-jycsd", "sub-pets": "pets-jycsd",
        "sub-home": "home-jycsd", "sub-finance": "finance-jycsd",
        "sub-tech": "tech-jycsd", "sub-travel": "travel-jycsd",
        "main-site": "main-site",
    }

    deployed = []
    for site_dir in sorted(changed_sites):
        project = PROJECT_MAP.get(site_dir)
        if not project:
            log(f"  跳过 {site_dir}: 无对应项目名")
            continue

        # 内容质量门禁
        quality_issues = check_site_quality(site_dir)
        if quality_issues:
            log(f"  {site_dir} 质量不达标，跳过部署:")
            for issue in quality_issues:
                log(f"    - {issue}")
            continue

        # 部署前审计
        audit_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "pre_commit_audit.py"), site_dir],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60
        )
        if "FAIL" in audit_result.stdout:
            log(f"  {site_dir} 审计不通过，跳过部署")
            log(f"    {audit_result.stdout.strip()[-200:]}")
            continue

        log(f"  部署: {site_dir} → {project}...")
        result = subprocess.run(
            ["npx", "wrangler", "pages", "deploy", site_dir,
             "--project-name", project, "--commit-dirty=true"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=120,
            env={**os.environ, "CLOUDFLARE_API_TOKEN": CF_TOKEN}
        )

        if "Deployment complete" in result.stdout:
            log(f"    ✓ 部署完成: {project}")
            # 线上验证
            time.sleep(3)  # CF CDN propagation
            live_issues = verify_live_site(project, site_dir)
            if live_issues:
                log(f"    ⚠ 线上验证发现问题:")
                for issue in live_issues:
                    log(f"      - {issue}")
            else:
                log(f"    ✓ 线上验证通过")
            deployed.append(site_dir)
        else:
            err = result.stderr.strip()[-200:]
            log(f"    ✗ 部署失败: {err}")

    state["sites_deployed"] = deployed
    log(f"  共部署 {len(deployed)} 个站点")

# ============================================================
# 阶段四：深度审计（site-auditor逻辑）
# ============================================================

def deep_audit_site(site_dir):
    """全站深度审计，返回问题列表（site-auditor Agent逻辑）"""
    site_path = ROOT / site_dir
    if not site_path.exists():
        return [f"{site_dir}: 目录不存在"]
    issues = []
    html_files = list(site_path.glob("**/*.html"))
    if not html_files:
        issues.append(f"{site_dir}: 无HTML文件")
        return issues

    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8", errors="ignore")
        except:
            issues.append(f"{html_file.name}: 无法读取")
            continue
        rel = html_file.relative_to(ROOT)

        # 内部链接检查
        for m in re.finditer(r'href="(\.\.?/[^"]+\.html[^"]*)"', content):
            target = (html_file.parent / m.group(1)).resolve()
            if not target.exists():
                issues.append(f"{rel}: 死链 → {m.group(1)}")

        # 空链接
        if 'href="#"' in content:
            issues.append(f"{rel}: 含href=#")

        # 图片检查
        for m in re.finditer(r'src="([^"]+\.(?:png|jpg|jpeg|webp|svg))"', content):
            src = m.group(1)
            if src.startswith("http"):
                continue
            img_path = html_file.parent / src
            if not img_path.exists():
                issues.append(f"{rel}: 缺图 → {src}")
            elif img_path.stat().st_size < 1000:
                issues.append(f"{rel}: 图片过小 → {src}")

        # 占位图
        if "picsum.photos" in content:
            issues.append(f"{rel}: 含picsum.photos")

        # 必需meta
        if "google-adsense-account" not in content:
            issues.append(f"{rel}: 缺google-adsense-account meta")

        # 空title
        if "<title></title>" in content or "<title>" not in content:
            issues.append(f"{rel}: title缺失或为空")

    # 搜索索引检查
    search_index = site_path / "search-index.json"
    if not search_index.exists():
        issues.append(f"{site_dir}: 缺search-index.json")
    else:
        try:
            si = json.loads(search_index.read_text(encoding="utf-8"))
            si_entries = len(si) if isinstance(si, list) else len(si.get("entries", []))
            if si_entries < len(html_files) * 0.5:
                issues.append(f"{site_dir}: search-index条目({si_entries})远少于HTML({len(html_files)})")
        except:
            issues.append(f"{site_dir}: search-index.json格式错误")

    # robots.txt
    if not (site_path / "robots.txt").exists():
        issues.append(f"{site_dir}: 缺robots.txt")

    # sitemap.xml + 条目一致性
    sitemap = site_path / "sitemap.xml"
    if sitemap.exists():
        sitemap_content = sitemap.read_text(encoding="utf-8", errors="ignore")
        url_count = len(re.findall(r"<url>", sitemap_content))
        if url_count < len(html_files) * 0.8:
            issues.append(f"{site_dir}: sitemap条目({url_count})少于HTML({len(html_files)})")
    else:
        issues.append(f"{site_dir}: 缺sitemap.xml")

    return issues

def deep_audit_all_sites():
    """对所有站点执行深度审计"""
    log("=" * 40)
    log("阶段四：深度审计（site-auditor）")
    log("=" * 40)

    all_issues = {}
    site_dirs = [d.name for d in ROOT.iterdir()
                 if d.is_dir() and (d.name.endswith("-site") or d.name.startswith("sub-"))]

    for site_dir in sorted(site_dirs):
        issues = deep_audit_site(site_dir)
        if issues:
            all_issues[site_dir] = issues
            log(f"  {site_dir}: {len(issues)}个问题")
            for issue in issues[:5]:
                log(f"    - {issue}")
            if len(issues) > 5:
                log(f"    ... 还有{len(issues)-5}个")
        else:
            log(f"  {site_dir}: ✓ 无问题")

    total = sum(len(v) for v in all_issues.values())
    log(f"  总问题数: {total}")
    return all_issues

# ============================================================
# 日报生成
# ============================================================

def generate_daily_report(stats, audit_issues, errors, state):
    """生成服务器工作日報"""
    report_path = ROOT / "logs" / "daily_report.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"# 服务器工作日报",
        f"**生成时间:** {now}",
        f"",
        f"## 阶段一：图片下载",
        f"- 新增下载: {stats.get('downloaded', 0)}",
        f"- 已存在: {stats.get('already_ok', 0)}",
        f"- 失败: {stats.get('failed', 0)}",
        f"- MD5去重删除: {stats.get('dedup_removed', 0)}",
        f"",
        f"## 阶段二：BUG修复",
        f"- 自动修复数: {state.get('bug_fixes_applied', 0)}",
        f"",
        f"## 阶段三：站点部署",
        f"- 部署站点: {', '.join(state.get('sites_deployed', [])) or '无'}",
        f"",
        f"## 阶段四：深度审计",
    ]

    total_issues = sum(len(v) for v in audit_issues.values())
    if total_issues > 0:
        lines.append(f"- **总问题数: {total_issues}**")
        for site, issues in audit_issues.items():
            lines.append(f"  - {site}: {len(issues)}个问题")
    else:
        lines.append(f"- ✓ 所有站点无问题")
    lines.append("")

    if errors:
        lines.append(f"## 错误")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    lines.append(f"## 状态文件")
    lines.append(f"- 最后运行: {state.get('last_run', 'N/A')}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"日报已生成: {report_path}")

# ============================================================
# 主流程
# ============================================================

def run_light():
    """轻量模式：仅热点侦察 + 广告监控"""
    log("Light mode — 热点侦察 + 广告监控")

    try:
        trend_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "trend_scout.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=180
        )
        log(f"  热点侦察: {trend_result.stdout.strip()[-500:]}")
        if trend_result.returncode != 0:
            log(f"  热点侦察stderr: {trend_result.stderr.strip()[-300:]}")
    except Exception as e:
        log(f"  trend_scout 失败: {e}")

    try:
        ad_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "ad_monitor.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60
        )
        log(f"  广告报告: {ad_result.stdout.strip()[-300:]}")
    except Exception as e:
        log(f"  ad_monitor 跳过: {e}")

def run_full():
    """全量模式：四阶段 + 日报"""
    state = load_state()
    errors = []
    img_stats = {"downloaded": 0, "already_ok": 0, "failed": 0, "dedup_removed": 0}
    audit_issues = {}
    fixes_count = 0

    # 阶段一：内容收集（image-pipeline）
    try:
        images_changed, img_stats = download_all_images(state)
    except Exception as e:
        log(f"阶段一失败: {e}")
        errors.append(f"阶段一: {e}")
        images_changed = False

    # 热点侦察
    try:
        trend_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "trend_scout.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=180
        )
        log(f"  热点侦察: {trend_result.stdout.strip()[-500:]}")
    except Exception as e:
        log(f"  trend_scout 失败: {e}")

    # 阶段二：BUG修复
    try:
        fixes_count = scan_and_fix_all_sites()
        state["bug_fixes_applied"] += fixes_count
    except Exception as e:
        log(f"阶段二失败: {e}")
        errors.append(f"阶段二: {e}")

    # 广告收益监控
    try:
        ad_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "ad_monitor.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60
        )
        log(f"  广告报告: {ad_result.stdout.strip()[-300:]}")
    except:
        pass

    # 阶段三：站点扩展（仅新内容触发）
    try:
        if images_changed:
            update_data_from_images()
            render_and_deploy(state)
        else:
            log("阶段三：无新内容，跳过渲染部署")
    except Exception as e:
        log(f"阶段三失败: {e}")
        errors.append(f"阶段三: {e}")

    # 阶段四：深度审计（site-auditor）
    try:
        audit_issues = deep_audit_all_sites()
    except Exception as e:
        log(f"阶段四失败: {e}")
        errors.append(f"阶段四: {e}")

    # 生成日报
    state["errors"] = errors
    save_state(state)
    generate_daily_report(img_stats, audit_issues, errors, state)

    log(f"全量完成。下载:{img_stats['downloaded']} 修复:{fixes_count} 部署:{len(state.get('sites_deployed',[]))} 审计:{sum(len(v) for v in audit_issues.values())} 错误:{len(errors)}")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--mode"
    # 支持 --mode light / --mode full 或简写 light / full
    if "full" in mode:
        mode = "full"
    else:
        mode = "light"

    os.makedirs(ROOT / "logs", exist_ok=True)
    log("=" * 60)
    log(f"Nightly Worker 启动 — {mode.upper()} 模式")
    log("=" * 60)

    if mode == "full":
        run_full()
    else:
        run_light()

    log("=" * 60)
    log(f"Nightly Worker 完成")
    log("=" * 60)

if __name__ == "__main__":
    main()
