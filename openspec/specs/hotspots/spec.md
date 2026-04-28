# hotspots Specification

## Purpose
The hotspots capability provides the `codexray hotspots <path>` CLI: it combines git-log change frequency with the dependency-graph coupling matrix to rank files into four hotspot categories (high-churn × high-coupling and the three other quadrants) and emits a deterministic JSON hotspots report. It is the priority input for ai-review.

## Requirements
### Requirement: Hotspots CLI 진입점
The system SHALL expose a `codexray hotspots <path>` command that prints a JSON hotspots report to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray hotspots <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray hotspots`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with top-level keys `schema_version`, `thresholds`, `summary`, and `files`. `thresholds`는 `change_count_median`(int)과 `coupling_median`(int)를 포함한다. `summary`는 `hotspot`, `active_stable`, `neglected_complex`, `stable` 네 키의 정수 카운트를 포함한다. `files` 배열의 각 원소는 `path`(string), `change_count`(int), `coupling`(int), `category`(string) 키만 포함한다.

#### Scenario: 스키마 키
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray hotspots`를 실행하면
- **THEN** 출력 객체는 `schema_version`, `thresholds`, `summary`, `files` 키를 모두 포함하고 `summary`는 4개 카테고리 키 모두 포함한다 (값이 0이라도)

#### Scenario: 파일 객체 키
- **WHEN** 출력 JSON에 파일이 포함될 때
- **THEN** 각 파일 객체는 `path`, `change_count`, `coupling`, `category` 네 키만 포함한다

### Requirement: 변경 빈도 계산
The system SHALL compute `change_count` per analyzed node by calling `git log --name-only --pretty=format:` once and counting non-empty file path lines. 분석 대상은 graph가 만든 노드들로 한정하며, 그 외 파일은 카운트하지 않는다. git history 어디에도 등장하지 않는 파일의 `change_count`는 0이다.

#### Scenario: 다 변경된 파일
- **WHEN** git history가 `a.py` 5번, `b.py` 1번, `c.py` 0번 변경했을 때
- **THEN** 시스템은 각각 `change_count` 5, 1, 0을 산출한다

#### Scenario: 분석 대상 외 파일 무시
- **WHEN** git history에 `README.md` 같은 비-소스 파일 변경이 많을 때
- **THEN** 시스템은 그 파일을 `files` 배열에 포함하지 않는다 (graph 노드 아님)

### Requirement: 결합도 계산
The system SHALL compute per-node `coupling` as `fan_in + fan_out + external_fan_out` using the existing graph metrics. 외부 의존이 많은 파일도 결합도에 반영된다.

#### Scenario: 결합도 합산
- **WHEN** 한 노드의 fan_in=2, fan_out=3, external_fan_out=4일 때
- **THEN** 시스템은 그 노드의 `coupling`을 9로 산출한다

### Requirement: 매트릭스 분류
The system SHALL classify each analyzed file into one of four categories using the medians of `change_count` and `coupling` across all analyzed files: `hotspot` (≥ both medians), `active_stable` (≥ change_count median, < coupling median), `neglected_complex` (< change_count median, ≥ coupling median), `stable` (< both medians).

#### Scenario: 분명한 hotspot
- **WHEN** 한 파일의 change_count와 coupling 모두 코드베이스 중앙값보다 높을 때
- **THEN** 시스템은 그 파일의 category를 `hotspot`으로 분류한다

#### Scenario: neglected_complex
- **WHEN** 한 파일의 change_count는 중앙값보다 낮고 coupling은 중앙값보다 높을 때
- **THEN** 시스템은 그 파일의 category를 `neglected_complex`로 분류한다

#### Scenario: 동일 중앙값 클램프
- **WHEN** 한 파일의 change_count가 정확히 중앙값과 같을 때
- **THEN** 시스템은 그 파일을 high(≥) 쪽으로 분류한다 (coupling도 같은 규칙)

### Requirement: 비-git 트리 폴백
The system SHALL detect non-git inputs by checking `git rev-parse --is-inside-work-tree` (or equivalent). git이 아니면 모든 파일의 `change_count`를 0으로 두고 stderr에 1줄 경고를 출력한 뒤 coupling 단일 차원으로 분류한다 (high coupling → `hotspot`, 그 외 → `stable`).

#### Scenario: 비-git 디렉토리
- **WHEN** 사용자가 git 저장소가 아닌 디렉토리를 인수로 전달하면
- **THEN** 시스템은 stderr에 git 비저장소 경고를 출력하고 모든 파일의 `change_count`를 0으로 산출한다

#### Scenario: 비-git 분류 폴백
- **WHEN** 비-git 입력에서 한 파일의 coupling이 중앙값 이상일 때
- **THEN** 시스템은 그 파일의 category를 `hotspot`으로 분류한다

### Requirement: 결정론적 정렬
The system SHALL sort the `files` array by `path` ascending.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 같은 트리에 대해 `codexray hotspots`를 두 번 실행하면 (git history 변동 없음)
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete hotspots output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray hotspots`를 실행하면
- **THEN** 시스템은 5초 이내에 JSON 출력을 완료한다

