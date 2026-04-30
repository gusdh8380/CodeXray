## Why

자체 분석에서 드러난 메타 결함이 있다. 현재 "다음 행동" 섹션은 hotspot × coupling 시그널에 과의존해서 CLI dispatcher / API router 같은 **엔트리포인트 파일을 1·2위 위험으로 잘못 잡는다**. 이는 구조적 패턴(엔트리포인트는 본질적으로 결합도 높음)을 결함으로 오해하는 false positive다.

근본 원인 — 추천 엔진이 두 시그널만 보고 있고, 프레임워크 관용구를 모르며, 후처리 검증도 없다. "시니어 개발자가 동의할 추천"까지 가려면 시그널 다양화 + sanity filter 같은 큰 작업이 필요하지만 그건 별도 변경에서 다룬다.

본 변경은 **추천 품질 자체는 손대지 않고**, 사용자가 추천을 비판적으로 받아들이도록 두 가지를 한다: (1) 추천을 3개 카테고리(코드 / 구조 / 바이브코딩)로 분류해서 액션의 성격을 구분하고, (2) "AI 자동 생성이라 부정확할 수 있음, 검토 후 진행" 경고 배너를 붙인다. 추천 내용 검증은 후속 변경의 일이다.

## What Changes

- AI 프롬프트가 `next_actions`를 단일 평면 배열 대신 `category` 필드를 가진 항목들의 배열로 반환 (카테고리: `code` / `structural` / `vibe_coding`)
- 카테고리당 1~3개, 합계 최대 9개. 카테고리가 비어있어도 허용
- `vibe_coding` 카테고리는 AI가 직접 생성하지 않고 기존 `briefing.vibe_insights.next_actions` 또는 `vibe_insights.starter_guide` 를 재구성해서 채움 (중복 방지, 데이터 흐름 단순화)
- `AINextAction` 데이터 모델에 `category` 필드 추가 (선택적 → 필수 아님, 누락 시 `code` 기본값)
- briefing payload의 `next_actions`는 `[{action, reason, evidence, ai_prompt, category}]` 평면 리스트로 직렬화 (그룹화는 프론트엔드에서)
- 프론트엔드 `NextActionsSection` 이 카테고리별 3개 그룹으로 렌더링, 각 그룹에 한국어 헤더와 아이콘
- 다음 행동 섹션 상단에 amber 경고 배너 — "AI 자동 생성이라 그대로 적용 시 부적절할 수 있음. 검토 후 진행"
- `PROMPT_VERSION` v4 → v5 (캐시 자동 무효화)
- `SCHEMA_VERSION` 2 → 3 (응답 구조 변경)
- 추천 내용 정확도 / sanity filter / 프레임워크 인식 / 시그널 다양화는 **본 변경에서 다루지 않음** — 별도 후속 변경 `senior-grade-recommendations`로 위임

## Capabilities

### Modified Capabilities
- `codebase-briefing`: AI 해석 결과 구조에 `category` 필드 추가, 다음 행동의 3 카테고리 분류 시나리오, vibe_coding 카테고리 채우기 규칙
- `react-frontend`: Briefing 매크로 화면의 "지금 뭘 해야 해" 섹션이 카테고리별 그룹 + 경고 배너 렌더링

## Impact

- `src/codexray/web/ai_briefing.py` — AI 프롬프트 텍스트 + JSON 스키마 + AINextAction dataclass + parse_ai_briefing_response + PROMPT_VERSION 변경
- `src/codexray/web/briefing_payload.py` — `_build_next_actions` 가 vibe_coding 카테고리 합성 + SCHEMA_VERSION bump
- `frontend/src/lib/api.ts` — NextAction 타입에 `category` 필드 추가
- `frontend/src/components/briefing/NextActionsSection.tsx` — 3 그룹 + 경고 배너 렌더링
- `tests/test_ai_briefing.py` — parse_ai_briefing_response의 카테고리 처리 + 누락 fallback 테스트
- `tests/test_briefing.py` — 직렬화 어서션 갱신 (category 필드 + schema_version)
- `openspec/specs/codebase-briefing/spec.md`, `openspec/specs/react-frontend/spec.md` — 본 변경 archive 후 sync
