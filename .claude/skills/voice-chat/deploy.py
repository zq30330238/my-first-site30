"""自动部署 - 提交并推送本地更改到GitHub，触发Cloudflare Pages自动部署"""
import subprocess, sys, os

REPO = r"d:\AI网站文件夹"

def deploy(message=None):
    os.chdir(REPO)
    # 检查是否有更改
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status.stdout.strip():
        return {"status": "no_changes", "message": "没有需要部署的更改"}

    files = [line[3:] for line in status.stdout.strip().split("\n")]
    msg = message or f"Auto-deploy: 更新 {len(files)} 个文件"

    subprocess.run(["git", "add", "-A"], capture_output=True, cwd=REPO)
    subprocess.run(["git", "commit", "-m", msg], capture_output=True, cwd=REPO)
    result = subprocess.run(["git", "push", "origin", "master"], capture_output=True, text=True, cwd=REPO)

    if result.returncode != 0:
        return {"status": "error", "message": result.stderr[:200]}
    return {"status": "deployed", "files": files, "message": msg}

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    import json
    print(json.dumps(deploy(msg), ensure_ascii=False, indent=2))
