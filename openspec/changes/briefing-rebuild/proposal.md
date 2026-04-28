## Why

현재 Briefing은 의도와 어긋나 있다. "웹 화면 자체가 발표 자료"여야 하는데 수치 나열에 가깝고, "코드를 몰라도 다음 행동을 파악"해야 하는데 비개발자에게 맥락이 없다. 추가로 바이브코딩 인사이트가 의도의 핵심인데 체크리스트 수준으로만 표현되어 있어 "잘했냐"의 판단 기준이 모호하다. 프론트엔드도 htmx 기반의 부분 렌더링으로 발표 품질에 도달하지 못한다.

처음 본 사람이 "이게 뭐고 / 어떤 상태고 / 뭘 먼저 봐야 하는지" 한 화면에서 명확하게 파악하도록 Briefing을 매크로 방향 잡기 화면으로 재설계하고, 바이브코딩 진단을 핵심 차별점으로 만든다.

## What Changes

- Briefing 화면을 5개 섹션으로 재구성: 이게 뭐야 / 어떻게 만들어졌나 / 지금 상태 / 바이브코딩 인사이트 / 지금 뭘 해야 해
- 바이브코딩 자동 판별 도입 (강한·중간·약한 신호) — 감지 시 3축 평가(환경 구축 / 개발 과정 깔끔함 / 이어받기 가능성), 미감지 시 시작 가이드
- 개발 과정 타임라인 시각화 — git 히스토리에서 프로세스 도입 시점과 코드/명세/검증 흐름 복원
- 다음 행동 형식 변경: "행동 + 왜 + 분석 증거 인용" 세트 (단순 체크리스트 폐기)
- AI 입력 방식 변경 — 처리된 JSON 메트릭이 아니라 원본 소스코드 + git history → codex CLI
- **BREAKING** 프론트엔드 전면 교체: htmx + Jinja → React + Vite + Tailwind + shadcn/ui (FastAPI는 JSON API만 제공, 빌드 결과를 정적 서빙)
- **BREAKING** 분석하기 버튼 제거 — 경로 입력 + Enter 또는 자동 분석으로 단순화
- 보이지 않던 PPT 슬라이드 구현 폐기 (개념은 5개 섹션으로 흡수)
- Dashboard는 이름만 변경하고 내부 구현은 후속 변경으로 미룸
- 시니어 개발자 깊이 만족 일단 아카이브 (후속 변경)
- 미시 분석 탭들(Quality, Hotspots, Graph, Inventory, Metrics, Entrypoints, Report, Review, Vibe Coding)은 새 프론트로 포팅하여 유지

## Capabilities

### New Capabilities
- `vibe-coding-insights`: 바이브코딩 자동 판별과 3축 진단(환경 구축 / 개발 과정 깔끔함 / 이어받기 가능성), 개발 과정 타임라인, 행동+왜 형식의 다음 프로세스 행동
- `react-frontend`: React + Vite + Tailwind + shadcn/ui로 구성된 SPA. FastAPI가 빌드 결과를 정적 서빙하며 JSON API와 통신

### Modified Capabilities
- `codebase-briefing`: 5개 섹션 매크로 화면으로 재정의, AI 입력은 원본 코드+git history, 다음 행동은 행동+왜+증거 형식
- `web-ui`: htmx 기반 서버 사이드 렌더링에서 React SPA + JSON API로 전환. 분석하기 버튼 제거, 메인 진입은 경로 입력 후 자동 분석 또는 Enter

## Impact

- `src/codexray/web/` — 라우트가 HTML fragment 대신 JSON 응답으로 전환
- `src/codexray/web/templates/` — 사실상 폐기 (index.html은 React SPA 진입점만)
- `src/codexray/web/static/` — 폐기, 새 프론트엔드 빌드 결과로 대체
- 새 디렉토리 `frontend/` — React + Vite 프로젝트, `frontend/dist`를 FastAPI가 서빙
- `src/codexray/briefing/` — 5개 섹션 빌더로 재구성, AI 프롬프트가 원본 코드 입력 받도록 변경
- 새 모듈 `src/codexray/vibe_insights/` — 자동 판별, 3축 평가, 타임라인 데이터 생성
- `src/codexray/web/ai_briefing.py` — 입력 포맷 변경 (JSON → raw code bundle)
- 기존 `briefing-as-product`, `humanize-analysis-output` 등 미아카이브 변경은 본 변경에 흡수
- 의존성 추가: Node.js (개발), npm 패키지(react, vite, tailwindcss, shadcn/ui 컴포넌트)
- 빌드 절차 변경: `npm run build` → `frontend/dist/` → FastAPI 정적 서빙
