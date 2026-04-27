## Why

MVP의 모든 기능은 "코드베이스 입력 → 분석 결과"의 변형이다. 가장 작은 입력→출력 한 사이클(인벤토리 표 생성)을 먼저 만들어야 이후 의존성 그래프, 정량 평가, AI 평가가 같은 입력 인터페이스 위에 누적될 수 있다. 첫 단추로 결정론적·AI 비의존 기능을 두어 회귀 검증을 쉽게 하고, 사용자의 작은 게임 프로젝트에 dogfooding으로 즉시 검증한다.

## What Changes

- CLI 진입점 1개 추가: `codexray inventory <path>`
- 입력: 로컬 디렉토리 경로 1개만 수용 (Git URL · 압축 파일은 후속 변경에서)
- 출력: stdout에 표 1개 — 컬럼은 `language`, `file_count`, `loc`, `last_modified_at`
- 언어 감지: 확장자 기반 단순 매핑 (Python, JavaScript, TypeScript, Java, C# 우선)
- 무시 규칙: 프로젝트 `.gitignore` + 기본 디렉토리 (`node_modules`, `.git`, `dist`, `build`, `venv`, `__pycache__`)
- 비-소스 파일은 `unknown`으로 분류하지 않고 집계에서 제외

## Capabilities

### New Capabilities
- `inventory`: 디렉토리 경로를 받아 언어별 파일 수·LoC·최종 수정일을 집계해 출력하는 능력. 이후 의존성 그래프·정량 평가가 동일 워킹·필터·언어 분류 결과를 재사용한다.

### Modified Capabilities
<!-- 해당 없음 — 첫 변경이라 기존 spec 없음 -->

## Impact

- 신규 코드: CLI 엔트리 1개, 파일 워커, `.gitignore` 파서, 언어 분류 매핑 테이블, LoC 카운터, 표 포매터
- 신규 의존성: 미정 (vibe-coding 단계에서 스택과 함께 결정). `.gitignore` 파싱·표 출력은 라이브러리 후보 검토 대상
- 외부 영향 없음 — 로컬 단발 실행, 네트워크/AI 호출 없음
- 검증 기준: 사용자의 작은 게임 프로젝트에 대해 5초 내 표 출력 (전체 MVP "5분 내 분석" 목표의 하위 예산)
