"""CF Pages安全部署——自动验证production_branch + 部署后校验自定义域名"""
import sys, json, subprocess, urllib.request, os, io

# Windows console GBK fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="backslashreplace")

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ACCOUNT = "4e8cd083c07627f679dd86dc5b488fb0"
BASE = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/pages"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def api(path, method="GET", body=None):
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS, method=method)
    if body:
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def deploy(project_name, dir_path):
    proj = api(f"/projects/{project_name}")["result"]
    prod_branch = proj.get("production_branch", "master")
    domains = [d for d in proj.get("domains", []) if not d.endswith(".pages.dev")]
    custom_domain = domains[0] if domains else None

    print(f"项目: {project_name}")
    print(f"生产分支: {prod_branch}")
    print(f"自定义域名: {custom_domain or '无'}")

    if not custom_domain:
        print("ERROR: 无自定义域名，中止！")
        return 1

    # 部署
    print(f"\n部署 {dir_path} -> {project_name} (branch={prod_branch})...")
    env = os.environ.copy()
    env["CLOUDFLARE_API_TOKEN"] = TOKEN
    result = subprocess.run(
        " ".join(["npx.cmd", "wrangler", "pages", "deploy", dir_path,
         "--project-name", project_name, "--branch", prod_branch]),
        capture_output=True, timeout=120, env=env, shell=True, encoding='utf-8'
    )
    out = result.stdout or ""
    err = result.stderr or ""
    print(out)
    if result.returncode != 0:
        print(f"DEPLOY FAILED:\n{err}")
        return 1

    # 提取preview URL
    preview_url = None
    for line in out.split("\n"):
        if "pages.dev" in line:
            preview_url = line.strip().split()[-1]
            break

    # 验证
    print(f"\n验证自定义域名: {custom_domain}")
    try:
        req = urllib.request.Request(f"https://{custom_domain}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            custom_body = resp.read().decode()
        print(f"  自定义域名 HTTP {resp.status}, {len(custom_body)} bytes — OK")
    except Exception as e:
        print(f"  自定义域名 ERROR: {e}")
        return 1

    if preview_url:
        print(f"验证Preview URL: {preview_url}")
        try:
            req = urllib.request.Request(preview_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                preview_body = resp.read().decode()
            print(f"  Preview HTTP {resp.status}, {len(preview_body)} bytes — OK")
            if len(custom_body) != len(preview_body):
                print(f"  警告: 内容大小不一致 (custom={len(custom_body)}, preview={len(preview_body)})")
        except Exception as e:
            print(f"  Preview ERROR: {e}")

    print(f"\n部署完成: https://{custom_domain}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python deploy_cf.py <project_name> <dir_path>")
        print("示例: python deploy_cf.py anime-jycsd d:/AI网站文件夹/anime-site")
        sys.exit(1)
    sys.exit(deploy(sys.argv[1], sys.argv[2]))
