"""Backup user-level Claude Code and Codex configs to project repo."""
import shutil, os, json
from pathlib import Path

PROJECT = Path(r"d:\AI网站文件夹")
BACKUP = PROJECT / "backup-config"
USER_CLAUDE = Path(os.path.expanduser(r"~\.claude"))
USER_CODEX = Path(os.path.expanduser(r"~\.codex"))
PROJECT_MEMORY = USER_CLAUDE / "projects" / "d--AI-----" / "memory"


def copy_if_exists(src, dst):
    if src.exists():
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.makedirs(dst.parent, exist_ok=True)
            shutil.copy2(src, dst)
        print(f"  + {dst.relative_to(PROJECT)}")
    else:
        print(f"  - {src} not found, skipping")


def main():
    BACKUP.mkdir(parents=True, exist_ok=True)

    print("Backing up user configs...")

    # Claude Code settings
    copy_if_exists(USER_CLAUDE / "settings.json", BACKUP / "claude-settings.json")

    # Memory files (BIO system)
    copy_if_exists(PROJECT_MEMORY, BACKUP / "memory")

    # Codex config
    copy_if_exists(USER_CODEX / "config.toml", BACKUP / "codex-config.toml")

    # Codex installed skills list (if any)
    codex_skills = USER_CODEX / "skills"
    if codex_skills.exists():
        for item in codex_skills.iterdir():
            copy_if_exists(item, BACKUP / "codex-skills" / item.name)

    print(f"\nDone. Backup saved to {BACKUP}")


if __name__ == "__main__":
    main()
