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

### Requirement: 페르소나 영역 분리
The web UI SHALL maintain a hard separation between the Briefing area (top of the page) and the Detailed Analysis toggle (below) so that each area serves a single, primary audience without compromise.

#### Scenario: 브리핑 영역은 비개발자 청자 영역
- **WHEN** Briefing 화면 상단(executive, architecture, quality_risk, vibe coding section, next actions, key insight, intent alignment)이 렌더링되면
- **THEN** 모든 텍스트는 비개발자 바이브코더가 1차 청자라는 가정하에 표시되며, 메트릭 용어를 직접 노출하지 않는다 (codebase-briefing 의 "Plain-language technical translation" 요구사항을 따른다)

#### Scenario: 상세 분석 토글은 개발자 청자 영역
- **WHEN** Briefing 화면에서 사용자가 상세 분석 토글(미시 분석 탭들 — Hotspots, Inventory, Code Metrics, Code Quality, Dependency Graph, Entrypoints, Vibe Coding Tab, Report)을 펼치면
- **THEN** 그 영역의 시각화·표·메트릭 표현은 개발자 청자 가정(메트릭 용어 직접 노출 OK)하에 그대로 유지되며 비개발자 친화 톤으로 다시 쓰지 않는다

#### Scenario: 영역 간 일관성
- **WHEN** Briefing 영역이 어떤 사실(예: hotspot 개수, coupling 상위 파일)을 평어로 인용하고
- **AND** 사용자가 같은 사실을 상세 분석 토글에서 메트릭 형태로 볼 수 있어야 하면
- **THEN** 두 영역의 데이터 소스는 동일하고 (briefing 평어가 메트릭의 부정확한 요약이 아니라 같은 결정론적 데이터의 다른 표현이어야 한다), 토글 영역에는 같은 메트릭의 raw 형태가 유지된다

#### Scenario: 영역 분리 위반 방지
- **WHEN** 새로운 화면 요소를 Briefing 영역에 추가할 때
- **THEN** 해당 요소의 텍스트가 메트릭 용어를 도입하지 않는지 codebase-briefing 의 "Plain-language technical translation" 요구사항으로 검증한다 (위반 시 토글 영역으로 이동 또는 평어 번역)

### Requirement: 4단계 축 상태 표시
The web UI SHALL render each vibe coding axis (`intent / verification / continuity`) as a 4-level state label with a recognized-signal count and 2–3 representative pieces of evidence, instead of a 0–100 numeric score.

#### Scenario: 상태 라벨 표시
- **WHEN** vibe coding 섹션이 렌더링되면
- **THEN** 각 축은 다음 중 하나의 상태 라벨로 표시된다: 강함 (`strong`), 보통 (`moderate`), 약함 (`weak`), 판단유보 (`unknown`)

#### Scenario: 근거 개수와 대표 근거
- **WHEN** 축 상태 라벨이 표시되면
- **THEN** 그 옆에 인지된 신호 개수(예: "신호 4개") 와 대표 근거 2-3 개(파일 경로 또는 문서 라벨)가 함께 표시된다

#### Scenario: 0-100 점수 미노출
- **WHEN** 브리핑 영역이 렌더링되면
- **THEN** 0-100 원시 점수는 *기본 노출되지 않으며*, 디버그/실험 토글이 있는 경우에만 그 안에서 보인다

### Requirement: 다음 행동 카드 0–3개 동적 렌더링
The web UI SHALL render between 0 and 3 next-action cards based on the payload's `next_actions` length, and display the corresponding zero-action message (`praise / judgment_pending / silent`) when the list is empty.

#### Scenario: 카드 0개 + 칭찬
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `praise` 일 때
- **THEN** UI 는 다음 행동 카드 영역을 숨기지 않고, 대신 "유지할 습관" 한 줄 메시지를 같은 카드 자리에 보조 톤으로 표시한다

#### Scenario: 카드 0개 + 판단 보류
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `judgment_pending` 일 때
- **THEN** UI 는 "코드만 봐선 추가 진단 어려움 — 사용자 대화·시연이 필요합니다" 메시지를 표시하고 칭찬 톤은 사용하지 않는다

#### Scenario: 카드 0개 + 침묵
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `silent` 일 때
- **THEN** UI 는 다음 행동 영역에 별도 카드나 메시지를 표시하지 않는다 (영역 자체를 숨김 또는 보조 텍스트만 노출)

