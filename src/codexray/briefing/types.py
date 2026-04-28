from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BriefingEvidence:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class BriefingCard:
    title: str
    text: str
    evidence: tuple[BriefingEvidence, ...]


@dataclass(frozen=True, slots=True)
class GitCommitSummary:
    hash: str
    subject: str
    commit_type: str
    process_categories: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GitHistorySummary:
    available: bool
    commit_count: int
    type_distribution: tuple[BriefingEvidence, ...]
    process_commits: tuple[GitCommitSummary, ...]
    recent_commits: tuple[GitCommitSummary, ...]
    unavailable_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CodebaseBriefing:
    schema_version: int
    path: str
    title: str
    executive: tuple[BriefingCard, ...]
    architecture: tuple[BriefingCard, ...]
    quality_risk: tuple[BriefingCard, ...]
    build_process: tuple[BriefingCard, ...]
    explain: tuple[BriefingCard, ...]
    deep_dive: tuple[BriefingCard, ...]
    git_history: GitHistorySummary
