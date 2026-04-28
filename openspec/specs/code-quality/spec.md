# code-quality Specification

## Purpose
TBD - created by archiving change add-quality-quant. Update Purpose after archive.
## Requirements
### Requirement: Quality CLI 진입점
The system SHALL expose a `codexray quality <path>` command that prints a JSON quality report to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray quality <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray quality`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with top-level keys `schema_version`, `overall`, and `dimensions`. `overall`은 `score`(int 0~100)와 `grade`(string A/B/C/D/F)를 포함한다. `dimensions`는 `coupling`, `cohesion`, `documentation`, `test` 네 키를 가진 객체이며, 각 값은 `score`, `grade`, `detail`(object)을 포함한다. 측정이 불가능한 차원은 `score`와 `grade`가 `null`이고 `detail.reason`에 사유 문자열이 들어간다.

#### Scenario: 스키마 키
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray quality`를 실행하면
- **THEN** 출력 객체는 `schema_version`, `overall`, `dimensions` 키를 모두 포함하고 `dimensions`는 `coupling`, `cohesion`, `documentation`, `test` 네 키를 모두 포함한다

#### Scenario: 차원 점수 형식
- **WHEN** `dimensions`의 한 차원이 측정 가능할 때
- **THEN** 그 객체의 `score`는 0 이상 100 이하 정수이고 `grade`는 `A`, `B`, `C`, `D`, `F` 중 하나다

#### Scenario: 측정 불가 차원
- **WHEN** 한 차원의 측정 입력이 0(예: documentation에 Python·C# 파일 없음)일 때
- **THEN** 그 차원의 `score`와 `grade`는 모두 `null`이고 `detail.reason`은 비어있지 않은 문자열이다

### Requirement: 점수 → 등급 매핑
The system SHALL map numeric scores to letter grades using the fixed thresholds: A ≥ 90, B ≥ 75, C ≥ 60, D ≥ 40, F < 40.

#### Scenario: 경계 점수
- **WHEN** 점수가 정확히 90, 75, 60, 40일 때
- **THEN** 등급은 각각 `A`, `B`, `C`, `D`다

#### Scenario: 가장 낮은 등급
- **WHEN** 점수가 39 이하일 때
- **THEN** 등급은 `F`다

### Requirement: Coupling 차원
The system SHALL compute the coupling score from the average of `fan_in + fan_out` (internal edges only) across all graph nodes. 점수는 `max(0, min(100, 100 - avg * 10))`으로 계산하며 `detail`은 `avg_fan_inout`(float, 소수점 둘째 자리 반올림)과 `max`(int, 모든 노드 중 최대 fan_in+fan_out)를 포함한다.

#### Scenario: 결합도 0
- **WHEN** 그래프에 internal 엣지가 하나도 없을 때
- **THEN** 시스템은 coupling 점수 100, grade `A`를 산출한다

#### Scenario: 평균 결합도 2
- **WHEN** 모든 노드의 평균 fan_in+fan_out이 2일 때
- **THEN** 시스템은 coupling 점수 80, grade `B`를 산출한다

### Requirement: Cohesion 차원
The system SHALL group source files by their first two path segments (e.g., `src/codexray/...`는 그룹 `src/codexray`) and compute, per group, the ratio of internal edges that target a file in the same group. 코드베이스 cohesion 점수는 그룹별 비율의 (그룹 내 파일 수 가중) 평균에 100을 곱한 정수다. 첫 두 segment가 부족한 파일들은 단일 그룹 `(root)`로 묶인다.

#### Scenario: 단일 폴더 트리
- **WHEN** 트리의 모든 파일이 같은 첫 2단계 폴더에 있고 모든 internal 엣지가 그 폴더 내부로 갈 때
- **THEN** 시스템은 cohesion 점수 100, grade `A`를 산출한다

#### Scenario: 두 폴더 절반 응집
- **WHEN** 두 폴더에 각 1 파일씩, 그 파일들이 서로 internal 엣지로 가는(=교차 의존)·내부 엣지 0인 트리
- **THEN** 시스템은 cohesion 점수 0, grade `F`를 산출한다 (모든 엣지가 외부 그룹으로 감)

#### Scenario: 비어있는 internal 엣지
- **WHEN** 트리에 노드는 있지만 internal 엣지가 0개일 때
- **THEN** 시스템은 cohesion `score`, `grade`를 `null`로 설정하고 `detail.reason`을 명시한다

### Requirement: Documentation 차원
The system SHALL compute the documentation score using the ratio of documented Python and C# items.
- Python: 모듈/함수/클래스의 첫 statement가 `Expr(Constant(str))`인 비율 (AST 기반)
- C#: `public|internal|private|protected` 한정자가 붙은 클래스/메서드/구조체/인터페이스 선언 직전 비공백 라인이 `///`로 시작하면 documented
- 점수는 (documented / items_total) × 100. 측정 가능한 항목이 0이면 차원 점수와 등급을 `null`로 둔다.

#### Scenario: 모든 함수 docstring
- **WHEN** Python 파일의 모든 함수와 클래스가 docstring을 가질 때
- **THEN** 시스템은 documentation 점수 100, grade `A`를 산출한다

#### Scenario: 절반 documented
- **WHEN** 측정 가능한 항목 10개 중 5개가 documented일 때
- **THEN** 시스템은 documentation 점수 50, grade `D`를 산출한다

#### Scenario: 측정 항목 0
- **WHEN** Python·C# 파일이 트리에 없을 때
- **THEN** 시스템은 documentation `score`, `grade`를 `null`로 설정한다

### Requirement: Test 차원
The system SHALL identify test files by directory (`tests/`, `test/`, `__tests__/`, `Assets/Tests/`, `Assets/Scripts/Tests/` 그 하위) or file-name pattern (`test_*.py`, `*_test.py`, `*.test.ts`, `*.test.js`, `*.spec.ts`, `*.spec.js`, `*Tests.cs`, `*Test.cs`) and compute the ratio of test LoC to source LoC. 점수는 `min(100, ratio * 200)`(즉 ratio 0.5에서 만점)을 정수로 반올림한다. 소스 LoC가 0이면 차원 점수와 등급을 `null`로 둔다.

#### Scenario: 충분한 테스트
- **WHEN** 테스트 LoC가 소스 LoC의 0.5 이상일 때
- **THEN** 시스템은 test 점수 100, grade `A`를 산출한다

#### Scenario: 적은 테스트
- **WHEN** 테스트 LoC가 소스 LoC의 0.10일 때
- **THEN** 시스템은 test 점수 20, grade `F`를 산출한다

#### Scenario: 소스 0
- **WHEN** 트리에 분석 대상 소스 파일이 없을 때
- **THEN** 시스템은 test `score`, `grade`를 `null`로 설정한다

### Requirement: Overall 점수
The system SHALL compute `overall.score` as the rounded mean of all dimensions whose score is non-null. 모든 차원이 null이면 `overall.score`와 `overall.grade`도 null이다.

#### Scenario: 4차원 모두 측정
- **WHEN** 4차원 점수가 모두 80일 때
- **THEN** `overall.score`는 80, `overall.grade`는 `B`다

#### Scenario: 일부 차원 N/A
- **WHEN** 4차원 중 documentation만 null이고 나머지 3개가 각 60일 때
- **THEN** `overall.score`는 60, `overall.grade`는 `C`다

### Requirement: 결정론
The system SHALL produce identical stdout bytes on repeated runs of the same input.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 같은 트리에 대해 `codexray quality`를 두 번 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete quality output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray quality`를 실행하면
- **THEN** 시스템은 5초 이내에 JSON 출력을 완료한다

