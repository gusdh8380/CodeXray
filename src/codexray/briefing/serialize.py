from __future__ import annotations

import json

from .types import BriefingCard, CodebaseBriefing, GitCommitSummary


def to_json(briefing: CodebaseBriefing) -> str:
    payload = {
        "schema_version": briefing.schema_version,
        "path": briefing.path,
        "title": briefing.title,
        "executive": [_card(card) for card in briefing.executive],
        "architecture": [_card(card) for card in briefing.architecture],
        "quality_risk": [_card(card) for card in briefing.quality_risk],
        "build_process": [_card(card) for card in briefing.build_process],
        "explain": [_card(card) for card in briefing.explain],
        "deep_dive": [_card(card) for card in briefing.deep_dive],
        "git_history": {
            "available": briefing.git_history.available,
            "commit_count": briefing.git_history.commit_count,
            "type_distribution": [
                {"label": item.label, "value": item.value}
                for item in briefing.git_history.type_distribution
            ],
            "process_commits": [
                _commit(commit) for commit in briefing.git_history.process_commits
            ],
            "recent_commits": [
                _commit(commit) for commit in briefing.git_history.recent_commits
            ],
            "unavailable_reason": briefing.git_history.unavailable_reason,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _card(card: BriefingCard) -> dict[str, object]:
    return {
        "title": card.title,
        "text": card.text,
        "evidence": [
            {"label": item.label, "value": item.value} for item in card.evidence
        ],
    }


def _commit(commit: GitCommitSummary) -> dict[str, object]:
    return {
        "hash": commit.hash,
        "subject": commit.subject,
        "commit_type": commit.commit_type,
        "process_categories": list(commit.process_categories),
    }
