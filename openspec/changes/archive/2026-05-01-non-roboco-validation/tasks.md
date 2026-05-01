## 1. 검증 대상 레포 준비

- [x] 1.1 사용자에게 보유한 OSS 로컬 경로 확인 (vite, fastapi, ruff, sqlite, anthropic-cookbook, nx, 사용자 보유 dogfood 1 개 — design.md 결정 1 의 다양성 매트릭스 충족 여부 점검)
- [x] 1.2 보유하지 않은 레포는 본 변경 범위에서 제외하고 그 사실을 결과 문서에 기록 (design.md Open Question 정책)
- [x] 1.3 분석 가능한 레포가 다양성 매트릭스 (언어 2+ / 연령 신생·성숙 각 1+ / AI 도구 도입 단계 2+) 를 충족하는지 검증, 미달 시 사용자와 추가 후보 협의

## 2. 일괄 분석 스크립트

- [x] 2.1 `scripts/validate_external_repos.py` 신규 작성 — 인자: 레포 경로 리스트 (텍스트 파일 또는 CLI 인자), 출력: `docs/validation/non-roboco-data/{repo}.json`
- [x] 2.2 스크립트는 `build_briefing_payload` 의 결정론 부분만 호출 (AI narrative / AI 카드 합성 차단) — 검증 시 AI 호출 차단 시나리오 충족
- [x] 2.3 출력 JSON 은 `vibe_insights` payload 전체 + 각 축의 ratio + blind_spots + process_proxies 포함, 결정론적 직렬화 형식 그대로
- [x] 2.4 콘솔 요약: 레포명 / 3 축 상태 한 줄 요약 / 분석 소요 시간
- [x] 2.5 단위 테스트 1–2 개 추가 (`tests/scripts/test_validate_external_repos.py`) — 작은 fixture 레포 1 개로 스크립트가 JSON 출력을 정상 생성하는지 확인

## 3. 데이터 수집 실행

- [x] 3.1 1 단계에서 확정한 레포 리스트로 스크립트 실행, `docs/validation/non-roboco-data/*.json` 생성 확인
- [x] 3.2 분석 실패 케이스 (예: git history 없음, 거대 레포 타임아웃) 가 있으면 원인을 결과 문서 부록에 기록
- [x] 3.3 자기 적용 결과 (CodeXray 자체) 도 같은 형식으로 1 개 더 수집해 비교 기준점으로 추가

## 4. 분포 분석 + 권고안 작성

- [x] 4.1 `docs/validation/non-roboco-validation-results.md` 신규 작성, 다음 6 섹션 모두 채움:
  - [x] 4.1.1 레포 × 3 축 상태 매트릭스 표
  - [x] 4.1.2 축별 신호 풀 ratio 분포 (수치 또는 텍스트 히스토그램)
  - [x] 4.1.3 누락된 신호 사례 (사람이 보면 잘된 것 같은데 weak 으로 분류된 케이스)
  - [x] 4.1.4 과탐지 사례 (도구가 strong 으로 분류했지만 빈약한 케이스)
  - [x] 4.1.5 권고안 — 임계값 (그대로/조정), 신호 풀 추가 후보, blind spot 추가 후보
  - [x] 4.1.6 후속 변경 제안 — `vibe-thresholds-tune` 또는 `vibe-signal-pool-expand` 등 별도 변경의 명세

## 5. 명백한 false positive 즉시 수정 (조건 충족 시에만)

- [x] 5.1 분포 분석 중 발견된 이슈가 design.md 결정 5 의 3 조건 (명백한 false positive / 1 함수 수 줄 / 회귀 없음) 을 모두 만족하는지 점검
- [x] 5.2 조건 충족 항목만 코드 수정 — 그 외는 모두 결과 문서의 "후속 변경 제안" 섹션으로 이관
- [x] 5.3 수정 직후 `uv run pytest tests/ -q` 통과 확인 (309 → 309 또는 309 + 1–2 신규 테스트)
- [x] 5.4 자기 적용 재실행 (CodeXray → CodeXray) 으로 회귀 없음 확인 — 직전 archive 의 자기 적용 결과 (`docs/validation/vibe-insights-realign-self.md`) 와 큰 차이 없는지 비교

## 6. 검증 + 문서화

- [x] 6.1 `uv run pytest tests/ -q` 전체 통과 (기존 309 + 신규 1–2)
- [x] 6.2 `openspec validate non-roboco-validation --strict` 통과
- [x] 6.3 결과 문서가 spec 의 4 시나리오 (다양성 매트릭스 / AI 차단 / 결과 문서 위치 / raw 데이터 보존) 를 모두 만족하는지 자가 점검
- [x] 6.4 CLAUDE.md "Current Sprint" 갱신 — 본 변경의 결과 + 후속 변경 후보 (`vibe-thresholds-tune` 등) 명시
- [x] 6.5 git commit (atomic 단위, 단일 PR 가정)

## 7. Archive

- [x] 7.1 `openspec archive non-roboco-validation` (실패 시 incomplete 태스크 점검 후 재시도)
- [x] 7.2 archive 후 main spec 동기화 확인 (`openspec/specs/vibe-coding-insights/spec.md` 에 ADDED 항목 3 개 반영됐는지)
- [x] 7.3 후속 변경 후보를 CLAUDE.md 와 결과 문서에 최종 정리
