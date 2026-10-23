#!/usr/bin/env python3
"""Install the bundled scientific appraisal skill using only the standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import tempfile
import uuid


NAME = "scientific-article-appraisal"
SOURCE = Path(__file__).absolute().parents[1] / "skills" / NAME


def safe_path(path):
    """Reject links (including dangling ones) before any path resolution."""
    for part in reversed((path, *path.parents)):
        try:
            info = part.lstat()
            mode = info.st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symlink or reparse point is not allowed: {part}")
        if part != path and not stat.S_ISDIR(mode):
            raise ValueError(f"Ancestor is not a directory: {part}")


def walk_error(error):
    raise error


def validate_tree(root):
    safe_path(root)
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        for name in dirs + files:
            entry = Path(directory) / name
            info = entry.lstat()
            mode = info.st_mode
            if getattr(info, "st_file_attributes", 0) & 0x400 or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError(f"Links, reparse points and special files are not allowed: {entry}")


def validate_target(target):
    if ".." in target.parts or target.name != NAME:
        raise ValueError(f"Destination must be an exact {NAME} directory without traversal")
    safe_path(target)
    source = SOURCE.absolute()
    if target == source or source in target.parents or target in source.parents:
        raise ValueError("Source and destination overlap")
    if target.exists():
        validate_tree(target)



CACHE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache", "caches"}


def manifest(root, exclude_caches=False):
    """Map relative paths to kinds and SHA-256 bytes, including empty directories."""
    validate_tree(root)
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        if exclude_caches:
            dirs[:] = [name for name in dirs if name not in CACHE_DIRS]
        for name in dirs:
            result[(Path(directory) / name).relative_to(root).as_posix()] = ["directory"]
        for name in files:
            if exclude_caches and (name in CACHE_DIRS or name.endswith((".pyc", ".pyo"))):
                continue
            path = Path(directory) / name
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[path.relative_to(root).as_posix()] = ["file", digest.hexdigest()]
    return result


def install(target, payload, existing=None):
    target.parent.mkdir(parents=True, exist_ok=True)
    safe_path(target)
    stage = Path(tempfile.mkdtemp(prefix=f".{NAME}.stage-", dir=target.parent))
    backup = None
    try:
        for relative, entry in sorted(payload.items()):
            destination = stage / relative
            if entry[0] == "directory":
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE / relative, destination)
        if manifest(stage) != payload:
            raise ValueError("Staged payload verification failed; source may have changed")
        validate_target(target)
        backup = None
        current = manifest(target, exclude_caches=True) if target.exists() else None
        if current != existing:
            raise ValueError("Destination changed while staging; refusing to overwrite")
        if existing is not None:
            backup = target.with_name(f".{NAME}.backup-{uuid.uuid4().hex}")
            if backup.exists() or backup.is_symlink():
                raise ValueError("Backup path already exists")
            target.rename(backup)
        stage.rename(target)
        return backup
    except BaseException:
        # Never delete a destination to roll back: preserve unexpected concurrent data.
        if backup is not None and backup.exists() and not target.exists() and not target.is_symlink():
            safe_path(target)
            backup.rename(target)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)


class Parser(argparse.ArgumentParser):
    def print_help(self, file=None):
        print(json.dumps({"status": "help", "target": None, "usage": self.format_help()}), file=file)

    def error(self, message):
        raise ValueError(message)


def main():
    target = None
    try:
        parser = Parser(description=__doc__)
        location = parser.add_mutually_exclusive_group(required=True)
        location.add_argument("--target-dir")
        location.add_argument("--agent", choices=("hermes", "codex", "claude"))
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--dry-run", action="store_true")
        mode.add_argument("--check", action="store_true")
        parser.add_argument("--replace", action="store_true")
        args = parser.parse_args()
        if args.check and args.replace:
            raise ValueError("--check cannot be combined with --replace")
        if args.target_dir is not None:
            target = Path(args.target_dir).absolute()
        elif args.agent == "hermes":
            target = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / "skills" / NAME
        else:
            target = Path.home() / {"codex": ".agents", "claude": ".claude"}[args.agent] / "skills" / NAME
        target = target.absolute()
        validate_target(target)
        validate_tree(SOURCE)
        text = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
        if frontmatter is None:
            raise ValueError("SKILL.md must have closed YAML frontmatter")
        match = re.search(r"^version:[ \t]*[\"']?([^\s\"']+)", frontmatter.group(1), re.MULTILINE)
        if match is None:
            raise ValueError("SKILL.md frontmatter must contain a version")
        payload = manifest(SOURCE, exclude_caches=True)
        existing = manifest(target, exclude_caches=True) if target.exists() else None
        backup = None
        if args.check:
            if existing != payload:
                raise ValueError("Destination is missing or payload hashes/paths differ")
            status = "verified"
        elif existing == payload:
            status = "already_installed"
        elif existing is not None and not args.replace:
            raise ValueError("Destination differs; use --replace to preserve a backup and replace")
        elif args.dry_run:
            status = "dry_run"
        else:
            backup = install(target, payload, existing)
            status = "replaced" if backup else "installed"
        print(json.dumps({"status": status, "target": str(target),
                          "backup": str(backup) if backup else None,
                          "version": match.group(1) if match else None,
                          "files": sum(entry[0] == "file" for entry in payload.values()),
                          "sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}))
        return 0
    except (ValueError, OSError, KeyboardInterrupt) as error:
        print(json.dumps({"status": "error", "target": str(target) if target else None,
                          "error": str(error) or "Installation interrupted"}))
        return 130 if isinstance(error, KeyboardInterrupt) else 1


def interrupted(signum, frame):
    raise KeyboardInterrupt(f"Interrupted by signal {signum}")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())
