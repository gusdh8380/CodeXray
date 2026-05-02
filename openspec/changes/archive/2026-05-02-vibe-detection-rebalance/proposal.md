## Why

직전 archive `non-roboco-validation` 의 외부 OSS 9 개 검증에서 fastapi 가 `NOT DETECTED` 로 떨어지는 게 도구의 가장 큰 사용성 결함으로 드러났다. detection 게이트(`CLAUDE.md/AGENTS.md/.claude/.omc/openspec` 중 하나라도 있어야 함) 자체는 *AI 협업 흔적* 을 정확히 잡는다. 문제는 비감지 시 사용자에게 강제로 노출되는 *바이브코딩 시작 가이드* — 사용자가 fastapi 를 분석할 때 "CLAUDE.md 작성하세요" 같은 권유를 받는 게 부적절하다.

사용자(프로젝트 오너) 와 두 페르소나 (동료=비개발자 vibe coding 학습자 1순위, 본인=일반 OSS 분석가) 를 검토 후 옵션 A' 를 채택했다: *detection 게이트는 유지 + 비감지 시 vibe insights 섹션 통째로 비노출 + starter_guide 제거*. 이렇게 하면 동료 페르소나는 변함 없고 (자기 vibe 프로젝트는 항상 감지됨), 본인 페르소나는 fastapi 같은 일반 OSS 를 *깔끔한 일반 분석 도구* 로 활용 가능하다.

## What Changes

- **BREAKING** vibe-coding-insights 응답 schema 변경: 비감지 시 `starter_guide` 필드 제거. 비감지 프로젝트는 vibe_insights 응답 자체가 *없거나 null*.
- **REMOVED** `src/codexray/vibe_insights/starter_guide.py` 모듈 + 관련 테스트.
- **REMOVED** 프론트엔드 `StarterGuide` / `StarterGuideCard` / `CopyPromptBox` 컴포넌트 + `StarterGuideItem` 타입.
- **MODIFIED** `vibe_insights.builder.build_vibe_insights` — detected=False 분기에서 *None 반환* (이전: dict + starter_guide).
- **MODIFIED** `briefing_payload.build_briefing_payload` — vibe_insights 가 None 일 때 응답 페이로드의 해당 필드 자체를 None 으로 직렬화.
- **MODIFIED** 프론트엔드 `BriefingScreen` — `data.vibe_insights` 가 null/falsy 면 `<VibeInsightsSection />` 렌더링 건너뜀.
- **MODIFIED** SCHEMA_VERSION 6 → 7 bump (응답 형태 변경 → 캐시 자동 무효화).
- blind_spots / process_proxies 필드도 `detected=True` 일 때만 응답에 포함 (현재도 이미 그렇지만 spec 으로 못 박아 회귀 차단).

## Capabilities

### New Capabilities
없음.

### Modified Capabilities
- `vibe-coding-insights`: "바이브코딩 미감지 시 시작 가이드" 요구사항 제거. "결정론적 직렬화" 의 SCHEMA_VERSION 7 로 bump. 비감지 시 응답 형태가 *없음* 임을 명문화.
- `codebase-briefing`: briefing 페이로드의 vibe_insights 필드가 *옵셔널* 임을 명시 (비감지 프로젝트는 부재).
- `react-frontend`: VibeInsightsSection 이 vibe_insights 부재 시 렌더링 건너뜀을 명문화. StarterGuide 컴포넌트 제거.

## Impact

- **변경 영향 코드**:
  - 백엔드: `src/codexray/vibe_insights/builder.py`, `src/codexray/vibe_insights/__init__.py`, `src/codexray/vibe_insights/starter_guide.py` (삭제), `src/codexray/web/briefing_payload.py`, `src/codexray/web/ai_briefing.py` (시작 가이드 prompt 부분 제거 검토)
  - 프론트엔드: `frontend/src/lib/api.ts`, `frontend/src/components/briefing/BriefingScreen.tsx`, `frontend/src/components/briefing/VibeInsightsSection.tsx` (StarterGuide 분기 제거 → 컴포넌트 단순화)
  - 테스트: `tests/vibe_insights/` 의 starter_guide 관련 테스트 제거, 비감지 시 응답 None 테스트 추가
- **API 호환성**: BREAKING — 기존 클라이언트가 `starter_guide` 필드를 기대하면 깨짐. 그러나 본 도구는 단일 SPA 클라이언트라 영향 범위 제한적.
- **캐시**: SCHEMA_VERSION 6 → 7 bump 로 자동 무효화. 사용자 액션 불필요.
- **문서**:
  - 자기 적용 검증: `docs/validation/vibe-detection-rebalance-self.md`
  - fastapi 적용 검증: `docs/validation/vibe-detection-rebalance-fastapi.md` (vibe insights 섹션 사라짐 + 일반 분석 정상 노출 확인)
- **사용자 가시 변화**:
  - 동료 페르소나 (자기 vibe 프로젝트): 변화 없음
  - 본인 페르소나 (fastapi 등 일반 OSS): vibe insights 섹션이 사라지고 What/How Built/Current State/Next Actions/미시 분석 9/그래프 4 만 노출
- **README 보강 검토** (별도 변경): vibe coding 처음 시작하는 사용자를 위해 외부 자료 (Anthropic Best Practices, OpenAI Codex AGENTS.md guide 등) 링크. 본 변경 범위 밖.
