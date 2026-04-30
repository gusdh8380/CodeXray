# web-ui Specification

## Purpose
The web-ui capability provides the `codexray serve` CLI: it runs a localhost FastAPI server (default `127.0.0.1:8080`) that serves the React SPA static bundle and exposes every CodeXray analysis builder and the AI review through JSON API endpoints. AI review is an explicit opt-in background job with cancel and status polling.
## Requirements
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

#### Scenario: aquaview validation
- **WHEN** aquaview repository path로 deterministic endpoint smoke를 실행하면
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