#### Scenario: 카드 1-3개
- **WHEN** payload 의 `next_actions` 가 1-3 개 항목을 포함하면
- **THEN** UI 는 그 만큼의 카드를 카테고리 그룹과 함께 렌더링한다 (직전 변경의 카테고리 표시 유지)

### Requirement: blind spot 고정 블록 UI
The web UI SHALL display a fixed "이 도구가 못 본 것" block in the Briefing area on every analysis result page, regardless of axis states or card counts.

#### Scenario: 블록 위치
- **WHEN** Briefing 화면이 렌더링되면
- **THEN** 검토 경고 배너 바로 아래 또는 vibe coding 섹션 하단에 blind spot 블록이 표시된다

#### Scenario: 블록 내용
- **WHEN** blind spot 블록이 렌더링되면
- **THEN** 다음 4 항목이 최소한 포함되고, codebase-briefing 의 "blind spot 상시 노출" 요구사항과 일치한다:
  1. 사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가
  2. 손으로 한 검증이 *실제로 매번* 굴러가는가
  3. 다음 행동의 우선순위를 사람이 정하고 있는가
  4. 외부 도구(Notion, Confluence, Slack, Linear 등)에 있는 의도·결정 흔적과 README 같은 문서의 *질적 깊이* 는 자동 판단 못 합니다

#### Scenario: 블록 톤은 자가 점검
- **WHEN** blind spot 블록이 렌더링되면
- **THEN** 본문 톤은 *자가 점검 체크리스트* 이며 "이 도구가 못 미덥다" 인상이 아닌 *사용자 책임 환기* 표현을 사용한다

### Requirement: 평가 철학 토글
The web UI SHALL display a collapsible "이 도구가 바이브코딩을 어떻게 평가하나요?" toggle at the bottom of the Briefing area, defaulting to collapsed, that exposes the evaluation philosophy and methodology to the user when expanded.

#### Scenario: 토글 위치와 기본 상태
- **WHEN** Briefing 화면이 렌더링되면
- **THEN** vibe coding 섹션 최하단 (blind spot 블록 아래) 또는 Briefing 화면 footer 영역에 "이 도구가 바이브코딩을 어떻게 평가하나요?" 라벨의 토글이 표시되고, 기본 상태는 *접힘* 이다

#### Scenario: 펼침 콘텐츠 구조
- **WHEN** 사용자가 토글을 펼치면
- **THEN** 다음 8 섹션이 순서대로 노출된다:
  1. 슬로건 한 줄 — "주인이 있는 프로젝트"
  2. 운영 정의 3 구조 — 외부화된 의도 / 독립 검증 / 인간 최종 판단
  3. 8 운영 신호 — 흔적 6 + 사각지대 2
  4. 3축 매핑 — 어느 신호가 어느 축에 매핑되는지
  5. 4 단계 상태 의미 — strong / moderate / weak / unknown 각각의 뜻과 임계
  6. 카드 수 정책 — 왜 0-3 동적인가
  7. 사각지대 4 항목 재명시
  8. 출처 — 리서치에서 인용한 핵심 자료

#### Scenario: 토글은 모든 화면에 일관되게 노출
- **WHEN** 사용자가 분석 결과를 새로 받거나 같은 결과를 다시 볼 때
- **THEN** 토글의 *콘텐츠는 동일하게* 표시된다 (분석 결과에 따라 변하지 않음 — 평가 *방법론* 자체이므로)

#### Scenario: 토글 콘텐츠 톤
- **WHEN** 토글 콘텐츠가 렌더링되면
- **THEN** 본문은 비개발자 100% 청자 톤을 유지하며 (codebase-briefing 의 "Plain-language technical translation" 요구사항 준수), 출처 인용은 영어 원문 그대로 OK

### Requirement: 약한 process proxy 보조 패널 분리
The web UI SHALL display weak process proxies (feat/fix ratio, spec commit timing, hotspot accumulation) only in a clearly separated supplementary panel, not as primary axis evidence.

#### Scenario: 보조 정보 패널 분리
- **WHEN** payload 의 `process_proxies` 필드가 비어있지 않을 때
- **THEN** UI 는 그 정보를 vibe coding 섹션의 *축 상태 라벨 옆* 이 아니라 *별도 보조 패널* (collapsable 토글 또는 작은 글씨 보조 라인) 로 노출한다

