# ai-review Specification

## Purpose
The ai-review capability provides the `codexray review <path>` CLI: it selects the top hotspot files and runs qualitative review through a shell-out adapter (codex or claude CLI), enforcing safety filters (empty `evidence_lines`, out-of-range line numbers, missing `comment` / `suggestion` / `limitations`, invalid `confidence`) before emitting a deterministic JSON review report. The CLI never imports an SDK directly — adapters keep the AI dependency at the process boundary.

## Requirements
### Requirement: Review CLI 진입점
The system SHALL expose a `codexray review <path>` command that runs AI qualitative review on the top N hotspot files and prints a JSON review report to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray review <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray review`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 어댑터 자동 감지와 강제 옵션
The system SHALL select an AI backend in this priority by default — `codex` then `claude` — and SHALL allow override via the `CODEXRAY_AI_BACKEND` environment variable accepting `auto`, `codex`, or `claude`. 선택된 backend 이름은 stderr에 1줄 안내로 출력하고 출력 JSON의 `backend` 필드에 기록한다. 어떤 backend도 사용 불가능하면 stderr에 "no AI backend available" 안내 후 종료 코드 0이 아닌 값으로 종료한다.

#### Scenario: 자동 codex 우선
- **WHEN** `codex` CLI는 PATH에 있고 `claude`도 있는 환경에서 `CODEXRAY_AI_BACKEND` 미설정 또는 `auto`일 때 `codexray review`를 실행하면
- **THEN** 시스템은 codex 어댑터를 사용하고 출력 `backend`는 `"codex"`다

#### Scenario: claude 폴백
- **WHEN** `codex`는 미설치, `claude`만 PATH에 있을 때 `codexray review`를 실행하면
- **THEN** 시스템은 claude 어댑터를 사용하고 출력 `backend`는 `"claude"`다

#### Scenario: 강제 claude
- **WHEN** `CODEXRAY_AI_BACKEND=claude`로 `codexray review`를 실행하면 (codex가 설치돼 있어도)
- **THEN** 시스템은 claude 어댑터를 사용한다

#### Scenario: backend 사용 불가
- **WHEN** codex/claude CLI 둘 다 미설치 상태에서 `codexray review`를 실행하면
- **THEN** 시스템은 stderr에 "no AI backend available" 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with top-level keys `schema_version`, `backend`, `files_reviewed`, `skipped`, and `reviews`. `reviews` 배열의 각 원소는 `path`(string), `dimensions`(객체), `confidence`(string), `limitations`(string)를 포함한다. `dimensions`는 `readability`, `design`, `maintainability`, `risk` 네 키를 가진다. 각 차원은 `score`(int 0-100), `evidence_lines`(비어있지 않은 int list), `comment`(string), `suggestion`(string)을 포함한다. `skipped` 배열의 원소는 `path`(string)와 `reason`(string).

#### Scenario: 스키마 키
- **WHEN** AI backend가 사용 가능하고 hotspot 파일이 있을 때 `codexray review`를 실행하면
- **THEN** 출력 객체는 `schema_version`, `backend`, `files_reviewed`, `skipped`, `reviews` 키를 모두 포함하고 `schema_version`은 정수 `1`이다

#### Scenario: 차원 객체 형식
- **WHEN** 한 review의 `dimensions.readability`가 존재할 때
- **THEN** 그 객체는 `score`, `evidence_lines`, `comment`, `suggestion` 네 키만 포함하고 `score`는 0 이상 100 이하 int, `evidence_lines`는 비어있지 않은 int list다

### Requirement: 근거 라인 안전장치
The system SHALL reject any AI review where any dimension has an empty `evidence_lines` list, includes line numbers outside the source file's line range, or has a missing `comment`/`suggestion` string. 거부된 파일은 `reviews`에 들어가지 않고 `skipped`에 `path`와 `reason` 1줄로 등록된다.

#### Scenario: 빈 evidence_lines
- **WHEN** AI 응답이 한 차원의 `evidence_lines`를 빈 list로 반환할 때
- **THEN** 그 파일은 `reviews`에 등록되지 않고 `skipped`에 `reason`이 비어있지 않은 string으로 등록된다

#### Scenario: 라인 번호 범위 초과
- **WHEN** AI 응답의 `evidence_lines`가 파일의 마지막 라인 번호보다 큰 값을 포함할 때
- **THEN** 그 파일은 `reviews`에 등록되지 않고 `skipped`에 등록된다

#### Scenario: 비어있는 comment
- **WHEN** AI 응답의 한 차원의 `comment`가 빈 문자열일 때
- **THEN** 그 파일은 `reviews`에 등록되지 않고 `skipped`에 등록된다

### Requirement: 신뢰도와 한계 안전장치
The system SHALL require each accepted review to include `confidence ∈ {"low", "medium", "high"}` and a non-empty `limitations` string. 둘 중 하나라도 누락되면 그 파일은 skipped로 격리된다.

#### Scenario: 누락된 confidence
- **WHEN** AI 응답에 `confidence` 키가 없거나 enum 외 값일 때
- **THEN** 그 파일은 `skipped`에 등록된다

#### Scenario: 빈 limitations
- **WHEN** AI 응답의 `limitations`가 빈 문자열일 때
- **THEN** 그 파일은 `skipped`에 등록된다

### Requirement: hotspot Top N 선택
The system SHALL select the top N hotspot files (category=`hotspot`, sorted by `change_count * coupling` descending; tie broken by `path` ascending) from the existing hotspots pipeline. N defaults to 5 and may be overridden via `CODEXRAY_AI_TOP_N` environment variable. hotspot 수가 N보다 적으면 모두 사용한다.

#### Scenario: 기본 N=5
- **WHEN** hotspot 수가 ≥5이고 `CODEXRAY_AI_TOP_N` 미설정일 때 `codexray review`를 실행하면
- **THEN** 시스템은 정확히 5 파일에 대해 AI 호출을 시도한다 (각 파일의 결과는 reviews 또는 skipped에 등록)

#### Scenario: hotspot 0개
- **WHEN** 코드베이스에 hotspot이 0개일 때 `codexray review`를 실행하면
- **THEN** 시스템은 `reviews`와 `skipped` 모두 빈 배열로 출력하고 `files_reviewed`는 0이다

#### Scenario: 환경변수 오버라이드
- **WHEN** `CODEXRAY_AI_TOP_N=3`을 설정하고 hotspot 수가 ≥3일 때 실행하면
- **THEN** 시스템은 정확히 3 파일에 대해 AI 호출을 시도한다

### Requirement: 프롬프트 결정론
The system SHALL build the per-file prompt deterministically from the file's content with line numbers prefixed (`{line_number}: ` 형식). 같은 파일 내용에 대해 같은 프롬프트 문자열이 생성된다.

#### Scenario: 동일 입력 동일 프롬프트
- **WHEN** 동일한 파일 내용에 대해 두 번 프롬프트를 빌드하면
- **THEN** 두 프롬프트 문자열이 완전히 동일하다

#### Scenario: 라인 번호 접두
- **WHEN** 한 줄로 구성된 파일에 대해 프롬프트를 빌드하면
- **THEN** 프롬프트는 `1: <원본 첫 줄>` 형식의 라인을 포함한다

### Requirement: 정렬
The system SHALL sort the `reviews` array by `path` ascending and the `skipped` array by `path` ascending.

#### Scenario: 결정론적 정렬
- **WHEN** 다수 파일을 review해 reviews와 skipped가 모두 비어있지 않을 때
- **THEN** 두 배열의 path는 모두 사전순 오름차순이다

