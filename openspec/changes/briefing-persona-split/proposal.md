## Why

CodeXray의 브리핑 영역(상단)과 상세 분석 토글(하단)이 *둘 다 시니어 개발자도, 비개발자도* 만족시키려고 가운데로 흘러서 양쪽 다 어정쩡한 상태가 되었다. 특히 Next Actions의 `ai_prompt` 필드는 비개발자 바이브코더가 다음 AI 세션에 그대로 들고 가서 쓰라는 목적인데, 한 문단짜리 단일 명령 형태라 새 세션에서 컨텍스트 결손·검증 가이드 부재·회귀 위험 안내 없음 문제가 생긴다. `docs/intent.md` 페르소나 우선순위를 비개발자 1순위로 못 박은 직후이므로 (2026-04-30), 그 결정과 가장 어긋나 있는 브리핑·Next Actions부터 정렬한다.

## What Changes

- 브리핑 영역(상단) 페르소나를 비개발자 100%로 못 박는다 — `codebase-briefing` 스펙이 청자·톤·메트릭 용어 차단을 명시한다.
- Next Actions의 `ai_prompt`를 3단 구조로 보강한다 — `[현재 프로젝트] / [작업 단계] / [끝나고 확인할 것]` 같은 자족적 컨텍스트 + 검증 체크리스트를 갖춘 형태. 비개발자가 새 AI 세션에 그대로 복사해서 쓸 수 있어야 한다.
- 위/아래 페르소나 분리를 `web-ui` 스펙에 명문화 — 브리핑 = 비개발자 영역, 상세 분석 토글 = 개발자 영역이라는 영역 책임 분리.
- 상세 분석 토글(하단)은 손대지 않는다 — 정의상 개발자 영역, 현재 톤 유지.
- `PROMPT_VERSION`을 bump해 캐시를 무효화한다 (스펙 차원 변경 아님, 구현 디테일).
- 검토 경고 배너는 유지하고 표현을 비개발자 친화적으로 다듬는다.

## Capabilities

### New Capabilities

(없음 — 기존 capability의 시나리오만 갱신)

### Modified Capabilities

- `codebase-briefing`: 브리핑 영역 청자가 비개발자 100%이며 메트릭 용어를 평어로 풀어 써야 한다는 시나리오를 추가/강화한다.
- `vibe-coding-insights`: Next Actions의 `ai_prompt` 필드가 3단 구조(이해→작업→검증)를 가져야 한다는 시나리오를 추가한다. 기존 "행동+왜+증거" 시나리오는 유지.
- `web-ui`: 브리핑 영역과 상세 분석 토글의 청자 페르소나가 다르다(비개발자 vs 개발자)는 영역 분리 시나리오를 추가한다.

## Impact

- **코드**: `src/codexray/web/ai_briefing.py`의 `build_ai_briefing_prompt` 톤 규칙 강화 + `ai_prompt` 3단 템플릿 지시. `src/codexray/vibe_insights/starter_guide.py`의 3개 항목도 같은 3단 구조로 통일.
- **버전**: `PROMPT_VERSION` v5-categorized-actions → v6-persona-split. `SCHEMA_VERSION`은 변경 없음 (필드 구조 동일, 문자열 내용만 더 길어짐).
- **캐시**: `~/.cache/codexray/ai-briefing/` 자동 무효화 (prompt_version 키).
- **프론트엔드**: `NextActionsSection.tsx`에서 길어진 `ai_prompt` 가독성 검토. 필요 시 카드 collapse 토글 도입(구현 단계 판단).
- **검증 자료**: `docs/validation/briefing-persona-split-self.md` (CodeXray 자기 적용), `docs/validation/briefing-persona-split-civilsim.md` (선택).
- **Intent 정렬**: `docs/intent.md` 직전 수정과 직접 정렬. 페르소나 분열 함정 학습이 코드까지 내려오는 첫 변경.
- **외부 호환성**: AI 브리핑 응답의 JSON 키는 동일. 값(문자열)만 길어지므로 기존 소비자(briefing_payload.py, NextActionsSection.tsx) 변경 최소.
