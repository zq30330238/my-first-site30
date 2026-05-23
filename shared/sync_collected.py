#!/usr/bin/env python3
"""Sync verified character images from server to local project directories.

Pulls images from the server's collected/<site>/<slug>.png and copies them
into the corresponding local site directory under images/.

Usage:
  python shared/sync_collected.py                        # pull new images, delete server copies
  python shared/sync_collected.py --keep-server          # keep server files after sync
  python shared/sync_collected.py --dry-run              # preview only
  python shared/sync_collected.py --site dragonball      # sync one site
  python shared/sync_collected.py --all                  # re-sync even up-to-date files

SSH config requirements:
  - Passwordless SSH key to root@206.119.168.150
  - Server has /root/my-first-site30/collected/ with collected PNGs
"""

import sys, json, subprocess, argparse, hashlib, os
from pathlib import Path
from typing import Optional

LOCAL_ROOT = Path(__file__).resolve().parent.parent
SERVER = "root@206.119.168.150"
SERVER_COLLECTED = "/root/my-first-site30/collected/"
SERVER_TARGETS = "/root/my-first-site30/shared/collect_targets.json"

# Map data site slug -> local project subdirectory name
# Images go into <dir>/images/ on the local side
SITE_DIR_MAP = {
    "dragonball-site": "dragonball-site",
    "onepiece-site": "onepiece-site",
    "naruto-site": "naruto-site",
    "lol-site": "lol-site",
    "fortnite-site": "fortnite-site",
    "valorant-site": "valorant-site",
    "eldenring-site": "eldenring-site",
    "demonslayer-site": "anime-site/guides/demonslayer",
    "aot-site": "anime-site/guides/aot",
    "jjk-site": "anime-site/guides/jjk",
}

SSH_OPTS = "-o ConnectTimeout=10 -o StrictHostKeyChecking=no"


def parse_args():
    p = argparse.ArgumentParser(description="Sync collected images from server")
    p.add_argument("--keep-server", action="store_true", help="Keep files on server after sync")
    p.add_argument("--dry-run", action="store_true", help="Show what would be synced without copying")
    p.add_argument("--site", help="Sync only images for this site (e.g., dragonball)")
    p.add_argument("--all", action="store_true", help="Re-sync even if local file exists and is up to date")
    return p.parse_args()


def ssh(cmd: str) -> str:
    """Run a shell command on the server via SSH. Returns stdout.

    NOTE: cmd is passed as-is to SSH. Do NOT pre-quote parts of cmd —
    this function handles quoting via stdin to avoid nested-quote bugs.
    """
    full_cmd = f'ssh {SSH_OPTS} {SERVER} bash'
    result = subprocess.run(
        full_cmd, shell=True, capture_output=True, text=True, timeout=30,
        input=cmd
    )
    if result.returncode != 0:
        if result.stderr.strip():
            print(f"  [ssh] {result.stderr.strip()[:200]}", file=sys.stderr)
        return ""
    return result.stdout.strip()


def shlex_quote(s: str) -> str:
    """Minimal shell quoting for SSH commands."""
    return "'" + s.replace("'", "'\\''") + "'"


def scp(remote_path: str, local_path: str) -> bool:
    """Copy a single file from server to local. Returns True on success."""
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        f'scp {SSH_OPTS} {SERVER}:{shlex_quote(remote_path)} {shlex_quote(local_path)}',
        shell=True, capture_output=True, timeout=30,
    )
    return result.returncode == 0


def rm_remote(path: str) -> bool:
    """Delete a file on the server. Returns True on success."""
    out = ssh(f"rm -f {path} && echo OK || echo FAIL")
    return out == "OK"


def list_server_images() -> list:
    """List all PNG files on the server under collected/."""
    output = ssh(
        f"find {SERVER_COLLECTED} -name '*.png' -printf '%p\\t%s\\n'"
    )
    if not output:
        return []
    images = []
    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        path = parts[0]
        size = int(parts[1]) if len(parts) > 1 else 0
        rel = path.replace(SERVER_COLLECTED, "").lstrip("/")
        if "/" not in rel:
            continue
        site, filename = rel.split("/", 1)
        slug = Path(filename).stem
        images.append({"site": site, "slug": slug, "path": path, "size": size, "file": filename})
    return images


def load_targets() -> list:
    """Load collect_targets.json from server or generate locally."""
    server_raw = ssh(f"cat {SERVER_TARGETS} 2>/dev/null || echo '__NOT_FOUND__'")
    if server_raw and server_raw != "__NOT_FOUND__":
        try:
            return json.loads(server_raw)
        except json.JSONDecodeError:
            pass
    local_file = LOCAL_ROOT / "shared" / "collect_targets.json"
    if local_file.exists():
        with open(local_file, encoding="utf-8") as f:
            return json.load(f)
    data_file = LOCAL_ROOT / "shared" / "anime_site_data.json"
    if data_file.exists():
        return _generate_targets(data_file)
    print("ERROR: Cannot find targets anywhere. Run collect_images_loop.py --gen-targets first.")
    sys.exit(1)


