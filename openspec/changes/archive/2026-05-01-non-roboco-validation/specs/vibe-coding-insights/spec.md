## ADDED Requirements

### Requirement: 외부 OSS 데이터셋 기반 임계값·신호 풀 검증 절차

The system's vibe coding 3-axis thresholds (`strong / moderate / weak / unknown`) and signal pools SHALL be validated against an external OSS dataset before any threshold or signal-pool change is committed. The dataset SHALL include at least 5 repositories chosen for diversity along three dimensions: language ecosystem, project age, and AI-tool adoption stage.

#### Scenario: 검증 데이터셋 다양성 매트릭스
- **WHEN** 외부 검증 데이터셋이 정의되면
- **THEN** 데이터셋은 최소 5 개 레포를 포함하고, 다음 세 차원에서 *각각 2 개 이상의 분포* 를 가진다: 언어 생태계 (예: JS / Python / Rust / C 중 2 개 이상), 프로젝트 연령 (신생 < 3 년 / 성숙 ≥ 3 년 각각 1 개 이상), AI 도구 도입 단계 (AI 지시 문서 있음 / 없음 / 부분 도입 중 2 개 이상)

#### Scenario: 검증 시 AI 호출 차단
- **WHEN** 외부 검증 절차가 실행되면
- **THEN** 결정론 분석 (`build_vibe_insights` 의 신호 수집 + 3 축 상태 + blind_spot + process_proxies) 만 수집되고, AI narrative 또는 AI 카드 합성 호출은 *수행되지 않는다*

#### Scenario: 검증 결과 문서 위치 고정
- **WHEN** 외부 검증이 완료되면
- **THEN** 결과는 `docs/validation/non-roboco-validation-results.md` 에 다음 항목을 포함하여 기록된다: (1) 레포별 3 축 상태 표, (2) 축별 신호 풀 ratio 분포, (3) 누락된 신호 사례, (4) 과탐지 사례, (5) 임계값·신호 풀 권고안, (6) 후속 변경 제안

#### Scenario: 검증 데이터 raw 보존
- **WHEN** 외부 검증이 실행되면
- **THEN** 각 레포의 vibe_insights payload 는 `docs/validation/non-roboco-data/{repo-name}.json` 에 결정론적 직렬화 형식 그대로 저장되어 재분석이 가능하다

### Requirement: 임계값·신호 풀 변경의 근거 트레일

Any change that modifies vibe coding 3-axis thresholds or signal pools SHALL cite a corresponding entry in `docs/validation/non-roboco-validation-results.md` (or a successor results document) as the data justification. Changes lacking such a citation SHALL be rejected at proposal review.

#### Scenario: 임계값 조정 변경의 근거 인용
- **WHEN** 새 OpenSpec 변경이 `strong / moderate / weak` 임계값 비율을 수정하려 할 때
- **THEN** 변경의 proposal.md 는 결과 문서의 해당 권고 섹션을 명시적으로 인용 (파일 경로 + 섹션 헤딩) 한다

#### Scenario: 신호 풀 확장의 근거 인용
- **WHEN** 새 OpenSpec 변경이 3 축의 신호 풀에 새 파일/패턴을 추가하려 할 때
- **THEN** 변경의 proposal.md 는 결과 문서의 "누락된 신호 사례" 섹션 또는 "권고안" 섹션을 명시적으로 인용한다

### Requirement: 검증 중 false positive 즉시 수정의 경계

External validation MAY apply a *narrow* code fix during the same change ONLY when all three of the following conditions hold simultaneously: (1) the issue is a clear, undisputed false positive identifiable by visual inspection, (2) the fix touches at most one function and at most a few lines, (3) the existing test suite remains green and self-application result does not regress. Any change that violates one or more of these conditions SHALL be deferred to a follow-up change.

#### Scenario: 즉시 수정이 허용되는 경우
- **WHEN** 검증 중 사람이 봐도 명백한 false positive 가 발견되고, 수정이 1 함수 1–수 줄 범위이며, 기존 테스트와 자기 적용 결과가 변하지 않을 때
- **THEN** 본 변경 안에서 코드 수정을 *허용한다*

#### Scenario: 즉시 수정이 거부되는 경우
- **WHEN** 검증 중 발견된 이슈가 임계값 비율 변경, 신호 풀에 새 파일/패턴 추가, 다축에 걸친 로직 변경 중 하나라도 해당될 때
- **THEN** 본 변경에서 코드는 수정하지 *않고*, 결과 문서의 "후속 변경 제안" 섹션에 기록한다
