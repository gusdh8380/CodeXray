# react-frontend Specification

## Purpose
The react-frontend capability defines the React + Vite + Tailwind + shadcn/ui single-page application that ships as CodeXray's user-facing UI. It auto-starts Briefing analysis on path entry, renders the five-section macro Briefing, preserves the legacy detailed analyzer tabs as a collapsible micro-analysis area, and communicates with the FastAPI backend exclusively through JSON endpoints.

## Requirements
### Requirement: React SPA 빌드 파이프라인
The system SHALL provide a React + Vite + Tailwind + shadcn/ui frontend project that builds to a static `frontend/dist/` directory served by FastAPI.

#### Scenario: 프로젝트 구조
- **WHEN** 저장소를 clone 한 직후
- **THEN** `frontend/` 디렉토리에 `package.json`, `vite.config.ts`, `tailwind.config.js`, `src/` 등이 존재한다

#### Scenario: 개발 빌드
- **WHEN** 개발자가 `frontend/`에서 `npm run dev`를 실행하면
- **THEN** Vite dev 서버가 시작되고 코드 변경이 즉시 반영된다

#### Scenario: 프로덕션 빌드
- **WHEN** 개발자가 `frontend/`에서 `npm run build`를 실행하면
- **THEN** `frontend/dist/`에 정적 자산이 생성되고 그 결과를 FastAPI가 `GET /` 응답으로 서빙한다

#### Scenario: 단일 명령 실행
- **WHEN** 사용자가 `codexray serve`를 실행하면
- **THEN** FastAPI는 빌드된 SPA(`frontend/dist/`)를 정적으로 서빙하고 SPA가 JSON API와 통신한다

### Requirement: SPA 진입과 자동 분석
The system SHALL load the SPA at `GET /`, accept a path input, and automatically start Briefing analysis when a path is submitted.

#### Scenario: SPA 초기 화면
- **WHEN** 브라우저가 `GET /`를 요청하면
- **THEN** SPA는 path input과 최근 path selector, 분석 결과 영역을 가진 화면을 렌더링한다

#### Scenario: 자동 분석 시작
- **WHEN** path input에 값이 있고 사용자가 Enter를 누르거나 최근 path를 선택하면
- **THEN** SPA는 별도 분석 시작 버튼 없이 즉시 Briefing 분석을 시작한다

#### Scenario: 분석하기 버튼 부재
- **WHEN** SPA가 렌더링되면
- **THEN** 별도의 "분석하기" 버튼은 존재하지 않는다

### Requirement: shadcn/ui 컴포넌트 사용
The system SHALL use shadcn/ui components for consistent visual presentation.

#### Scenario: 카드 컴포넌트
- **WHEN** Briefing 섹션, 바이브코딩 점수, 다음 행동 항목이 렌더링되면
- **THEN** UI는 shadcn/ui Card 또는 그 파생 컴포넌트를 사용한다

#### Scenario: 진행 상태 컴포넌트
- **WHEN** Briefing 분석이 진행 중이면
- **THEN** UI는 shadcn/ui Progress 컴포넌트와 단계 텍스트로 진행 상태를 표시한다

#### Scenario: 라이트/다크 테마
- **WHEN** 사용자가 테마를 토글하면
- **THEN** Tailwind dark 모드 클래스가 적용되고 모든 shadcn/ui 컴포넌트가 일관되게 변경된다

### Requirement: JSON API 통신
The system SHALL communicate with the FastAPI backend exclusively through JSON endpoints.

#### Scenario: Briefing 시작 호출
- **WHEN** SPA가 분석을 시작하면
- **THEN** SPA는 `POST /api/briefing`에 path를 JSON으로 전송하고 `{ jobId, status }` JSON을 받는다

#### Scenario: Briefing 진행 상태 polling
- **WHEN** Briefing job이 진행 중이면
- **THEN** SPA는 `GET /api/briefing/status/{jobId}`를 polling하고 step과 progress 정보를 받아 UI에 반영한다

#### Scenario: 미시 탭 분석 호출
- **WHEN** 사용자가 미시 분석 탭(Quality, Hotspots, Graph 등)을 클릭하면
- **THEN** SPA는 해당 endpoint(`POST /api/{tab}`)에 path를 보내고 JSON 결과를 받아 컴포넌트로 렌더링한다