def _generate_targets(data_path: Path) -> list:
    import re as _re
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    targets = []
    for site_key, site_data in data.items():
        series_raw = site_data.get("site_name", site_key)
        series = series_raw.replace(" Wiki", "").replace(" Database", "")
        for char in site_data.get("characters", []):
            name = char["name"]
            slug = (
                name.lower()
                .replace(" ", "-")
                .replace(".", "")
                .replace("'", "")
                .replace('"', "")
                .replace("(", "")
                .replace(")", "")
                .replace(":", "")
                .replace("!", "")
            )
            slug = _re.sub(r"-+", "-", slug).strip("-")
            targets.append({
                "site": site_key,
                "character": name,
                "slug": slug,
                "series": series,
            })
    return targets


def local_image_path(target: dict) -> Optional[Path]:
    """Determine local destination path for a collected image."""
    site = target["site"]
    dir_name = SITE_DIR_MAP.get(site)
    if not dir_name:
        return None
    return LOCAL_ROOT / dir_name / "images" / f"{target['slug']}.png"


def main():
    args = parse_args()
    print("=" * 50)
    print("Sync Collected Images")
    print(f"Server: {SERVER}")
    print(f"Keep server files: {args.keep_server}")
    print(f"Dry run: {'YES' if args.dry_run else 'NO'}")
    if args.site:
        print(f"Site filter: {args.site}")
    print("=" * 50)

    # Load targets
    targets = load_targets()
    target_map = {(t["site"], t["slug"]): t for t in targets}
    print(f"Loaded {len(targets)} targets")

    # List server images
    all_images = list_server_images()
    if args.site:
        all_images = [img for img in all_images if img["site"] == args.site]

    if not all_images:
        print("No images found on server (or SSH connection failed).")
        ts = ", ".join(sorted(set(t["site"] for t in targets)))
        print(f"Expected sites: {ts}")
        sys.exit(0)

    # Group by site
    by_site: dict = {}
    for img in all_images:
        by_site.setdefault(img["site"], []).append(img)

    print(f"Found images on server by site:")
    for site, imgs in sorted(by_site.items()):
        print(f"  {site}: {len(imgs)} image(s)")
    print()

    # Process
    synced = 0
    skipped = 0
    failed = 0
    deleted = 0
    no_mapping = 0

    for img in all_images:
        key = (img["site"], img["slug"])
        target = target_map.get(key)
        if not target:
            target_sites_from_data = set()
            for t in targets:
                target_sites_from_data.add(t["site"])
            if img["site"] in target_sites_from_data:
                print(f"  ? {img['site']}/{img['slug']}.png — no matching target (slug mismatch?)")
            else:
                print(f"  ? {img['site']}/{img['slug']}.png — site not in targets data")
            no_mapping += 1
            continue

        local_path = local_image_path(target)
        if local_path is None:
            print(f"  ? {img['site']}/{img['slug']}.png — no local directory mapping")
            no_mapping += 1
            continue

        if not args.all and local_path.exists():
            if local_path.stat().st_size == img["size"]:
                print(f"  = {target['character']} ({img['site']}) — already synced")
                skipped += 1
                if not args.keep_server:
                    if rm_remote(img["path"]):
                        deleted += 1
                continue

        if args.dry_run:
            print(f"  -> {target['character']} ({img['site']}) -> {local_path}")
            synced += 1
            continue

        # Do the copy
        if scp(img["path"], str(local_path)):
            # Verify integrity
            local_size = local_path.stat().st_size
            if local_size != img["size"]:
                print(f"  WARN {target['character']} — size mismatch (server:{img['size']} local:{local_size})")
                local_path.unlink(missing_ok=True)
                failed += 1
                continue
            print(f"  OK {target['character']} ({img['site']}) — {local_size} bytes")
            synced += 1
            if not args.keep_server:
                if rm_remote(img["path"]):
                    deleted += 1
        else:
            print(f"  FAIL {target['character']} ({img['site']}) — SCP error")
            failed += 1

    # Summary
    print()
    print("=" * 50)
    print(f"Synced: {synced}")
    print(f"Skipped (already synced): {skipped}")
    print(f"Failed: {failed}")
    print(f"No mapping: {no_mapping}")
    if not args.keep_server and not args.dry_run:
        print(f"Deleted from server: {deleted}")
    if args.dry_run:
        print(f"[DRY RUN — no files copied]")
    print("=" * 50)

    # Show unmapped sites on server for user awareness
    server_sites = set(img["site"] for img in all_images)
    mapped_sites = set(SITE_DIR_MAP.keys())
    unmapped = server_sites - mapped_sites
    if unmapped:
        print(f"\nUnmapped server sites (add to SITE_DIR_MAP): {', '.join(sorted(unmapped))}")


if __name__ == "__main__":
    main()
