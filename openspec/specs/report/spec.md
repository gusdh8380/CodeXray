# report Specification

## Purpose
The report capability provides the `codexray report <path>` CLI: it composes the outputs of the six analysis builders (inventory, graph, metrics, entrypoints, quality, hotspots) into a single one-page Markdown report with rule-based recommendations, written deterministically to stdout.
## Requirements
### Requirement: Report CLI 진입점
The system SHALL expose a `codexray report <path>` command that prints a Markdown report to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray report <path>`를 실행하면
- **THEN** 시스템은 stdout에 Markdown 문서를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray report`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 스키마 버전 마커
The system SHALL include the comment `<!-- codexray-report-v1 -->` exactly once near the top of the Markdown output.

#### Scenario: v1 마커 존재
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray report`를 실행하면
- **THEN** 출력의 첫 5줄 안에 `<!-- codexray-report-v1 -->` 마커가 정확히 1번 등장한다

### Requirement: 종합 등급 섹션
The system SHALL render a "## Overall Grade" section that shows the quality overall score/grade and a 4-row table for `coupling`, `cohesion`, `documentation`, `test` with columns `dimension`, `grade`, `score`, `detail`. 측정 불가 차원은 `grade`/`score` 셀에 `N/A`로 표기.

#### Scenario: 4차원 모두 측정
- **WHEN** 4차원 quality가 모두 측정 가능한 트리에서 실행할 때
- **THEN** 출력의 "Overall Grade" 표는 `coupling`, `cohesion`, `documentation`, `test` 4행을 포함한다

#### Scenario: N/A 표기
- **WHEN** documentation 차원이 측정 불가일 때
- **THEN** documentation 행의 `grade`와 `score` 셀은 `N/A` 문자열을 포함한다

### Requirement: 인벤토리 섹션
The system SHALL render an "## Inventory" section that includes a table with columns `language`, `file_count`, `loc`, `last_modified_at`. 인벤토리 결과가 빈 트리면 "(no source files)" 같은 안내 텍스트로 대체한다.

#### Scenario: 다국어 트리
- **WHEN** 트리에 Python·C# 파일이 있을 때
- **THEN** 출력의 "Inventory" 섹션은 두 언어를 표 행으로 포함한다

#### Scenario: 빈 트리
- **WHEN** 트리에 분석 대상 소스 파일이 없을 때
- **THEN** "Inventory" 섹션은 표 대신 빈 트리 안내 텍스트를 포함한다

### Requirement: 구조 요약 섹션
The system SHALL render a "## Structure" section listing: total node count, internal edge count, external edge count, largest SCC size, is_dag flag, total entrypoint count, and entrypoint kind distribution.

#### Scenario: 구조 키 모두 등장
- **WHEN** 임의의 유효한 코드베이스에서 실행할 때
- **THEN** "Structure" 섹션 본문은 `nodes`, `internal edges`, `external edges`, `largest SCC`, `entrypoints` 단어를 모두 포함한다

### Requirement: Top Hotspots 섹션
The system SHALL render a "## Top Hotspots" section listing up to 5 highest-priority hotspot files (category=`hotspot`, sorted by change_count × coupling descending; tie broken by `path` ascending). 각 항목은 path, change_count, coupling을 표기한다. hotspot가 0개면 "(no hotspots)" 텍스트로 대체.

#### Scenario: hotspots 존재
- **WHEN** hotspots.summary.hotspot이 5 이상일 때
- **THEN** "Top Hotspots" 섹션은 정확히 5 항목을 포함한다

#### Scenario: hotspots 없음
- **WHEN** hotspots.summary.hotspot == 0일 때
- **THEN** "Top Hotspots" 섹션은 "(no hotspots)" 안내 텍스트를 포함한다

### Requirement: 권고 섹션
The system SHALL render a "## Recommendations" section listing up to 5 deterministic rule-based recommendations sorted by priority. 가능한 룰: F 등급 차원, 사이클 (is_dag=False), Top hotspot, D 등급 차원, 진입점 부재. 권고가 0개면 "(no recommendations)" 텍스트.

#### Scenario: F 등급 차원 권고
- **WHEN** quality.test.grade == "F"일 때
- **THEN** Recommendations 섹션 항목 중 하나는 `test` 단어와 grade `F`를 본문에 포함한다

#### Scenario: 사이클 권고
- **WHEN** metrics.is_dag == False일 때
- **THEN** Recommendations 섹션 항목 중 하나는 "cycle" 또는 "SCC" 단어를 본문에 포함한다

#### Scenario: Top hotspot 권고
- **WHEN** hotspots.summary.hotspot >= 1일 때
- **THEN** Recommendations 섹션 항목 중 하나는 가장 큰 hotspot 파일의 path를 본문에 포함한다

### Requirement: 결정론
The system SHALL produce identical Markdown bytes on repeated runs of the same input WHEN the date does not change between runs.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 같은 트리에 대해 `codexray report`를 두 번 같은 날짜에 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete report output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray report`를 실행하면
- **THEN** 시스템은 5초 이내에 Markdown 출력을 완료한다

### Requirement: Strengths/Weaknesses/Actions section
The system SHALL render a "## Strengths" section, a "## Weaknesses" section, and a "## Next Actions" section in the Markdown report, each listing up to 3 deterministic rule-based items with mandatory evidence citation. The three sections SHALL appear after "## Overall Grade" and before "## Top Hotspots".

#### Scenario: 위치
- **WHEN** `codexray report <path>` Markdown 출력을 보면
- **THEN** "## Strengths", "## Weaknesses", "## Next Actions" 섹션이 "## Overall Grade" 다음, "## Top Hotspots" 이전 순서로 등장한다

#### Scenario: 항목 cap
- **WHEN** summary 빌더가 4개 이상 강점·약점·다음 행동 항목을 산출하면
- **THEN** Markdown 각 섹션은 정확히 3개 항목만 표시한다

#### Scenario: 항목 fallback
- **WHEN** summary 빌더가 어느 한 섹션에서 0개 항목을 산출하면
- **THEN** 해당 섹션은 항목 list 대신 "(특이사항 없음)" 안내 텍스트를 포함한다

#### Scenario: 근거 인용
- **WHEN** "Strengths", "Weaknesses", "Next Actions" 섹션 항목이 출력되면
- **THEN** 각 항목 본문은 file path 또는 dimension 이름과 score / grade / count 같은 수치 근거를 포함한다

#### Scenario: 결정론
- **WHEN** 같은 트리에 대해 `codexray report`를 두 번 같은 날짜에 실행하면
- **THEN** "Strengths", "Weaknesses", "Next Actions" 섹션의 stdout 바이트가 동일하다

