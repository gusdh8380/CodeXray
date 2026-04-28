# web-ui Specification

## Purpose
The web-ui capability provides the `codexray serve` CLI: it runs a localhost FastAPI server (default `127.0.0.1:8080`) that exposes every CodeXray analysis builder and the AI review through a single htmx + Jinja2 page. Results render inline as decision-oriented HTML with a Korean senior-developer commentary sidebar, and AI review is an explicit opt-in background job with cancel and status polling. The capability ships without a JavaScript build pipeline to stay aligned with the project's local-first constraint.
## Requirements
### Requirement: Web UI CLI 진입점
The system SHALL expose a `codexray serve` command that starts a localhost web UI server for controlling CodeXray analysis commands.

#### Scenario: 기본 서버 실행
- **WHEN** 사용자가 `codexray serve`를 실행하면
- **THEN** 시스템은 `127.0.0.1:8080`에서 HTTP 서버를 시작한다

#### Scenario: 포트 지정
- **WHEN** 사용자가 `codexray serve --port 8090`을 실행하면
- **THEN** 시스템은 `127.0.0.1:8090`에서 HTTP 서버를 시작한다

#### Scenario: 브라우저 자동 열림 비활성화
- **WHEN** 사용자가 `codexray serve --no-browser`를 실행하면
- **THEN** 시스템은 서버를 시작하지만 브라우저를 자동으로 열지 않는다

### Requirement: 메인 페이지
The system SHALL serve a main page at `GET /` with a path input, recent path selector, analysis tabs, status text, and a result panel.

#### Scenario: 메인 페이지 로드
- **WHEN** 브라우저가 `GET /`를 요청하면
- **THEN** 시스템은 HTTP 200 HTML 응답을 반환하고 본문에 path input, status text, result panel, and analysis tabs를 포함한다

#### Scenario: 최근 path 저장
- **WHEN** 사용자가 UI에서 분석 path를 제출하면
- **THEN** 브라우저는 localStorage에 최근 path를 최대 5개까지 저장할 수 있다

#### Scenario: Overview 자동 로드
- **WHEN** 메인 페이지 JavaScript가 초기화되면
- **THEN** 브라우저는 기본 path로 Overview 탭을 자동 실행한다

### Requirement: htmx Jinja UI
The system SHALL implement the first web UI with server-rendered Jinja2 templates and htmx fragment swaps without a JavaScript build pipeline.

#### Scenario: htmx fragment swap
- **WHEN** 사용자가 Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, Dashboard, or Review 탭을 클릭하면
- **THEN** 브라우저는 htmx request를 보내고 result panel을 서버가 반환한 HTML fragment로 교체한다

#### Scenario: Active tab 표시
- **WHEN** 사용자가 analysis tab을 클릭하면
- **THEN** UI는 해당 tab을 active 상태로 표시한다

#### Scenario: Loading 표시
- **WHEN** analysis htmx request가 진행 중이면
- **THEN** UI는 result panel에 loading 상태를 표시하고 status text를 갱신한다

#### Scenario: Enter 재실행
- **WHEN** 사용자가 path input에서 Enter를 누르면
- **THEN** UI는 현재 active tab을 같은 path로 다시 실행한다

### Requirement: Path validation
The system SHALL validate submitted paths before running analysis.

#### Scenario: 유효한 디렉토리 path
- **WHEN** 사용자가 존재하는 디렉토리 path를 제출하면
- **THEN** 시스템은 해당 디렉토리에 대해 요청된 분석을 실행하고 HTTP 200 fragment를 반환한다

#### Scenario: 존재하지 않는 path
- **WHEN** 사용자가 존재하지 않는 path를 제출하면
- **THEN** 시스템은 HTTP 400 오류 fragment를 반환하고 서버 프로세스는 계속 실행된다

#### Scenario: 파일 path
- **WHEN** 사용자가 디렉토리가 아닌 파일 path를 제출하면
- **THEN** 시스템은 HTTP 400 오류 fragment를 반환하고 분석 builder를 호출하지 않는다

### Requirement: Analysis endpoints
The system SHALL provide web endpoints for overview, inventory, graph, metrics, entrypoints, quality, hotspots, report, dashboard, and review.

#### Scenario: 결정론적 분석 endpoint
- **WHEN** 유효한 path로 `/api/inventory`, `/api/graph`, `/api/metrics`, `/api/entrypoints`, `/api/quality`, `/api/hotspots`, `/api/report`, or `/api/dashboard`에 POST 요청을 보내면
- **THEN** 시스템은 기존 CodeXray builder를 사용해 결과 fragment를 반환한다

