## Context

현재 result panel은 좌측부터 내용이 흐르고 넓은 화면에서 오른쪽 여백이 생긴다. 이 공간을 설명 패널로 쓰면 화면 밀도를 높이면서도 JSON/표만으로 부족한 해석 경험을 보완할 수 있다.

## Goals / Non-Goals

**Goals:**
- 7개 deterministic analysis panel에 한국어 설명 sidebar 제공
- 시니어 개발자 관점의 리스크, 해석 기준, 다음 행동을 제시
- responsive layout 유지
- raw JSON은 계속 secondary detail로 유지
- macOS에서 Path 입력을 Finder folder picker로 채울 수 있게 함

**Non-Goals:**
- AI로 설명 생성
- 사용자별 설명 커스터마이징
- Dashboard/Review 설명 sidebar
- React migration
- Cross-platform native folder picker

## Decisions

### Decision 1: Static deterministic copy

설명은 AI 생성이 아니라 정적 한국어 copy로 둔다. 같은 분석 결과에 같은 화면을 보장하고, 외부 호출 없이 빠르게 렌더링한다.

### Decision 2: Two-column panel layout

넓은 화면에서는 `analysis-layout`을 사용해 왼쪽에 결과, 오른쪽에 설명을 둔다. 좁은 화면에서는 1열로 접는다.

### Decision 3: Senior framing

각 설명은 다음 구조를 따른다.
- 이 화면이 무엇인지
- 의미 있는 신호가 무엇인지
- 시니어 개발자가 다음에 무엇을 할지

### Decision 4: macOS folder picker via local server

브라우저는 보안상 일반 웹 API로 로컬 절대 경로를 안정적으로 제공하지 않는다. 이 앱은 localhost 단일 사용자 Python 서버이므로 macOS에서는 `osascript`의 `choose folder`를 서버가 실행하고 POSIX path를 반환한다. htmx out-of-band swap으로 path input 값을 갱신한다.

## Risks / Trade-offs

- **[트레이드오프] 정적 설명은 프로젝트별 맥락을 완전히 반영하지 못함**: 대신 안정적이고 빠르다.
- **[리스크] 화면이 장황해질 수 있음**: 오른쪽 별도 영역으로 분리해 표 읽기를 방해하지 않는다.
- **[리스크] folder picker는 macOS 전용**: 다른 OS에서는 명확한 오류 fragment를 반환하고 수동 입력을 유지한다.
