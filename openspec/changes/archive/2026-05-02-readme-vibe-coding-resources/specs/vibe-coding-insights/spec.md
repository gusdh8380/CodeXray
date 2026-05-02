## ADDED Requirements

### Requirement: vibe coding 학습 자료 외부 참조 진입점
The project's `README.md` SHALL maintain a section titled "Vibe Coding 처음 시작하기" (or equivalent Korean heading) that lists 8–10 external learning resources covering vibe coding fundamentals. The resource set SHALL be kept *consistent* with the EvaluationPhilosophyToggle component's "평가 기준의 출처" section (currently `frontend/src/components/briefing/EvaluationPhilosophyToggle.tsx` Section 8). When one is updated, the other SHALL be reviewed for synchronization.

#### Scenario: README 학습 자료 섹션 존재
- **WHEN** 프로젝트 루트의 `README.md` 가 검사되면
- **THEN** README 는 "Vibe Coding 처음 시작하기" (또는 동등 한국어 제목) 섹션을 포함하고, 그 섹션은 외부 학습 자료 8–10 개를 *제목 + 한 줄 요약 + 링크* 형식으로 나열한다

#### Scenario: 자료 셋이 평가 철학 토글과 동기화
- **WHEN** README 의 학습 자료 섹션과 EvaluationPhilosophyToggle 의 8 번 섹션이 비교되면
- **THEN** 두 곳의 자료 셋 (저자/저작 이름 단위) 은 *동일* 하다. 한 곳의 자료를 추가/제거할 때 다른 곳도 함께 갱신해야 한다 (PR 리뷰에서 명시적 점검 대상)

#### Scenario: 한 줄 요약 동봉
- **WHEN** README 학습 자료 섹션의 각 항목이 작성되면
- **THEN** 각 항목은 단순 링크가 아니라 *왜 이 자료를 봐야 하는지* 한국어 한 줄 요약을 포함한다 (예: "Anthropic — Claude Code Best Practices: CLAUDE.md 작성 원칙")
