## Why

직전 archive 인 `vibe-insights-realign` 으로 3축(intent/verification/continuity) + 4단계 상태(strong ≥70%, moderate ≥40%, weak ≥10%, unknown) 가 도입됐지만 **자기 적용(CodeXray → CodeXray) 1 회 데이터** 만으로 검증됨. 이 단일 데이터는 ROBOCO/OMC 컨벤션 편향과 임계값 적정성을 입증할 수 없고, README purpose 휴리스틱이 일반 OSS 의 다양한 README 스타일에 어떻게 반응하는지도 미지수다. 외부 OSS 5–7 개로 분포 데이터를 모아야 다음 임계값·신호 풀 조정 변경이 근거를 가지고 들어갈 수 있다.

## What Changes

- 외부 OSS 일괄 분석 스크립트 추가 (`scripts/validate_external_repos.py`) — 레포 경로 리스트를 받아 결정론 분석을 돌리고 vibe_insights 페이로드 + 3 축 ratio + blind spot 응답을 JSON 으로 수집. AI 호출은 **하지 않음** (편향·비용 차단).
- 검증 결과 문서 `docs/validation/non-roboco-validation-results.md` 추가 — 각 레포 결과 표 + 3 축 분포 통계 + 신호별 false positive/negative 사례 + 임계값·신호 풀 조정 권고.
- `vibe-coding-insights` capability 에 **검증 방법론 시나리오** 추가 — 3 축 임계값과 신호 풀이 외부 데이터로 주기적으로 점검돼야 한다는 요구사항을 spec 화 (다음 임계값 변경의 근거 트레일).
- 필요 시 데이터에서 **명백한 false positive 만 즉시 수정** (예: 한 줄짜리 README 키워드 매칭). 큰 임계값 조정·신호 풀 추가는 본 변경에서 하지 않고 후속 변경(`vibe-thresholds-tune` 등)으로 분리.

## Capabilities

### New Capabilities
없음 — 일괄 분석 스크립트는 dev 도구로 새 capability 가 아님.

### Modified Capabilities
- `vibe-coding-insights`: 3 축 임계값과 신호 풀의 외부 검증 절차를 spec 요구사항으로 추가. 검증 데이터셋·결과 문서 위치를 고정해 회귀 추적 가능하게 함.

## Impact

- 신규 파일: `scripts/validate_external_repos.py`, `docs/validation/non-roboco-validation-results.md`
- 영향 받는 코드: 없음 (스크립트는 기존 `codexray.web.briefing_payload` / `codexray.vibe_insights.builder` 의 결정론 부분만 재사용). `src/` 변경은 명백한 false positive 수정 시에만 최소.
- 의존성: 추가 패키지 없음 (외부 레포 clone 은 사용자가 사전 준비; 스크립트는 로컬 경로만 받음).
- 캐시: AI 호출 안 하므로 PROMPT_VERSION/SCHEMA_VERSION bump 불필요.
- 테스트: 309 유지 + 스크립트 단위 테스트 1–2 개 추가.
