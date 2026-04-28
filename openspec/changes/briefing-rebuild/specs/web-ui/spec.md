## MODIFIED Requirements

### Requirement: Web UI CLI 진입점
The system SHALL expose a `codexray serve` command that starts a localhost web server hosting the React SPA and JSON API.

#### Scenario: 기본 서버 실행
- **WHEN** 사용자가 `codexray serve`를 실행하면
- **THEN** 시스템은 `127.0.0.1:8080`에서 HTTP 서버를 시작한다

#### Scenario: 포트 지정
- **WHEN** 사용자가 `codexray serve --port 8090`을 실행하면
- **THEN** 시스템은 `127.0.0.1:8090`에서 HTTP 서버를 시작한다

#### Scenario: 브라우저 자동 열림 비활성화
- **WHEN** 사용자가 `codexray serve --no-browser`를 실행하면
- **THEN** 시스템은 서버를 시작하지만 브라우저를 자동으로 열지 않는다

#### Scenario: SPA 정적 서빙
- **WHEN** 서버가 시작되면
- **THEN** 서버는 `frontend/dist/`의 정적 자산을 `GET /` 와 자산 경로에 서빙한다

### Requirement: Path validation
The system SHALL validate submitted paths before running analysis and return JSON errors when invalid.

#### Scenario: 유효한 디렉토리 path
- **WHEN** 사용자가 존재하는 디렉토리 path를 제출하면
- **THEN** 시스템은 해당 디렉토리에 대한 분석을 실행하고 HTTP 200 JSON을 반환한다

#### Scenario: 존재하지 않는 path
- **WHEN** 사용자가 존재하지 않는 path를 제출하면
- **THEN** 시스템은 HTTP 400 JSON error response를 반환하고 서버 프로세스는 계속 실행된다

#### Scenario: 파일 path
- **WHEN** 사용자가 디렉토리가 아닌 파일 path를 제출하면
- **THEN** 시스템은 HTTP 400 JSON error를 반환하고 분석 builder를 호출하지 않는다

### Requirement: Analysis endpoints
The system SHALL provide JSON API endpoints for briefing, overview, inventory, graph, metrics, entrypoints, quality, hotspots, report, and review.

#### Scenario: 결정론적 분석 endpoint
- **WHEN** 유효한 path로 `/api/inventory`, `/api/graph`, `/api/metrics`, `/api/entrypoints`, `/api/quality`, `/api/hotspots`, `/api/report`에 POST 요청을 보내면
- **THEN** 시스템은 분석 builder의 결과를 JSON으로 반환한다

#### Scenario: Briefing endpoint
- **WHEN** 유효한 path로 `/api/briefing`에 POST 요청을 보내면
- **THEN** 시스템은 background job을 시작하고 `{ jobId }`를 즉시 반환한다

#### Scenario: Briefing 진행 상태 polling
- **WHEN** SPA가 `GET /api/briefing/status/{jobId}`를 polling하면
- **THEN** 시스템은 현재 단계와 진행률, 완료 시 결과를 JSON으로 반환한다

#### Scenario: Vibe coding insights endpoint
- **WHEN** 유효한 path로 `/api/vibe-coding-insights`에 POST 요청을 보내면
- **THEN** 시스템은 자동 판별 결과, 3축 점수, 타임라인 데이터, 다음 행동을 JSON으로 반환한다

### Requirement: AI review opt-in
The system SHALL keep AI review as an explicit user action exposed through JSON endpoints.

#### Scenario: 명시 실행
- **WHEN** 사용자가 SPA에서 Review 실행을 명시적으로 요청하면
- **THEN** SPA는 `POST /api/review`로 background job을 시작하고 진행 상태 JSON을 받는다

#### Scenario: Review 상태 polling
- **WHEN** background AI review job이 진행 중이면
- **THEN** SPA는 `GET /api/review/status/{jobId}`를 polling하여 현재 단계와 결과를 받는다

#### Scenario: Review 취소
- **WHEN** 사용자가 진행 중인 review job에 대해 Cancel을 요청하면
- **THEN** 시스템은 `POST /api/review/cancel/{jobId}`을 받아 job을 cancelled 상태로 표시하고 cancelled JSON을 반환한다

### Requirement: Performance budget
The system SHALL return JSON results within 5 seconds for deterministic endpoints on the validation codebases.

#### Scenario: Self validation
- **WHEN** CodeXray repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 JSON 결과를 반환한다

#### Scenario: CivilSim validation
- **WHEN** CivilSim repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 JSON 결과를 반환한다

### Requirement: Folder picker
The system SHALL provide a folder picker JSON endpoint that returns the chosen path when the host OS supports it.

