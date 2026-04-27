# inventory Specification

## Purpose
TBD - created by archiving change add-inventory-cli. Update Purpose after archive.
## Requirements
### Requirement: 인벤토리 CLI 진입점
The system SHALL expose a `codexray inventory <path>` command. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray inventory <path>`를 실행하면
- **THEN** 시스템은 stdout에 인벤토리 표를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray inventory`를 실행하면
- **THEN** 시스템은 stderr에 사용법(usage) 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 입력 경로 검증
The system SHALL verify that the path argument refers to an existing directory. 파일 경로·존재하지 않는 경로·접근 불가 경로는 거부한다.

#### Scenario: 존재하지 않는 경로
- **WHEN** 사용자가 존재하지 않는 경로를 전달하면
- **THEN** 시스템은 stderr에 "path does not exist" 형태의 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 디렉토리가 아닌 경로
- **WHEN** 사용자가 일반 파일·디바이스·소켓 경로를 전달하면
- **THEN** 시스템은 stderr에 "path is not a directory" 형태의 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 파일 무시 규칙
The system SHALL exclude paths that match `.gitignore` rules within the input tree, plus a fixed default ignore set. The system MUST NOT follow symbolic links. 기본 무시 디렉토리는 `.git`, `node_modules`, `dist`, `build`, `venv`, `.venv`, `__pycache__`, `.next`, `target`이다.

#### Scenario: .gitignore 매칭
- **WHEN** 입력 디렉토리에 `.gitignore`가 있고 그 안에 `*.log` 패턴이 정의돼 있으며 트리에 `app.log` 파일이 존재할 때 인벤토리를 실행하면
- **THEN** 시스템은 `app.log`를 집계에서 제외한다

#### Scenario: 기본 무시 디렉토리
- **WHEN** 입력 디렉토리 하위에 `node_modules/` 디렉토리가 존재하고 그 안에 `.js` 파일이 다수 있을 때 인벤토리를 실행하면
- **THEN** 시스템은 `node_modules/` 내부 파일을 모두 집계에서 제외한다

#### Scenario: .gitignore 부재
- **WHEN** 입력 디렉토리에 `.gitignore`가 없을 때 인벤토리를 실행하면
- **THEN** 시스템은 기본 무시 디렉토리만 적용해 정상 집계한다

#### Scenario: 심볼릭 링크
- **WHEN** 입력 디렉토리 내부에 다른 디렉토리를 가리키는 심볼릭 링크가 존재할 때 인벤토리를 실행하면
- **THEN** 시스템은 링크를 따라가지 않으며 링크 자체는 집계에서 제외된다

### Requirement: 언어 분류
The system SHALL classify files into languages by extension using a fixed mapping table. Files whose extension is not in the table MUST be excluded from aggregation, and the system MUST NOT emit an `unknown` row. 1차 매핑 — Python(`.py`), JavaScript(`.js`, `.jsx`, `.mjs`, `.cjs`), TypeScript(`.ts`, `.tsx`), Java(`.java`), C#(`.cs`).

#### Scenario: 매핑된 확장자
- **WHEN** 트리에 `main.py`, `index.ts`, `App.tsx` 파일이 존재할 때 인벤토리를 실행하면
- **THEN** 시스템은 `main.py`를 Python, `index.ts`와 `App.tsx`를 TypeScript로 분류한다

#### Scenario: 매핑되지 않은 확장자
- **WHEN** 트리에 `README.md`, `data.json`, `logo.png` 파일만 존재할 때 인벤토리를 실행하면
- **THEN** 시스템은 빈 표를 출력하고 unknown 행을 만들지 않는다

### Requirement: 표 출력 형식
The system SHALL print a table to stdout with exactly four columns — `language`, `file_count`, `loc`, `last_modified_at` — sorted by `loc` descending. `loc` MUST be computed as the sum of non-empty lines across files of that language. `last_modified_at` MUST be the maximum mtime among files of that language, formatted as ISO-8601 in the local timezone.

#### Scenario: 다국어 코드베이스
- **WHEN** 트리에 Python 파일 3개(LoC 합 200), TypeScript 파일 1개(LoC 50)가 존재할 때 인벤토리를 실행하면
- **THEN** 시스템은 첫 번째 행에 `Python | 3 | 200 | <mtime>`, 두 번째 행에 `TypeScript | 1 | 50 | <mtime>` 순서로 출력한다

#### Scenario: LoC 계산
- **WHEN** 1개의 Python 파일이 10줄로 구성되고 그중 3줄이 빈 줄일 때 인벤토리를 실행하면
- **THEN** 시스템은 해당 언어의 `loc`를 7로 집계한다

#### Scenario: 빈 코드베이스
- **WHEN** 입력 디렉토리에 매핑된 확장자의 파일이 하나도 없을 때 인벤토리를 실행하면
- **THEN** 시스템은 헤더만 가진 빈 표를 출력하고 종료 코드 0으로 종료한다

### Requirement: 성능 예산
The system SHALL complete table output within 5 seconds on the validation codebase (사용자의 작은 게임 프로젝트, 수천 파일 이하 규모).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 게임 프로젝트 경로로 `codexray inventory`를 실행하면
- **THEN** 시스템은 5초 이내에 표 출력을 완료한다

