from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

from .types import BriefingEvidence, GitCommitSummary, GitHistorySummary

_TIMEOUT = 5
_MAX_COMMITS = 60

_PROCESS_PATHS = {
    "openspec": "OpenSpec 명세",
    "docs/validation": "검증 캡처",
    "docs/vibe-coding": "회고",
    "docs/handoff": "인수인계",
    "AGENTS.md": "에이전트 지침",
    "CLAUDE.md": "Claude 지침",
    ".claude": "Claude 환경",
    ".omc": "OMC 메모리",
    ".roboco": "ROBOCO 설정",
}


def build_git_history(root: Path) -> GitHistorySummary:
    if not _is_git_repo(root):
        return GitHistorySummary(
            available=False,
            commit_count=0,
            type_distribution=(),
            process_commits=(),
            recent_commits=(),
            unavailable_reason="not a git repository",
        )
    count = _commit_count(root)
    raw = _git_log(root)
    if raw is None:
        return GitHistorySummary(
            available=False,
            commit_count=count,
            type_distribution=(),
            process_commits=(),
            recent_commits=(),
            unavailable_reason="git log unavailable",
        )
    commits = tuple(_parse_commits(raw))
    type_counts = Counter(commit.commit_type for commit in commits)
    type_distribution = tuple(
        BriefingEvidence(label=key, value=str(type_counts[key]))
        for key in sorted(type_counts)
    )
    process_commits = tuple(
        commit for commit in commits if commit.process_categories
    )[:10]
    return GitHistorySummary(
        available=True,
        commit_count=count,
        type_distribution=type_distribution,
        process_commits=process_commits,
        recent_commits=commits[:8],
    )


def _is_git_repo(root: Path) -> bool:
    result = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    return result is not None and result.returncode == 0 and result.stdout.strip() == "true"


def _commit_count(root: Path) -> int:
    result = _run_git(root, ["rev-list", "--count", "HEAD"])
    if result is None or result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def _git_log(root: Path) -> str | None:
    result = _run_git(
        root,
        [
            "log",
            f"--max-count={_MAX_COMMITS}",
            "--name-only",
            "--pretty=format:__COMMIT__%x1f%h%x1f%s",
        ],
    )
    if result is None or result.returncode != 0:
        return None
    return result.stdout


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=_TIMEOUT,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _parse_commits(raw: str) -> list[GitCommitSummary]:
    commits: list[GitCommitSummary] = []
    current_hash = ""
    current_subject = ""
    paths: list[str] = []
    for line in raw.splitlines():
        if line.startswith("__COMMIT__"):
            if current_hash:
                commits.append(_commit(current_hash, current_subject, paths))
            _, current_hash, current_subject = line.split("\x1f", maxsplit=2)
            paths = []
            continue
        stripped = line.strip()
        if stripped:
            paths.append(stripped)
    if current_hash:
        commits.append(_commit(current_hash, current_subject, paths))
    return commits


def _commit(commit_hash: str, subject: str, paths: list[str]) -> GitCommitSummary:
    categories = sorted(
        {
            category
            for path in paths
            for prefix, category in _PROCESS_PATHS.items()
            if path == prefix or path.startswith(prefix + "/") or path.startswith(prefix)
        }
    )
    return GitCommitSummary(
        hash=commit_hash,
        subject=subject,
        commit_type=_commit_type(subject),
        process_categories=tuple(categories),
    )


def _commit_type(subject: str) -> str:
    prefix = subject.split(":", maxsplit=1)[0].strip().lower()
    if prefix in {"feat", "fix", "docs", "test", "refactor", "chore", "perf"}:
        return prefix
    return "other"
