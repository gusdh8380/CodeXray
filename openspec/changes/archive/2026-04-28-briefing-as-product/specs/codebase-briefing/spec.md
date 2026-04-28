## ADDED Requirements

### Requirement: Vibe Coding 인사이트 슬라이드
The system SHALL build a dedicated Vibe Coding insights slide that evaluates git history and project folder structure from a vibe coding process perspective, clearly identifying what went well and what needs improvement.

#### Scenario: 잘한 것 목록 생성
- **WHEN** git history 또는 프로젝트 폴더에서 OpenSpec, 검증 문서, 회고록, AGENTS.md, CLAUDE.md 등의 프로세스 아티팩트가 감지되면
- **THEN** 슬라이드는 감지된 아티팩트를 근거로 잘 수행된 프로세스 항목 목록을 포함한다

#### Scenario: 못한 것 목록 생성
- **WHEN** quality 등급이 C 이하이거나 test dimension이 낮거나 hotspot 파일이 다수이면
- **THEN** 슬라이드는 테스트 부재, 문서화 부족, hotspot 방치 등 개선이 필요한 항목 목록을 포함한다

#### Scenario: 프로세스 증거 없을 때 폴백
- **WHEN** git history가 없거나 프로세스 카테고리 커밋이 0개이면
- **THEN** 슬라이드는 "바이브코딩 프로세스 증거를 감지하지 못했습니다" 안내와 함께 품질 지표 기반의 기본 평가를 표시한다

#### Scenario: 슬라이드 직렬화
- **WHEN** 동일 레포를 동일 상태에서 두 번 분석하면
- **THEN** Vibe Coding 슬라이드의 직렬화 결과는 동일하다