#### Scenario: 보조 패널 라벨
- **WHEN** 보조 패널이 렌더링되면
- **THEN** 패널의 헤더는 명확하게 "참고용 — 단독 판정 근거 아님" 같은 표현을 포함하여 사용자가 이를 *축 상태와 별개* 로 인식하게 한다

### Requirement: 크로스 플랫폼 CI 게이트

The project SHALL maintain a GitHub Actions CI workflow that runs the full pytest suite on Linux, macOS, and Windows for every push to `main` and every pull request. All three OS jobs SHALL pass before any change is merged. This guarantees the tool's CLI and web-ui backend work on the user's primary persona's environment (Windows coworkers) without manual platform verification.

#### Scenario: CI matrix 3 OS 정의
- **WHEN** `.github/workflows/ci.yml` 가 검사되면
- **THEN** workflow 는 `strategy.matrix.os` 에 `ubuntu-latest`, `macos-latest`, `windows-latest` 셋을 모두 포함한다

#### Scenario: pytest 가 모든 OS 에서 실행됨
- **WHEN** 모든 matrix job 이 실행되면
- **THEN** 각 job 은 `uv sync` 로 의존성을 설치한 후 `uv run pytest tests/ -q` 를 실행하고 *exit code 0* 을 반환한다

#### Scenario: 한 OS 라도 실패하면 머지 차단
- **WHEN** main 브랜치로 push 되거나 pull request 가 생성되면
- **THEN** workflow 가 trigger 되고, 셋 중 하나라도 실패하면 CI 결과가 *failure* 로 보고된다 (GitHub PR UI 에서 머지 가능 상태가 아니게 됨)

#### Scenario: 신규 변경의 Windows 회귀 차단
- **WHEN** 새 변경이 main 으로 머지되기 전 PR 단계에서
- **THEN** Windows job 이 통과해야 머지 가능하다 — Windows 사용자 (1순위 페르소나) 의 첫 경험이 깨지지 않도록 자동 보장

### Requirement: PyPI 패키지 설치 가능

The project SHALL be installable from PyPI as a single command (`pip install codexray` or `uv tool install codexray`). The installed package SHALL include the React frontend build artifact (`frontend/dist/`) so that `codexray serve` works without additional setup. Installation SHALL succeed on Linux, macOS, and Windows for Python 3.11 and above.

#### Scenario: 패키지 메타데이터 PyPI 호환
- **WHEN** `pyproject.toml` 이 검사되면
- **THEN** `[project]` 테이블은 `name`, `version`, `description`, `readme`, `license`, `authors`, `requires-python` 필수 필드를 포함하고, `[project.urls]` 에 Repository / Issues 링크가 있으며, `classifiers` 에 OS / Python 버전 / Topic / License / Development Status 분류가 있고, `keywords` 가 1 개 이상이다

#### Scenario: 빌드 산출물에 frontend/dist 포함
- **WHEN** `uv build` 가 실행되어 wheel 이 생성되면
- **THEN** wheel 은 `frontend/dist/index.html` 과 그 모든 자산 (JS, CSS, 기타) 을 패키지 내부 경로 (예: `codexray/_frontend/`) 에 포함한다. 별도 npm install 없이 설치 후 `codexray serve` 가 SPA 를 서빙할 수 있다

#### Scenario: README 에 OS 별 설치 가이드
- **WHEN** README 가 검사되면
- **THEN** README 는 *Quickstart 위쪽* 에 "## 설치" 섹션을 포함하고, Windows / macOS / Linux 공통 명령 (`pip install codexray` 또는 `uv tool install codexray`) 과 prerequisite (Python 3.11+, 선택적 codex/claude CLI) 안내를 갖는다

#### Scenario: 빌드 검증 절차 문서화
- **WHEN** PyPI publish 직전에 빌드를 검증하면
- **THEN** 다음 절차가 README 또는 docs 에 명시되어 있다: (1) `cd frontend && npm run build`, (2) `uv build`, (3) `unzip -l dist/codexray-*.whl` 로 frontend 자산 포함 확인, (4) 임시 venv 에 wheel 설치 + `codexray --help` 동작 확인