#### Scenario: Overview endpoint
- **WHEN** 유효한 path로 `/api/overview`에 POST 요청을 보내면
- **THEN** 시스템은 전체 grade, 주요 hotspot, 파일/언어 요약을 포함한 summary fragment를 반환한다

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

### Requirement: AI review opt-in
The system SHALL make AI review an explicit user action separate from deterministic analysis and SHALL show clear running feedback while the background review job is active.

#### Scenario: Review 탭 경고
- **WHEN** 사용자가 Review 탭을 볼 때
- **THEN** UI는 AI review가 1~5분 걸릴 수 있고 명시 실행이 필요하다는 경고를 표시한다

#### Scenario: 명시 실행
- **WHEN** 사용자가 Review 실행을 명시적으로 요청하면
- **THEN** 시스템은 background job을 시작하고 진행 상태 fragment를 즉시 반환한다

#### Scenario: Review running feedback
- **WHEN** background AI review job이 실행 중이면
- **THEN** UI는 polling 중임과 cancel control을 표시하고 다른 탭을 계속 사용할 수 있음을 보여준다

#### Scenario: Review 취소
- **WHEN** 사용자가 running AI review job에서 Cancel을 누르면
- **THEN** 시스템은 job을 cancelled 상태로 표시하고 cancelled fragment를 반환한다

#### Scenario: Review 상태 polling
- **WHEN** background AI review job이 완료되면
- **THEN** 시스템은 status endpoint를 통해 schema_version을 포함하는 readable review result fragment를 반환한다

### Requirement: Performance budget
The system SHALL return meaningful HTTP results within 5 seconds for deterministic endpoints on the validation codebases.

#### Scenario: Self validation
- **WHEN** CodeXray repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 result marker를 반환한다

#### Scenario: CivilSim validation
- **WHEN** CivilSim repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 result marker를 반환한다

### Requirement: Validation capture
The system SHALL capture web UI validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-web-ui 구현 검증을 완료하면
- **THEN** `docs/validation/web-ui-self.md` and `docs/validation/web-ui-civilsim.md` contain endpoint smoke results and representative output summaries

### Requirement: Theme mode
The system SHALL provide light and dark theme modes for the web UI and persist the user's preference in browser localStorage.

#### Scenario: Theme toggle
- **WHEN** 사용자가 theme toggle을 누르면
- **THEN** UI는 light와 dark mode 사이를 전환한다

#### Scenario: Theme persistence
- **WHEN** 사용자가 theme을 선택한 뒤 페이지를 다시 열면
- **THEN** 브라우저는 저장된 theme preference를 적용한다

### Requirement: Folder picker
The system SHALL provide a path Browse control that fills the path input from a local folder picker when the host OS supports it.

#### Scenario: macOS folder 선택
- **WHEN** macOS 사용자가 Browse 버튼을 눌러 폴더를 선택하면
- **THEN** 시스템은 선택된 POSIX path를 path input에 채운다

#### Scenario: folder 선택 취소
- **WHEN** 사용자가 folder picker를 취소하면
- **THEN** 시스템은 기존 path input 값을 유지하고 취소 상태를 표시한다

#### Scenario: 지원하지 않는 OS
- **WHEN** folder picker가 지원되지 않는 OS에서 Browse 버튼을 누르면
- **THEN** 시스템은 수동 path 입력이 필요하다는 오류 상태를 표시한다

### Requirement: Vibe Coding tab
The system SHALL provide a Vibe Coding tab in the localhost web UI that renders the vibe-coding report for the selected repository.

#### Scenario: Tab appears on main page
- **WHEN** the browser loads the web UI main page
- **THEN** the analysis tabs include a Vibe Coding tab

#### Scenario: Vibe Coding endpoint
- **WHEN** a valid repository path is submitted to the Vibe Coding tab
- **THEN** the web UI returns an HTTP 200 fragment containing the vibe-coding report

### Requirement: Non-developer report rendering
The system SHALL render the Vibe Coding tab as a readable Korean report for non-developer vibe coders, with summary cards before technical evidence tables.

#### Scenario: Summary-first rendering
- **WHEN** the Vibe Coding tab renders a report
- **THEN** the fragment begins with confidence, strengths, risks, and next actions before listing detailed evidence

