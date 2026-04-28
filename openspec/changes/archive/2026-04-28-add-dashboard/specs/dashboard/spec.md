## ADDED Requirements

### Requirement: Dashboard CLI 진입점
The system SHALL expose a `codexray dashboard <path>` command that prints a single self-contained HTML document to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray dashboard <path>`를 실행하면
- **THEN** 시스템은 stdout에 HTML 문서를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray dashboard`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 스키마 버전 마커
The system SHALL include the comment `<!-- codexray-dashboard-v1 -->` exactly once near the top of the HTML output.

#### Scenario: v1 마커 존재
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray dashboard`를 실행하면
- **THEN** 출력의 첫 5줄 안에 `<!-- codexray-dashboard-v1 -->` 마커가 정확히 1번 등장한다

### Requirement: 인라인 데이터 블록
The system SHALL include six `<script type="application/json">` blocks with ids `codexray-data-inventory`, `codexray-data-graph`, `codexray-data-metrics`, `codexray-data-entrypoints`, `codexray-data-quality`, `codexray-data-hotspots`. 각 블록 내용은 해당 명령(`codexray <name>`)이 출력하는 JSON과 동일하거나 호환되는 표현이다.

#### Scenario: 6개 블록 모두 등장
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray dashboard`를 실행하면
- **THEN** 출력 HTML은 6개 id의 `<script type="application/json">` 블록을 모두 포함한다

#### Scenario: 블록 내용은 유효 JSON
- **WHEN** 출력 HTML의 인라인 데이터 블록을 추출해 파싱하면
- **THEN** 6개 블록 모두 JSON으로 파싱 가능하다

### Requirement: D3 자산 로드
The system SHALL include exactly one `<script src=".../d3@7..."></script>` tag pointing to D3 v7 from a public CDN.

#### Scenario: D3 v7 스크립트 태그
- **WHEN** 출력 HTML을 검사하면
- **THEN** 정확히 한 `<script>` 태그의 `src`가 `d3@7` 문자열을 포함한다

### Requirement: 헤더 섹션
The system SHALL include a header section displaying: codebase path, generation date (ISO-8601 local), and overall quality grade with score from `quality.overall`. quality가 측정 불가일 때(`overall.score == null`)는 grade/score 자리에 `N/A`로 표기한다.

#### Scenario: 헤더 정보
- **WHEN** quality.overall.grade가 `D`이고 score가 40인 코드베이스에서 실행할 때
- **THEN** HTML 본문 텍스트에 codebase path, 날짜, 그리고 `D`와 `40`이 모두 등장한다

#### Scenario: 측정 불가 quality
- **WHEN** quality.overall.score가 null인 빈 트리에서 실행할 때
- **THEN** HTML 헤더 영역에 `N/A` 텍스트가 등장한다

### Requirement: 결정론
The system SHALL produce identical HTML bytes on repeated runs of the same input WHEN the date does not change between runs.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 같은 트리에 대해 `codexray dashboard`를 두 번 같은 날짜에 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete dashboard output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray dashboard`를 실행하면
- **THEN** 시스템은 5초 이내에 HTML 출력을 완료한다