#### Scenario: HTML fragment 미사용
- **WHEN** SPA가 백엔드와 통신하면
- **THEN** 응답은 HTML fragment가 아닌 JSON 데이터이며 SPA가 모든 마크업을 생성한다

### Requirement: Briefing 매크로 화면 5개 섹션
The system SHALL render the Briefing screen as five vertically-flowing sections optimized for first-time understanding and live presentation.

#### Scenario: 섹션 순서와 정체성
- **WHEN** Briefing 결과가 표시되면
- **THEN** 화면은 위에서 아래로 "이게 뭐야 / 어떻게 만들어졌나 / 지금 상태 / 바이브코딩 인사이트 / 지금 뭘 해야 해" 순서로 다섯 섹션을 표시한다

#### Scenario: 섹션별 미시 탭 링크
- **WHEN** "어떻게 만들어졌나" 섹션이 표시되면
- **THEN** 섹션은 Graph 탭으로 이동하는 링크를 포함하고, "지금 상태" 섹션은 Quality 탭, 위험 위치는 Hotspots 탭으로 이동하는 링크를 포함한다

#### Scenario: 발표 친화적 시각
- **WHEN** Briefing 결과가 표시되면
- **THEN** 큰 제목, 충분한 여백, 한국어 본문 폰트로 발표용 화면 그대로 사용 가능한 시각 품질을 갖춘다

### Requirement: 진행 상태 UX
The system SHALL show step-by-step progress while Briefing analysis runs.

#### Scenario: 단계 텍스트 표시
- **WHEN** Briefing 분석이 진행 중이면
- **THEN** UI는 현재 단계("파일 트리 수집 중…", "핵심 파일 읽는 중…", "git history 분석 중…", "AI 해석 요청 중…", "결과 정리 중…")를 한국어 텍스트로 표시한다

#### Scenario: 빈 화면 없음
- **WHEN** 분석 시작 후 결과가 나오기 전까지
- **THEN** UI는 빈 화면 대신 진행 단계와 진행 막대를 항상 표시한다

#### Scenario: 단계 변화에 따른 시각 피드백
- **WHEN** 단계가 다음으로 넘어가면
- **THEN** UI는 단계 텍스트와 진행 막대를 부드럽게 갱신해서 멈춰 보이지 않게 한다

### Requirement: 미시 분석 영역
The system SHALL preserve access to the existing detailed analyzers as a collapsible micro-analysis area below the Briefing.

#### Scenario: 미시 영역 위치
- **WHEN** Briefing이 표시되면
- **THEN** 화면 아래쪽에 "상세 분석" 영역이 접힌 상태로 존재하고 펼치면 미시 분석 탭들이 노출된다

#### Scenario: 보존된 미시 탭
- **WHEN** 미시 영역이 펼쳐지면
- **THEN** 영역에는 Overview / Inventory / Graph / Metrics / Quality / Hotspots / Entrypoints / Report / Review / Vibe Coding / 구조 그래프 탭이 포함된다

#### Scenario: 미시 탭 결과 렌더링
- **WHEN** 사용자가 미시 탭을 클릭하면
- **THEN** SPA는 해당 분석 JSON을 받아 React 컴포넌트로 표시하며 raw JSON을 화면에 노출하지 않는다

### Requirement: 라이트/다크 테마와 영속성
The system SHALL provide light and dark themes with localStorage persistence.

#### Scenario: 테마 토글
- **WHEN** 사용자가 테마 토글을 누르면
- **THEN** UI는 light와 dark 모드 사이를 전환하고 모든 컴포넌트의 색이 일관되게 변경된다

#### Scenario: 테마 유지
- **WHEN** 사용자가 테마를 선택한 뒤 페이지를 다시 열면
- **THEN** 브라우저는 저장된 테마 preference를 적용한다

### Requirement: 최근 path 저장
The system SHALL store recent paths in browser localStorage and surface them as quick selectors.

#### Scenario: 분석 후 저장
- **WHEN** 사용자가 path로 분석을 완료하면
- **THEN** 브라우저는 해당 path를 localStorage에 저장하며 최대 5개를 최신 순으로 보관한다

#### Scenario: 최근 path 선택
- **WHEN** 사용자가 최근 path selector에서 항목을 클릭하면
- **THEN** SPA는 path input을 갱신하고 즉시 Briefing 분석을 시작한다
