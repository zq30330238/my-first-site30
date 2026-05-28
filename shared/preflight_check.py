"""One-click deployment readiness check.

Usage: python shared/preflight_check.py
Exit 0 = all ready, exit 1 = something wrong.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime


def fmt_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def check_cf_token() -> tuple[bool, str]:
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        return False, "CLOUDFLARE_API_TOKEN not set"

    result = subprocess.run(
        [
            "curl", "-s",
            "-H", f"Authorization: Bearer {token}",
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
        ],
        capture_output=True, text=True, timeout=15,
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, f"could not parse response (HTTP {result.returncode})"

    if not data.get("success"):
        errs = data.get("errors", [])
        msg = errs[0].get("message", "unknown error") if errs else "unknown error"
        return False, f"token invalid ({msg})"

    status = data.get("result", {}).get("status", "unknown")
    expires = data.get("result", {}).get("expires_on", None)
    if status != "active":
        return False, f"token status is '{status}' (not active)"

    suffix = f" (expires {expires})" if expires else ""
    return True, f"active{suffix}"


def check_vpn() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [
                "curl", "-s", "--max-time", "5",
                "https://www.google.com",
                "-o", os.devnull,
                "-w", "%{http_code}",
            ],
            capture_output=True, text=True, timeout=10,
        )
        code = result.stdout.strip()
        if code in ("200", "301", "302"):
            return True, f"google.com accessible (HTTP {code})"
        if code == "000":
            return False, "Flygo VPN may not be running (connection failed)"
        return False, f"google.com returned HTTP {code}"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Flygo VPN may not be running (timeout or curl unavailable)"


def check_wrangler() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["npx", "wrangler", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        out = (result.stdout or result.stderr or "").strip()
        if not out:
            return False, "wrangler not installed (no output)"
        # Extract version number
        version_str = out.split()[-1].lstrip("v")
        return True, f"v{version_str}"
    except FileNotFoundError:
        return False, "npx not found — Node.js not installed?"
    except subprocess.TimeoutExpired:
        return False, "npx wrangler timed out (>30s)"
    except Exception as e:
        return False, f"wrangler error: {e}"


def check_disk() -> tuple[bool, str]:
    try:
        usage = shutil.disk_usage("d:/")
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        msg = f"D:\\  {free_gb:.0f}GB free / {total_gb:.0f}GB total"
        if free_gb < 1:
            return False, f"{msg}  ** CRITICAL: < 1GB **"
        if free_gb < 5:
            return False, f"{msg}  ** WARNING: < 5GB **"
        return True, msg
    except Exception as e:
        return False, f"D: drive check failed: {e}"


def main():
    checks = [
        ("CF Token", check_cf_token),
        ("VPN", check_vpn),
        ("wrangler", check_wrangler),
        ("Disk", check_disk),
    ]

    results: list[tuple[str, bool, str]] = []

    print(f"=== Deployment Preflight Check {fmt_ts()} ===\n")

    for label, fn in checks:
        ok, msg = fn()
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {label:12s} {msg}")
        results.append((label, ok, msg))

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n---")
    if passed == total:
        print(f"All checks passed. Ready to deploy.")
        sys.exit(0)
    else:
        failed = total - passed
        print(f"{failed}/{total} checks failed. Fix before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