#### Scenario: Evidence remains inspectable
- **WHEN** the Vibe Coding tab renders detected artifacts
- **THEN** the fragment includes evidence paths grouped by process area

### Requirement: Vibe Coding tab validation capture
The system SHALL capture Vibe Coding tab validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-vibe-coding-report-tab implementation validation is complete
- **THEN** `docs/validation/vibe-coding-report-self.md` and `docs/validation/vibe-coding-report-civilsim.md` contain representative output summaries

### Requirement: Briefing-first web navigation
The system SHALL organize the web UI around one top-level Briefing tab before low-level analyzer tabs, and SHALL keep briefing subsections inside the Briefing presentation controls instead of duplicating them as top-level tabs.

#### Scenario: Primary briefing tab appears
- **WHEN** the browser loads the web UI main page
- **THEN** the primary navigation includes exactly one top-level Briefing tab that requests `/api/briefing`

#### Scenario: Briefing subsections are not duplicate top-level tabs
- **WHEN** the browser loads the web UI main page
- **THEN** Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive are not rendered as separate top-level analysis tabs

#### Scenario: Detailed analyzers remain accessible
- **WHEN** the user reviews the top-level navigation
- **THEN** the UI still exposes the existing detailed analysis views for overview, inventory, graph, metrics, hotspots, quality, entrypoints, report, dashboard, vibe-coding evidence, and review

### Requirement: Briefing endpoint
The system SHALL provide a web endpoint that renders the codebase briefing for the selected repository.

#### Scenario: Valid path briefing request
- **WHEN** a valid repository path is submitted to the briefing endpoint
- **THEN** the web UI returns an HTTP 200 fragment containing a presentation-like briefing with executive, architecture, risk, build-process, explanation, and deep-dive sections

#### Scenario: Briefing includes git-history build process
- **WHEN** git history is available for the selected repository
- **THEN** the rendered briefing includes a How It Was Built section with commit timeline and vibe-coding process evidence

### Requirement: Non-developer friendly rendering
The system SHALL render briefing content in readable Korean for both technical and non-technical audiences.

#### Scenario: Plain-language explanation appears
- **WHEN** the Explain section is rendered
- **THEN** it includes plain-language text suitable for explaining the repository to a non-developer

#### Scenario: Evidence remains visible
- **WHEN** a briefing section presents an interpretation
- **THEN** nearby UI includes concrete evidence such as grade, paths, commit messages, or process artifacts

### Requirement: Briefing validation capture
The system SHALL capture briefing validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-codebase-briefing-experience implementation validation is complete
- **THEN** `docs/validation/codebase-briefing-self.md` and `docs/validation/codebase-briefing-civilsim.md` contain representative briefing output summaries

### Requirement: Overview strengths/weaknesses/actions cards
The system SHALL render three card sections — Strengths, Weaknesses, Next Actions — in the Overview tab main area above the existing summary metrics, each listing up to 3 deterministic items with evidence citations. The cards SHALL be rendered without AI calls and within the existing 5-second performance budget.

#### Scenario: 카드 위치
- **WHEN** 사용자가 Overview 탭을 보면
- **THEN** 메인 영역 상단에 Strengths · Weaknesses · Next Actions 세 카드가 노출되고 그 아래에 기존 summary 메트릭이 표시된다

#### Scenario: 항목 fallback
- **WHEN** 어느 카드의 summary 항목이 0개이면
- **THEN** 해당 카드는 항목 list 대신 "특이사항 없음" 안내 텍스트를 표시한다

#### Scenario: 근거 인용
- **WHEN** Strengths · Weaknesses · Next Actions 항목이 표시되면
- **THEN** 각 항목 본문은 file path 또는 dimension 이름과 score / grade / count 같은 수치 근거를 포함한다

#### Scenario: AI 미사용
- **WHEN** Overview 탭이 렌더링되면
- **THEN** 시스템은 AI 어댑터를 호출하지 않고 result fragment를 반환한다

### Requirement: Report tab strengths/weaknesses/actions sections
The system SHALL render Strengths, Weaknesses, and Next Actions sections at the top of the Report tab readable HTML, mirroring the Markdown structure with up to 3 items each and mandatory evidence citation.

#### Scenario: 위치
- **WHEN** 사용자가 Report 탭을 보면
- **THEN** readable HTML 상단에 Strengths · Weaknesses · Next Actions 섹션이 등장하고 그 아래에 기존 Recommendations · Markdown 본문이 표시된다

