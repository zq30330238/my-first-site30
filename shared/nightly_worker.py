"""
每日 22:30 定时任务 —— 内容收集 → BUG修复 → 站点扩展
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

IMAGE_TARGETS = {
    "fortnite": {
        "characters": [
            {"name": "jonesy", "keywords": ["fortnite jonesy render png transparent", "fortnite jonesy the first png"]},
            {"name": "raven", "keywords": ["fortnite raven skin render png", "fortnite raven outfit png"]},
            {"name": "lynx", "keywords": ["fortnite lynx skin render png", "fortnite lynx outfit transparent"]},
            {"name": "peely", "keywords": ["fortnite peely render png", "fortnite peely banana png"]},
        ],
        "image_dir": ROOT / "fortnite-site" / "images"
    },
    "eldenring": {
        "characters": [
            {"name": "malenia", "keywords": ["elden ring malenia render png", "malenia blade of miquella png"]},
            {"name": "ranni", "keywords": ["elden ring ranni render png", "ranni the witch png transparent"]},
            {"name": "radahn", "keywords": ["elden ring radahn render png", "starscourge radahn png"]},
            {"name": "melina", "keywords": ["elden ring melina render png", "melina kindling maiden png"]},
        ],
        "image_dir": ROOT / "eldenring-site" / "images"
    },
    "dragonball": {
        "characters": [
            {"name": "goku", "keywords": ["goku render png transparent", "dragon ball goku ultra instinct png"]},
            {"name": "vegeta", "keywords": ["vegeta render png transparent", "dragon ball vegeta ultra ego png"]},
            {"name": "gohan", "keywords": ["gohan beast render png", "dragon ball gohan png transparent"]},
            {"name": "piccolo", "keywords": ["piccolo render png", "dragon ball piccolo orange png"]},
        ],
        "image_dir": ROOT / "dragonball-site" / "images"
    },
    "onepiece": {
        "characters": [
            {"name": "luffy", "keywords": ["luffy gear 5 render png", "one piece luffy nika png transparent"]},
            {"name": "zoro", "keywords": ["zoro render png", "one piece roronoa zoro png transparent"]},
            {"name": "nami", "keywords": ["nami render png", "one piece nami png transparent"]},
            {"name": "sanji", "keywords": ["sanji render png", "one piece sanji png transparent"]},
        ],
        "image_dir": ROOT / "onepiece-site" / "images"
    },
    "naruto": {
        "characters": [
            {"name": "naruto", "keywords": ["naruto baryon mode render png", "naruto uzumaki png transparent"]},
            {"name": "sasuke", "keywords": ["sasuke render png", "sasuke uchiha png transparent"]},
            {"name": "sakura", "keywords": ["sakura render png", "sakura haruno png transparent"]},
            {"name": "kakashi", "keywords": ["kakashi render png", "kakashi hatake png transparent"]},
        ],
        "image_dir": ROOT / "naruto-site" / "images"
    },
}

def verify_png(filepath):
    """验证文件是有效PNG且大小合理"""
    if not os.path.exists(filepath):
        return False
    size = os.path.getsize(filepath)
    if size < 10000:
        return False
    with open(filepath, "rb") as f:
        header = f.read(8)
    return header[:4] == b'\x89PNG' and header[4:8] == b'\r\n\x1a\n'

def try_download_pngegg(keywords, dest_path):
    """从 pngegg.com 搜索并下载（通过Google图片间接获取）"""
    # pngegg 有严格的防爬，此方法供未来实现
    return False

def try_download_direct(session, url, dest_path):
    """直接下载URL，验证PNG"""
    try:
        r = session.get(url, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 10000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            if verify_png(dest_path):
                return True
            else:
                os.remove(dest_path)
    except:
        pass
    return False

def try_download_character(session, target_name, keywords, dest_dir):
    """尝试多种URL模式下载角色图"""
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{target_name}.png")

    # 如果已有且有效，跳过
    if verify_png(dest):
        return "already_ok"

    # URL 模式列表（按优先级）
    patterns = []

    # 模式1: pngimg.com 直接URL
    clean_name = target_name.replace("_", "-")
    patterns.append(f"https://pngimg.com/uploads/{clean_name}/{clean_name}_PNG.png")

    # 模式2: 尝试 pngegg 搜索页（需要解析HTML，暂用简单模式）
    # patterns are constructed below per game

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    })

    for pattern in patterns:
        if try_download_direct(session, pattern, dest):
            size_kb = os.path.getsize(dest) // 1024
            log(f"  ✓ {target_name}.png ({size_kb}KB) 来源: {pattern[:60]}")
            return "downloaded"

    return "all_failed"

def download_all_images(state):
    """下载所有缺失的角色图"""
    log("=" * 40)
    log("阶段一：内容收集 —— 角色图下载")
    log("=" * 40)

    try:
        import requests
    except ImportError:
        log("✗ requests 库未安装，跳过图片下载")
        return

    session = requests.Session()
    changed = False

    for game_key, config in IMAGE_TARGETS.items():
        img_dir = config["image_dir"]
        os.makedirs(img_dir, exist_ok=True)

        if game_key not in state["image_downloads"]:
            state["image_downloads"][game_key] = {}

        for char in config["characters"]:
            name = char["name"]
            prev_status = state["image_downloads"][game_key].get(name, "pending")

            # 已有成功记录且文件有效，跳过
            if prev_status == "success":
                dest = os.path.join(img_dir, f"{name}.png")
                if verify_png(dest):
                    continue
                else:
                    state["image_downloads"][game_key][name] = "pending"

            log(f"下载: {game_key}/{name}...")
            result = try_download_character(session, name, char["keywords"], img_dir)
            state["image_downloads"][game_key][name] = result
            if result in ("downloaded", "already_ok"):
                changed = True

    if changed:
        log("图片有更新，标记需要重新渲染")
    else:
        log("无新图片下载成功")

    return changed

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

        log(f"  部署: {site_dir} → {project}...")
        result = subprocess.run(
            ["npx", "wrangler", "pages", "deploy", site_dir,
             "--project-name", project, "--commit-dirty=true"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=120,
            env={**os.environ, "CLOUDFLARE_API_TOKEN": CF_TOKEN}
        )

        if "Deployment complete" in result.stdout:
            log(f"    ✓ 部署成功: {project}")
            deployed.append(site_dir)
        else:
            err = result.stderr.strip()[-200:]
            log(f"    ✗ 部署失败: {err}")

    state["sites_deployed"] = deployed
    log(f"  共部署 {len(deployed)} 个站点")

# ============================================================
# 主流程
# ============================================================

def main():
    os.makedirs(ROOT / "logs", exist_ok=True)
    log("=" * 60)
    log("Nightly Worker 启动")
    log("=" * 60)

    state = load_state()
    errors = []

    # 阶段一：内容收集
    try:
        images_changed = download_all_images(state)
    except Exception as e:
        log(f"✗ 阶段一失败: {e}")
        errors.append(f"阶段一: {e}")
        images_changed = False

    # 阶段一b：热点侦察
    try:
        trend_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "trend_scout.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=180
        )
        log(f"  热点侦察: {trend_result.stdout.strip()[-500:]}")
        if trend_result.returncode != 0:
            log(f"  热点侦察stderr: {trend_result.stderr.strip()[-300:]}")
    except Exception as e:
        log(f"✗ 热点侦察失败: {e}")
        errors.append(f"热点侦察: {e}")

    # 阶段二：BUG修复
    try:
        fixes_count = scan_and_fix_all_sites()
        state["bug_fixes_applied"] += fixes_count
    except Exception as e:
        log(f"✗ 阶段二失败: {e}")
        errors.append(f"阶段二: {e}")
        fixes_count = 0

    # 广告收益监控
    try:
        ad_result = subprocess.run(
            [sys.executable, str(ROOT / "shared" / "ad_monitor.py")],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60
        )
        log(f"  广告报告: {ad_result.stdout.strip()[-300:]}")
    except Exception as e:
        log(f"  广告监控跳过: {e}")

    # 阶段三：站点扩展
    try:
        if images_changed or fixes_count > 0:
            data_updated = update_data_from_images()
            render_and_deploy(state)
        else:
            log("=" * 40)
            log("阶段三：无变更，跳过")
            log("=" * 40)
    except Exception as e:
        log(f"✗ 阶段三失败: {e}")
        errors.append(f"阶段三: {e}")

    state["errors"] = errors
    save_state(state)

    log("=" * 60)
    log(f"Nightly Worker 完成。图片变更:{images_changed} 修复:{fixes_count} 错误:{len(errors)}")
    log("=" * 60)

if __name__ == "__main__":
    main()