#### Scenario: macOS folder 선택
- **WHEN** macOS 사용자가 SPA의 Browse 컨트롤을 통해 폴더를 선택하면
- **THEN** SPA는 `POST /api/browse-folder`로 호출하고 응답으로 받은 POSIX path를 path input에 채운다

#### Scenario: folder 선택 취소
- **WHEN** 사용자가 folder picker를 취소하면
- **THEN** 시스템은 cancellation을 의미하는 JSON을 반환하고 SPA는 path input을 변경하지 않는다

#### Scenario: 지원하지 않는 OS
- **WHEN** folder picker가 지원되지 않는 OS에서 호출되면
- **THEN** 시스템은 HTTP 400 JSON error를 반환하고 SPA는 수동 입력 안내를 표시한다

### Requirement: Validation capture
The system SHALL capture web UI validation results for both validation codebases after the rebuild.

#### Scenario: Validation documents
- **WHEN** briefing-rebuild 구현 검증을 완료하면
- **THEN** `docs/validation/briefing-rebuild-self.md` 와 `docs/validation/briefing-rebuild-civilsim.md` 에 JSON endpoint smoke와 SPA 렌더링 결과가 포함된다

## REMOVED Requirements

### Requirement: htmx Jinja UI
**Reason:** htmx + Jinja 기반 부분 렌더링은 React SPA + JSON API로 전면 교체됨.

**Migration:** react-frontend capability의 "React SPA 빌드 파이프라인", "SPA 진입과 자동 분석", "JSON API 통신" 요구를 참조.

### Requirement: 메인 페이지
**Reason:** 메인 페이지는 SPA 진입점으로 단순화됨. 기존 메인 페이지의 path input, recent path selector, 분석 탭, 결과 패널은 모두 SPA 컴포넌트로 이전됨.

**Migration:** react-frontend 의 "SPA 진입과 자동 분석", "최근 path 저장", "미시 분석 영역" 요구를 사용한다.

### Requirement: Briefing-first web navigation
**Reason:** Briefing 단일 화면 + 미시 분석 영역 구조로 단순화. 별도 탭으로서의 Briefing은 사라지고 메인 화면 자체가 Briefing임.

**Migration:** react-frontend 의 "Briefing 매크로 화면 5개 섹션", "미시 분석 영역" 요구를 사용한다.

### Requirement: Briefing endpoint
**Reason:** HTML fragment 응답을 JSON으로 변경하기 위해 새 Analysis endpoints 요구로 통합됨.

**Migration:** 새 Analysis endpoints 요구의 Briefing endpoint, Briefing 진행 상태 polling 시나리오를 사용한다.

### Requirement: Result rendering
**Reason:** HTML 렌더링은 SPA가 책임. 백엔드는 JSON만 반환.

**Migration:** react-frontend 의 "JSON API 통신" 요구와 미시 분석 영역 렌더링 요구를 사용한다.

### Requirement: Briefing presentation mode
**Reason:** 슬라이드 모드는 5개 섹션 매크로 화면으로 흡수됨.

**Migration:** react-frontend 의 "Briefing 매크로 화면 5개 섹션" 요구를 사용한다.

### Requirement: Presenter-friendly briefing content
**Reason:** 발표 친화 콘텐츠는 5개 섹션 화면 자체가 발표 자료가 되도록 설계됨.

**Migration:** react-frontend 의 "Briefing 매크로 화면 5개 섹션" 의 발표 친화적 시각 시나리오를 사용한다.

### Requirement: Briefing presentation validation capture
**Reason:** 새 검증 capture 요구로 대체됨.

**Migration:** 새 Validation capture 요구를 사용한다.

### Requirement: Rich briefing slide rendering
**Reason:** 슬라이드 단위 렌더링이 폐기됨에 따라 폐기.

**Migration:** react-frontend 의 5개 섹션 렌더링과 미시 영역으로 이전됨.

### Requirement: Narrative depth validation capture
**Reason:** 새 Validation capture 요구로 통합됨.

**Migration:** 새 Validation capture 요구를 사용한다.

### Requirement: Senior insights generation
**Reason:** 시니어 인사이트는 본 변경에서 일단 아카이브되며 후속 변경에서 React SPA 위에 다시 도입 예정.

**Migration:** 후속 변경에서 별도 capability로 재도입.

### Requirement: Insights cache
**Reason:** 시니어 인사이트 미지원에 따라 폐기.

**Migration:** 후속 변경에서 재도입.

### Requirement: Insights AI fallback
**Reason:** 시니어 인사이트 미지원에 따라 폐기.

**Migration:** 후속 변경에서 재도입.

### Requirement: Vibe Coding tab
**Reason:** Vibe Coding은 메인 Briefing 안의 핵심 섹션과 독립 미시 탭 두 곳에서 다뤄지며 새 vibe-coding-insights capability와 react-frontend 의 미시 분석 영역으로 이전됨.

