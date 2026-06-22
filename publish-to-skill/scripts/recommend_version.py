#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


VERSION_RE = re.compile(r"(?m)^version:\s*['\"]?(\d+\.\d+\.\d+)['\"]?\s*$")
BUMP_BOUNDARY_RE = re.compile(
    r"(^|\b)(update|upgrade|bump|release)(\s+the)?\s+ver(sion)?\b|^v?\d+\.\d+\.\d+$",
    re.IGNORECASE,
)
MAJOR_RE = re.compile(r"\bbreaking\b|breaking change|^major[:\s]", re.IGNORECASE)
MINOR_RE = re.compile(r"^feat(\(.+\))?:|\bfeature\b|\bnew capability\b", re.IGNORECASE)
PATCH_RE = re.compile(
    r"^fix(\(.+\))?:|^docs(\(.+\))?:|^refactor(\(.+\))?:|\bbug\b|\bexample\b|\bsample\b|\bhint\b|\bcleanup\b",
    re.IGNORECASE,
)


@dataclass
class Commit:
    sha: str
    subject: str
    body: str


def run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_repo_root(path: Path) -> Optional[Path]:
    try:
        root = run(["git", "-C", str(path), "rev-parse", "--show-toplevel"], check=True)
    except subprocess.CalledProcessError:
        return None
    return Path(root)


def read_current_version(skill_path: Path, explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"SKILL.md not found under {skill_path}")
    match = VERSION_RE.search(skill_md.read_text())
    if not match:
        raise SystemExit("No version field found in SKILL.md; pass --current-version explicitly")
    return match.group(1)


def parse_semver(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise SystemExit(f"Invalid semver: {version}")
    return tuple(int(part) for part in match.groups())


def bump_version(version: str, bump: str) -> str:
    major, minor, patch = parse_semver(version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if bump == "none":
        return version
    raise ValueError(f"Unknown bump: {bump}")


def recent_commits(repo_root: Path, limit: int) -> list[Commit]:
    raw = run(
        [
            "git",
            "-C",
            str(repo_root),
            "log",
            f"-n{limit}",
            "--format=%H%x1f%s%x1f%b%x1e",
        ]
    )
    commits = []
    for chunk in raw.split("\x1e"):
        if not chunk.strip():
            continue
        parts = chunk.split("\x1f")
        if len(parts) < 2:
            continue
        while len(parts) < 3:
            parts.append("")
        sha = parts[0]
        subject = parts[1]
        body = "\x1f".join(parts[2:])
        commits.append(Commit(sha=sha.strip(), subject=subject.strip(), body=body.strip()))
    return commits


def commits_since_boundary(commits: list[Commit]) -> tuple[list[Commit], Optional[Commit]]:
    relevant = []
    boundary = None
    for commit in commits:
        if BUMP_BOUNDARY_RE.search(commit.subject):
            boundary = commit
            break
        relevant.append(commit)
    return relevant, boundary


def working_tree_changes(repo_root: Path) -> list[str]:
    output = run(["git", "-C", str(repo_root), "status", "--short"], check=False)
    return [line for line in output.splitlines() if line.strip()]


def classify(commits: list[Commit], dirty_lines: list[str]) -> tuple[str, list[str]]:
    reasons = []
    texts = [f"{commit.subject}\n{commit.body}".strip() for commit in commits]

    for text in texts:
        if MAJOR_RE.search(text):
            reasons.append("found explicit breaking-change language in recent commits")
            return "major", reasons

    for text in texts:
        if MINOR_RE.search(text):
            reasons.append("found a feature-style recent commit")
            return "minor", reasons

    if commits:
        reasons.append("recent unpublished commits exist, but none indicate a new feature")
        return "patch", reasons

    if dirty_lines:
        reasons.append("working tree has unpublished changes")
        return "patch", reasons

    reasons.append("no meaningful unpublished changes detected")
    return "none", reasons


def first_human_change(commits: list[Commit], dirty_lines: list[str]) -> str:
    if commits:
        return commits[0].subject
    if dirty_lines:
        return "local unpublished changes"
    return "no changes"


def normalize_changelog_subject(subject: str) -> str:
    clean = re.sub(r"^(feat|fix|docs|refactor|chore)(\(.+\))?:\s*", "", subject, flags=re.IGNORECASE)
    clean = re.sub(r"\s+", " ", clean).strip(" .")
    return clean or "update skill"


def build_result(skill_path: Path, current_version: str, limit: int) -> dict:
    repo_root = git_repo_root(skill_path)
    commits = recent_commits(repo_root, limit) if repo_root else []
    relevant_commits, boundary = commits_since_boundary(commits)
    dirty_lines = working_tree_changes(repo_root) if repo_root else []
    bump, reasons = classify(relevant_commits, dirty_lines)
    next_version = bump_version(current_version, bump)
    change_subject = normalize_changelog_subject(first_human_change(relevant_commits, dirty_lines))

    if bump == "minor":
        changelog = f"feat: {change_subject}"
    elif bump == "patch":
        changelog = f"fix: {change_subject}"
    elif bump == "major":
        changelog = change_subject
    else:
        changelog = ""

    return {
        "skill_path": str(skill_path),
        "repo_root": str(repo_root) if repo_root else None,
        "current_version": current_version,
        "recommended_bump": bump,
        "next_version": next_version,
        "suggested_changelog": changelog,
        "boundary_commit": {
            "sha": boundary.sha,
            "subject": boundary.subject,
        }
        if boundary
        else None,
        "recent_commits_considered": [
            {"sha": commit.sha, "subject": commit.subject} for commit in relevant_commits
        ],
        "working_tree_changes": dirty_lines,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend the next version for a skill publish.")
    parser.add_argument("skill_path", help="Path to the local skill directory")
    parser.add_argument("--current-version", help="Override the current version instead of reading SKILL.md")
    parser.add_argument("--limit", type=int, default=20, help="How many recent commits to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    skill_path = Path(args.skill_path).expanduser().resolve()
    current_version = read_current_version(skill_path, args.current_version)
    result = build_result(skill_path, current_version, args.limit)

    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    else:
        print(f"current_version: {result['current_version']}")
        print(f"recommended_bump: {result['recommended_bump']}")
        print(f"next_version: {result['next_version']}")
        if result["suggested_changelog"]:
            print(f"suggested_changelog: {result['suggested_changelog']}")
        if result["boundary_commit"]:
            print(f"boundary_commit: {result['boundary_commit']['subject']}")
        for reason in result["reasons"]:
            print(f"reason: {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
