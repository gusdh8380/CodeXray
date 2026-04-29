"""First-step guide for repos that don't yet show vibe-coding signals."""

from __future__ import annotations

from typing import Any


def build_starter_guide(*, quality: Any, hotspots: Any) -> list[dict[str, str]]:
    grade = quality.overall.grade or "N/A"
    return [
        {
            "action": "프로젝트에 CLAUDE.md 작성",
            "reason": (
                "AI 에이전트가 이 레포의 목적·스택·관행을 매번 다시 파악하지 않고 바로 일을 "
                "이어받을 수 있게 하려면 가장 먼저 갖춰야 할 파일입니다."
            ),
            "ai_prompt": (
                "이 프로젝트의 루트에 CLAUDE.md를 작성해주세요. "
                "다음 구조를 사용하세요: "
                "1) Project Overview — 한두 문장으로 이 프로젝트가 뭐 하는 건지, "
                "2) Tech Stack — 사용된 언어와 프레임워크, "
                "3) Development Commands — build/test/lint 명령어, "
                "4) Coding Conventions — 명명 규칙·디렉토리 구조 메모. "
                "기존 README와 package.json/pyproject.toml을 읽고 빈 칸 없이 채워주세요."
            ),
        },
        {
            "action": "docs/intent.md 로 의도 명문화",
            "reason": (
                "Why를 글로 남겨두지 않으면 코드만 보고 의도를 추론하느라 AI가 빗나가기 "
                f"쉽습니다. 현재 등급 {grade}, hotspot {hotspots.summary.hotspot}개 상태에서 "
                "의도 명확화는 다음 변경의 위험을 크게 줄입니다."
            ),
            "ai_prompt": (
                "docs/intent.md를 새로 작성해주세요. 세 섹션으로: "
                "## Why — 이 프로젝트가 왜 존재하는지, 어떤 문제를 푸는지, "
                "## What — 무엇을 만드는지 (체크박스 형태 목록), "
                "## Not — 명시적으로 하지 않을 것들. "
                "기존 README와 코드를 읽고 추론해서 초안을 작성하되, "
                "확신 없는 부분은 (TODO: 확인 필요) 표시하세요."
            ),
        },
        {
            "action": "openspec 도입으로 변경마다 명세부터",
            "reason": (
                "코드 변경 전에 명세를 작성하면 AI 협업의 결과물이 일관되게 누적됩니다. "
                "처음에는 작은 변경 한 건부터 시작해도 효과가 있습니다."
            ),
            "ai_prompt": (
                "이 프로젝트에 openspec 워크플로우를 시작합니다. "
                "1) openspec/ 디렉토리를 만들고, "
                "2) project.md 한 페이지에 프로젝트 컨텍스트 정리, "
                "3) 첫 변경 후보를 하나 골라 openspec/changes/<name>/ 아래 "
                "proposal.md(Why/What), design.md(How), tasks.md(체크리스트)를 작성해주세요. "
                "구현은 명세가 통과한 뒤에만 시작합니다."
            ),
        },
    ]