#### Scenario: 항목 일관성
- **WHEN** 같은 path로 `codexray report`(CLI)와 Web Report 탭을 비교하면
- **THEN** Strengths · Weaknesses · Next Actions의 항목 수와 본문 텍스트는 같은 path에 대해 동일하다

#### Scenario: AI 미사용
- **WHEN** Report 탭이 렌더링되면
- **THEN** 시스템은 AI 어댑터를 호출하지 않는다

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

### Requirement: Briefing presentation mode
The system SHALL render the Briefing tab as a presentation-mode experience inside the localhost web UI.

#### Scenario: Presentation controls appear
- **WHEN** the Briefing tab renders for a valid repository path
- **THEN** the fragment includes slide count, previous control, next control, and section navigation for the presentation slides

#### Scenario: Focused slide rendering
- **WHEN** the presentation-mode briefing first appears
- **THEN** the first slide is visible as the focused slide and non-focused slides are hidden or visually inactive

#### Scenario: Local slide navigation
- **WHEN** the user activates next, previous, or a section navigation control
- **THEN** the focused slide changes locally without requesting a new server analysis

#### Scenario: Keyboard navigation
- **WHEN** the presentation-mode briefing has focus and the user presses ArrowRight or ArrowLeft
- **THEN** the focused slide moves to the next or previous slide locally

### Requirement: Presenter-friendly briefing content
The system SHALL render presenter-friendly content for technical and non-technical audiences while keeping evidence visible.

#### Scenario: Presenter summary appears
- **WHEN** the Briefing tab renders
- **THEN** the fragment includes a concise presenter summary near the top of the presentation

#### Scenario: Evidence remains visible on slides
- **WHEN** a slide presents an interpretation
- **THEN** the slide displays concrete evidence such as grade, path, metric, hotspot, commit message, or process artifact near that interpretation

#### Scenario: Deep dive remains available
- **WHEN** a user reaches the final or deep-dive slide
- **THEN** the UI provides links or controls to inspect the existing detailed analyzer tabs

### Requirement: Briefing presentation validation capture
The system SHALL capture briefing presentation validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-briefing-presentation-mode implementation validation is complete
- **THEN** `docs/validation/briefing-presentation-self.md` and `docs/validation/briefing-presentation-civilsim.md` contain representative presentation output summaries and navigation markers

### Requirement: Rich briefing slide rendering
The system SHALL render deep briefing interpretation on presentation slides in a scannable format.

#### Scenario: Slide interpretation sections appear
- **WHEN** the Briefing presentation renders
- **THEN** each slide displays summary, meaning, risk, and action sections when those fields are present

#### Scenario: Evidence stays adjacent
- **WHEN** interpretation sections are displayed
- **THEN** concrete evidence and deep-dive references remain visible on the same slide

### Requirement: Narrative depth validation capture
The system SHALL capture validation output for the deeper briefing narrative on both validation codebases.

#### Scenario: Validation documents
- **WHEN** improve-briefing-narrative-depth implementation validation is complete
- **THEN** `docs/validation/briefing-narrative-depth-self.md` and `docs/validation/briefing-narrative-depth-civilsim.md` contain representative slide interpretation summaries

### Requirement: Raw JSON 제거
The system SHALL NOT render raw JSON blocks in any analysis tab result panel.

#### Scenario: 분석 탭 결과 렌더링
- **WHEN** 분석 탭이 결과를 렌더링하면
- **THEN** 결과 패널에 raw JSON 블록이 포함되지 않는다

### Requirement: Insight 텍스트 한국어
The system SHALL display all analysis insight texts in Korean.

#### Scenario: Hotspots insight 텍스트
- **WHEN** Hotspots 탭이 렌더링되면
- **THEN** insight 텍스트가 한국어로 표시된다

#### Scenario: AI Review insight 텍스트
- **WHEN** AI Review 탭이 렌더링되면
- **THEN** insight 텍스트가 한국어로 표시된다

### Requirement: 상세 탭 시각 구분
The system SHALL visually separate summary tabs from detail tabs using a divider.

#### Scenario: 탭 구분선 표시
- **WHEN** 메인 페이지가 로드되면
- **THEN** 주요 탭(Briefing~Review) 과 상세 탭(Graph/Entrypoints/Dashboard/Vibe Coding) 사이에 시각적 구분선이 표시된다

