#!/usr/bin/env python3

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path


EXCLUDED_NAMES = {
    ".git",
    ".gitignore",
    ".DS_Store",
    ".idea",
    ".vscode",
    ".claude",
    ".codex",
    ".openclaw",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "coverage",
    "artifacts",
    "todo.md",
    "TODO.md",
}


def should_skip(path: Path) -> bool:
    name = path.name
    if name in EXCLUDED_NAMES:
        return True
    if name.startswith("."):
        return True
    return False


def copy_tree(source: Path, destination: Path) -> tuple[list[str], list[str]]:
    copied = []
    skipped = []

    for item in sorted(source.iterdir()):
        if should_skip(item):
            skipped.append(item.name)
            continue

        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        copied.append(item.name)

    return copied, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a publish-safe copy of a skill directory.")
    parser.add_argument("source", help="Path to the local skill directory")
    parser.add_argument("--out-dir", help="Optional explicit output directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")

    if args.out_dir:
        destination = Path(args.out_dir).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
    else:
        destination = Path(tempfile.mkdtemp(prefix=f"{source.name}-publish-"))

    copied, skipped = copy_tree(source, destination)

    result = {
        "source": str(source),
        "prepared_dir": str(destination),
        "copied_top_level": copied,
        "skipped_top_level": skipped,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(destination)

    return 0


if __name__ == "__main__":
    sys.exit(main())
