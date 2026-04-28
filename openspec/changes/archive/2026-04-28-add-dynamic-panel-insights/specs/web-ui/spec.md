## MODIFIED Requirements

### Requirement: Result rendering
The system SHALL render analysis results inline in the result panel as readable decision-oriented HTML by default, while preserving raw JSON as secondary detail when JSON exists. The right side area SHALL be split into a senior insights panel (dynamic, AI-generated) and a junior learning context panel (static).

#### Scenario: JSON 계열 결과
- **WHEN** inventory, graph, metrics, entrypoints, quality, hotspots, or review 결과를 표시하면
- **THEN** 시스템은 요약, 해석, table 또는 breakdown을 포함하는 readable HTML을 렌더링하고 raw JSON을 collapsible detail로 제공한다

#### Scenario: 주니어 학습 컨텍스트 sidebar
- **WHEN** Overview, Inventory, Graph, Metrics, Entrypoints, Quality, Hotspots, or Report 결과를 표시하면
- **THEN** 시스템은 우측 영역에 해당 capability의 메트릭 개념과 일반 학습 컨텍스트를 한국어 정적 텍스트로 표시하고 AI 호출 없이 즉시 렌더링한다

#### Scenario: 시니어 인사이트 sidebar 자리
- **WHEN** Overview, Inventory, Graph, Metrics, Entrypoints, Quality, Hotspots, or Report 결과를 표시하면
- **THEN** 시스템은 우측 영역에 시니어 인사이트 패널 자리를 표시하고 사용자가 "Generate insights" 버튼을 누르기 전까지는 빈 상태와 안내 메시지를 보여준다

#### Scenario: Report 결과
- **WHEN** report 결과를 표시하면
- **THEN** 시스템은 Markdown report를 sectioned readable HTML로 렌더링하고 핵심 grade와 recommendation을 상단에 표시한다

#### Scenario: Dashboard 결과
- **WHEN** dashboard 결과를 표시하면
- **THEN** 시스템은 기존 dashboard HTML을 넓은 workspace iframe에 렌더링하고 고정된 작은 내부창처럼 보이지 않게 하며 시니어 인사이트 패널은 본 변경에서 비활성화한다

## ADDED Requirements

### Requirement: Senior insights generation
The system SHALL generate senior-developer panel insights from the raw analysis JSON of the active tab through the codex / claude CLI adapters as an explicit opt-in background job.

#### Scenario: 명시 인사이트 생성
- **WHEN** 사용자가 시니어 인사이트 패널의 "Generate insights" 버튼을 누르면
- **THEN** 시스템은 raw JSON을 입력으로 background insights job을 시작하고 진행 상태 fragment를 즉시 반환한다

#### Scenario: 인사이트 출력 형식
- **WHEN** background insights job이 완료되면
- **THEN** 시스템은 적어도 1개 risk와 적어도 1개 next-action을 포함하는 3~5개 불릿(관찰 한 줄 + 함의 한 줄) 형식의 한국어 시니어 인사이트 fragment를 반환한다

#### Scenario: 인사이트 polling
- **WHEN** background insights job이 실행 중이면
- **THEN** UI는 polling 중임과 cancel control을 표시하고 다른 탭과 주니어 패널은 계속 사용할 수 있음을 보여준다

#### Scenario: 인사이트 취소
- **WHEN** 사용자가 running insights job에서 Cancel을 누르면
- **THEN** 시스템은 job을 cancelled 상태로 표시하고 cancelled fragment를 반환한다

#### Scenario: 인사이트 응답 안전장치
- **WHEN** AI 응답이 빈 본문이거나 불릿이 1개 미만 또는 10개 초과이거나 risk 또는 next-action이 모두 없으면
- **THEN** 시스템은 결과를 skipped로 격리하고 "AI 응답이 형식에 맞지 않음" 안내 fragment를 반환한다

#### Scenario: Dashboard 탭 비활성화
- **WHEN** Dashboard 또는 Review 탭에서 시니어 인사이트 패널을 보면
- **THEN** 시스템은 본 변경에서는 인사이트 패널을 비활성화하고 비활성화 사유를 표시한다

### Requirement: Insights cache
The system SHALL cache senior insights to disk so the same input deterministically returns the same output, and the system SHALL provide explicit regeneration.

#### Scenario: 캐시 hit
- **WHEN** 사용자가 "Generate insights"를 눌렀고 같은 path · tab · raw JSON hash · adapter · prompt version 키의 캐시가 존재하면
- **THEN** 시스템은 background job을 시작하지 않고 즉시 캐시된 인사이트 fragment를 반환한다

#### Scenario: 캐시 miss 후 저장
- **WHEN** 캐시가 없고 background job이 안전장치를 통과한 인사이트를 생성하면
- **THEN** 시스템은 결과를 `~/.cache/codexray/insights/<sha256_key>.json`에 저장한다

#### Scenario: 강제 재생성
- **WHEN** 사용자가 인사이트 패널의 "다시 생성" 버튼을 누르면
- **THEN** 시스템은 기존 캐시를 무시하고 새 background job을 시작한다

#### Scenario: prompt version 무효화
- **WHEN** prompt version이 새 버전으로 올라간 후 사용자가 "Generate insights"를 누르면
- **THEN** 시스템은 이전 버전 캐시를 무시하고 새 background job을 시작한다

### Requirement: Insights AI fallback
The system SHALL keep the web UI usable when AI adapters are unavailable.

#### Scenario: AI 어댑터 미설정
- **WHEN** codex와 claude CLI 어댑터가 모두 사용 불가능하고 사용자가 "Generate insights"를 누르면
- **THEN** 시스템은 시니어 패널에 "AI 어댑터 미설정 — codex login 또는 claude login 필요" 안내를 표시하고 주니어 패널과 분석 결과는 정상 표시한다

#### Scenario: AI 호출 실패
- **WHEN** background insights job이 어댑터 오류로 실패하면
- **THEN** 시스템은 "AI 호출 실패 — 다시 시도" fragment를 반환하고 주니어 패널과 분석 결과는 영향받지 않는다
