## Why

직전 archive `vibe-detection-rebalance` 에서 starter_guide 모듈·컴포넌트를 완전 제거했다 (옵션 A' 채택, 비-AI OSS 사용자에게 부적절한 권유 차단이 목적). 부작용으로 *vibe coding 처음 시작하는 사용자가 도구 안에서 학습 자료를 찾을 진입점이 사라짐*. design.md Open Question 1 에서 "안내 안 보여줌" 을 채택했으나, 진입점 자체가 필요하다는 결정은 별도 변경으로 분리됐다.

본 변경은 그 진입점을 *도구 화면이 아니라 README 에* 마련한다 — 도구 사용자가 vibe coding 자체를 배우려고 할 때 신뢰할 만한 외부 자료로 안내하는 가벼운 문서 변경.

## What Changes

- README.md 에 "Vibe Coding 처음 시작하기" 섹션 추가 — 외부 학습 자료 링크 모음.
- 자료 셋은 `EvaluationPhilosophyToggle.tsx` 의 8 번 섹션 (출처 인용) 과 일관되게 유지: Anthropic, OpenAI Codex, Karpathy, Simon Willison, Kent Beck, Geoffrey Huntley, Birgitta Böckeler, Will Larson, GitHub Spec Kit, Cursor/Cline/Aider.
- 각 자료에 *왜 이걸 봐야 하는지* 한 줄 요약 동봉 (단순 링크 덤프 회피).
- vibe-coding-insights capability 에 "학습 자료 외부 참조 진입점 유지" 요구사항 추가 — README 가 학습 진입점이라는 사실을 spec 으로 못 박아 회귀 차단.

## Capabilities

### New Capabilities
없음.

### Modified Capabilities
- `vibe-coding-insights`: ADDED 요구사항 1 개 — 도구가 starter_guide 화면 진입점을 제공하지 않는 대신 README 에 외부 학습 자료 셋이 *항상 유지* 되어야 함을 명시.

## Impact

- 신규/수정 파일: `README.md` (주요 변경), `openspec/specs/vibe-coding-insights/spec.md` (ADDED 1 개 — archive 시 sync)
- 영향 받는 코드: 없음 (순수 문서)
- 캐시 / 버전: 영향 없음 (PROMPT_VERSION/SCHEMA_VERSION bump 불필요)
- 테스트: 추가 안 함 (외부 링크 유효성은 수동 점검)
- 사용자 가시 변화:
  - 도구 화면: 변화 없음 (옵션 A' 유지)
  - README 를 읽는 사용자: vibe coding 학습 진입점 확보
