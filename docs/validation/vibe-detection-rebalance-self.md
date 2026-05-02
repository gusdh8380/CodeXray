# vibe-detection-rebalance — 자기 적용 검증

**날짜**: 2026-05-02
**대상**: CodeXray 자체 분석 (동료 페르소나 시뮬레이션)
**페르소나**: 자기 vibe coding 프로젝트를 분석하는 사용자 — 화면 변화 없어야 함

## 자동 검증

- `uv run pytest tests/ -q` → **312 passed** (직전 archive 와 동일 수준)
- `cd frontend && npm run build` → 383KB JS / 38KB CSS (이전 385KB / 38KB 대비 -2KB, StarterGuide / StarterGuideCard / CopyPromptBox 컴포넌트 제거 효과)
- `openspec validate vibe-detection-rebalance --strict` → 통과
- `uv run ruff check src/codexray/vibe_insights/ src/codexray/web/briefing_payload.py src/codexray/web/ai_briefing.py scripts/` → 신규 위반 0건 (기존 E501 19건은 프로젝트 관행상 수용)

## 결정론 페이로드 검증

```
SCHEMA_VERSION = 5  (이전 4 에서 bump)
CodeXray: vibe_insights detected → 의도:strong | 검증:strong | 이어받기:strong
  next_actions categories: {'structural', 'code'} (count=2)
```

확인된 동작:
- vibe_insights 페이로드 정상 포함 (None 아님)
- 3 축 모두 strong → "carded weakness" 없음 → vibe_coding 카테고리 카드 0개 (예상대로 — 강한 프로젝트는 칭찬 또는 침묵)
- code/structural 카드는 fallback 합성으로 정상 노출

## 동료 페르소나 화면 시뮬레이션

브라우저 직접 확인 (별도 사용자 검증):
- vibe insights 섹션 정상 표시 (3 축 카드 + AI 종합 해석 + blind spot + 평가 철학 토글)
- 시작 가이드 영역 *부재* (이전: StarterGuide 분기에서 표시되던 "전통 방식 → 첫 걸음" 카드. 본 변경에서 컴포넌트 자체 제거)
- 화면 5 섹션 (정체 / 구조 / 현재 상태 / 바이브코딩 인사이트 / 다음 행동) 정상 노출
- ROBOCO 컨벤션이 모두 적용된 자기 프로젝트라 회귀 없음

## 회귀 차단 점검

직전 archive `vibe-insights-realign` self.md 와 비교:
- vibe insights 3 축 진단 동작 동일 (state 라벨, 신호 개수, 대표 근거 모두 변경 없음)
- blind spot 4 항목 노출 동일
- process proxies 보조 패널 동일
- 평가 철학 토글 8 섹션 동일
- ai_prompt v7 라벨 셋 유지

이전과 *완전히 같은 화면* — 동료 페르소나 영향 없음 확인.

## 결론

본 변경의 핵심 가치 — *"감지된 프로젝트는 영향 없음"* — 검증됨. 다음 단계: fastapi 페르소나 검증 (`docs/validation/vibe-detection-rebalance-fastapi.md`).
