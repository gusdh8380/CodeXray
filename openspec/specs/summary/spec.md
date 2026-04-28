# summary Specification

## Purpose
The summary capability composes existing quality, hotspot, metrics, entrypoint, and inventory outputs into deterministic strengths, weaknesses, and next-action lists with evidence on every item. It feeds `codexray report` and the web Overview/Report views so users can quickly decide what is working, what is risky, and what to inspect next before diving into lower-level analyzer details.

## Requirements
### Requirement: Summary builder
The system SHALL provide a `build_summary(quality, hotspots, metrics, entrypoints, inventory)` builder that produces a deterministic JSON summary of the top 3 strengths, top 3 weaknesses, and top 3 next actions for an analyzed codebase, with mandatory evidence citation on every item.

#### Scenario: 결정론적 출력
- **WHEN** 같은 quality·hotspots·metrics·entrypoints·inventory 입력으로 build_summary를 호출하면
- **THEN** 시스템은 같은 strengths / weaknesses / actions 항목을 같은 정렬 순서로 반환한다

#### Scenario: 근거 의무 인용
- **WHEN** strength·weakness·action 항목이 생성되면
- **THEN** 각 항목은 비어있지 않은 evidence(file path 또는 dimension 이름 + 수치 또는 등급)를 의무 포함한다

#### Scenario: Top 3 cap
- **WHEN** 룰이 3개 초과 항목을 산출하면
- **THEN** 시스템은 severity tier 우선 정렬 후 상위 3개만 반환한다

#### Scenario: 항목 부족 fallback
- **WHEN** 룰이 1개 미만 항목을 산출하면
- **THEN** 시스템은 항목 list를 빈 tuple로 반환하고 "특이사항 없음" 의미를 외부가 표현할 수 있게 한다

### Requirement: 강점 룰
The system SHALL extract strengths from the inputs using deterministic rules that prefer A/B grade quality dimensions, stable hotspot ratios, DAG structure, and active-stable top hotspots.

#### Scenario: A/B grade 차원
- **WHEN** quality.dimensions에 grade A 또는 B 차원이 있으면
- **THEN** 시스템은 해당 차원을 강점 항목에 포함하고 evidence에 dimension name·score·grade를 인용한다

#### Scenario: stable ratio 강점
- **WHEN** hotspots.summary의 stable count가 전체 hotspot 분류 합의 50% 이상이면
- **THEN** 시스템은 "stable file 비중이 높음" 강점 항목을 추가하고 evidence에 stable count·total을 인용한다

#### Scenario: DAG 강점
- **WHEN** metrics.graph.is_dag이 true이면
- **THEN** 시스템은 "순환 의존 없음" 강점 항목을 추가하고 evidence에 node_count를 인용한다

#### Scenario: active_stable top hotspot
- **WHEN** Top hotspot의 category가 active_stable이면
- **THEN** 시스템은 "활발한 영역의 결합도가 낮음" 강점 항목을 추가하고 evidence에 path·change_count를 인용한다

### Requirement: 약점 룰
The system SHALL extract weaknesses from the inputs using deterministic rules that prefer D/F grade quality dimensions, neglected_complex files, large SCCs, and hotspot top files.

#### Scenario: D/F grade 차원
- **WHEN** quality.dimensions에 grade D 또는 F 차원이 있으면
- **THEN** 시스템은 해당 차원을 약점 항목에 포함하고 evidence에 dimension name·score·grade를 인용한다

#### Scenario: neglected_complex 파일
- **WHEN** hotspots.files에 category가 neglected_complex인 파일이 1개 이상 있으면
- **THEN** 시스템은 "neglected_complex 파일이 있음" 약점 항목을 추가하고 evidence에 Top 1 path·coupling을 인용한다

#### Scenario: 순환 의존
- **WHEN** metrics.graph.largest_scc_size가 1보다 크면
- **THEN** 시스템은 "순환 의존 발견" 약점 항목을 추가하고 evidence에 scc size·예시 node를 인용한다

#### Scenario: hotspot category top
- **WHEN** Top hotspot의 category가 hotspot이면
- **THEN** 시스템은 "Top hotspot 위험" 약점 항목을 추가하고 evidence에 path·change_count·coupling·priority(change×coupling)를 인용한다

### Requirement: 다음 행동 매핑
The system SHALL produce next-action items mapped from each weakness via a deterministic dictionary so that every weakness yields at most one corresponding action.

#### Scenario: 약점-행동 매핑 일관
- **WHEN** weakness가 test 차원 D/F이면
- **THEN** 다음 행동에 "characterization test 우선 보강" 항목이 추가되고 evidence에 같은 dimension name·grade를 인용한다

#### Scenario: 매핑 누락 안전 장치
- **WHEN** weakness 룰이 새로 추가되었으나 다음 행동 매핑이 정의되지 않았으면
- **THEN** 시스템은 행동 list에서 그 weakness를 건너뛰고 명시 매핑이 있는 항목만 포함한다

### Requirement: JSON 직렬화
The system SHALL serialize the summary result with `schema_version: 1`, deterministic key ordering, and stable item order.

#### Scenario: schema_version 포함
- **WHEN** summary를 JSON으로 직렬화하면
- **THEN** 출력의 최상위 객체는 `schema_version` 키를 포함하고 값은 1이다

#### Scenario: 정렬 결정론
- **WHEN** 같은 입력으로 직렬화를 두 번 수행하면
- **THEN** stdout 바이트가 동일하다