**Migration:** vibe-coding-insights capability 와 react-frontend 의 "미시 분석 영역" 요구를 사용한다.

### Requirement: Non-developer report rendering
**Reason:** 비개발자 친화 렌더링은 react-frontend 와 codebase-briefing 의 plain-language 요구로 이전됨.

**Migration:** codebase-briefing 의 "Plain-language technical translation" 요구를 사용한다.

### Requirement: Vibe Coding tab validation capture
**Reason:** 새 Validation capture 요구로 통합됨.

**Migration:** 새 Validation capture 요구를 사용한다.

### Requirement: Briefing validation capture
**Reason:** 새 Validation capture 요구로 통합됨.

**Migration:** 새 Validation capture 요구를 사용한다.

### Requirement: Non-developer friendly rendering
**Reason:** codebase-briefing 의 plain-language 요구로 이전됨.

**Migration:** codebase-briefing 의 "Plain-language technical translation" 요구를 사용한다.

### Requirement: AI-first briefing loading UX
**Reason:** SPA의 진행 상태 UX 요구로 이전됨.

**Migration:** react-frontend 의 "진행 상태 UX" 요구를 사용한다.

### Requirement: AI 해석 결과 폴백
**Reason:** AI 폴백은 codebase-briefing 의 새 AI 해석 레이어 요구의 폴백 시나리오로 통합됨.

**Migration:** codebase-briefing 의 "AI 해석 레이어" 요구의 폴백 시나리오를 사용한다.

### Requirement: Overview strengths/weaknesses/actions cards
**Reason:** Strengths/Weaknesses/Actions 카드는 미시 영역의 Overview 탭이 React 컴포넌트로 포팅될 때 그대로 유지됨. 단, 본 변경에서는 백엔드 JSON으로 분리되어 SPA가 렌더링한다.

**Migration:** Analysis endpoints 의 overview JSON 응답에 strengths, weaknesses, next_actions 배열을 포함하고 react-frontend 의 "미시 분석 영역" 에서 Overview 컴포넌트가 렌더링한다.

### Requirement: Report tab strengths/weaknesses/actions sections
**Reason:** Report 탭의 SWA 섹션도 JSON 응답에 포함되고 React 컴포넌트가 렌더링.

**Migration:** Analysis endpoints 의 report JSON 응답에 strengths, weaknesses, next_actions 배열을 포함한다.

### Requirement: Raw JSON 제거
**Reason:** SPA 도입으로 raw JSON이 화면에 노출되는 경로 자체가 사라짐. 결과는 컴포넌트가 표시.

**Migration:** react-frontend 의 "미시 분석 영역" 요구의 raw JSON 미노출 시나리오로 흡수.

### Requirement: Insight 텍스트 한국어
**Reason:** 한국어 텍스트는 SPA의 모든 화면에서 기본이며 별도 요구 불필요.

**Migration:** react-frontend 와 codebase-briefing 의 한국어 서술 요구로 흡수.

### Requirement: 상세 탭 시각 구분
**Reason:** 시각 구분은 SPA의 디자인 시스템(shadcn/ui Card / Tabs)이 보장.

**Migration:** react-frontend 의 "shadcn/ui 컴포넌트 사용" 과 "미시 분석 영역" 요구로 흡수.

### Requirement: LoC 규모 레이블
**Reason:** 레이블 표시는 SPA 컴포넌트가 데이터를 받아 표시.

**Migration:** Analysis endpoints 의 inventory JSON에 loc 수치와 함께 size_label 필드를 포함한다.

### Requirement: Coupling 위험도 표시
**Reason:** 위험도 레이블도 SPA 컴포넌트 책임.

**Migration:** Analysis endpoints 의 metrics 와 hotspots JSON에 risk_label 필드를 포함한다.

### Requirement: 전문 용어 설명
**Reason:** 용어 설명은 SPA의 tooltip/secondary text가 담당.

**Migration:** react-frontend 의 미시 영역 컴포넌트에서 전문 용어 옆 보조 설명을 표시한다.

### Requirement: Hotspot 카테고리 한국어화
**Reason:** 한국어화는 SPA 책임.

**Migration:** Analysis endpoints 의 hotspots JSON에 category_label 필드(한국어)를 포함한다.

### Requirement: Quality 등급 해석
**Reason:** 등급 해석은 SPA 컴포넌트가 표시.

**Migration:** Analysis endpoints 의 quality JSON에 grade와 함께 grade_interpretation 필드를 포함한다.

### Requirement: Theme mode
**Reason:** 테마 모드는 react-frontend capability의 "라이트/다크 테마와 영속성" 요구로 이전됨.

**Migration:** react-frontend 의 새 요구를 사용한다.
