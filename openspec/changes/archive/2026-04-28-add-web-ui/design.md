## Context

MVP 분석 capability는 이미 CLI로 안정화되어 있다. 이번 변경의 핵심은 분석 로직이 아니라 제어면이다. 사용자는 path를 입력하고, 탭을 눌러 각 분석 결과를 확인하고, 필요할 때만 AI review를 실행한다.

서버는 로컬 머신에서만 실행한다. 외부 SaaS, 계정, 원격 저장소 업로드는 도입하지 않는다.

## Goals / Non-Goals

**Goals:**
- `codexray serve` 한 번으로 localhost 웹 UI 실행
- 기본적으로 브라우저 자동 오픈
- 빌드 파이프라인 없는 htmx + Jinja2 UI
- 기존 8개 분석 명령 결과를 탭 UI에서 실행/조회
- path 입력과 최근 5개 path history 제공
- AI review는 명시 클릭 + 시간 경고 후 실행
- endpoint smoke가 self/CivilSim에서 5초 내 의미 있는 결과를 반환

**Non-Goals:**
- 멀티 사용자 인증/권한
- 원격 SaaS 호스팅
- 프로젝트 파일 업로드
- 장기 실행 job queue, database, background worker
- React/Vite SPA 빌드 파이프라인
- 실시간 스트리밍 AI review
- 분석 결과 영구 캐시
- dashboard 시각화 로직 재작성

## Decisions

### Decision 1: Backend stack — FastAPI + uvicorn

FastAPI는 Python codebase 안에서 분석 builder를 직접 호출하기 쉽고, 테스트 클라이언트로 route smoke를 검증하기 쉽다. `uvicorn`은 `codexray serve`의 로컬 개발 서버 역할만 한다.

**대안 기각:**
- Flask: 충분히 가능하지만 async route, typed request, OpenAPI 자동 문서 면에서 FastAPI가 더 낫다.
- Node backend: 기존 Python builder를 다시 shell-out해야 하므로 불필요하다.

### Decision 2: Frontend stack — htmx + Jinja2

사용자가 2026-04-28에 htmx + Jinja2를 선택했다. 1차 UI는 form submit, tab button, result panel swap이 대부분이라 서버 주도 렌더링이 코드량과 유지보수 비용을 낮춘다. 빌드 파이프라인이 없어 기존 dashboard의 "vanilla first" 방향과도 일관된다.

**대안 기각:**
- Alpine.js: local state에는 좋지만 서버 fragment swap 중심이면 htmx가 더 직접적이다.
- Preact CDN: React식 component 모델은 장점이지만 이번 UI에는 상태 복잡도가 작다.
- React + Vite: 장기 SPA에는 좋지만 1차 단추에는 의존성과 빌드가 무겁다.

### Decision 3: htmx delivery — CDN script tag

1차 구현은 htmx를 CDN에서 로드한다. 서버는 정적 CSS/JS만 제공한다. 오프라인 완전 동작은 후속 변경에서 htmx vendoring으로 다룬다.

근거: 현재 dashboard도 D3 v7 CDN을 사용한다. 이번 변경은 웹 UI 구조 검증이 우선이고, 완전 오프라인 번들링은 별도 capability 가치가 있다.

### Decision 4: Result rendering

- Inventory/Graph/Metrics/Entrypoints/Quality/Hotspots/Review: pretty JSON fragment
- Report: Markdown을 제한된 HTML로 렌더링하거나 `<pre>` fallback으로 표시
- Dashboard: 기존 `dashboard.to_html` 결과를 sandboxed iframe `srcdoc`로 표시
- Overview: quality/report/hotspots를 조합한 짧은 summary fragment

모든 endpoint는 htmx 요청에 HTML fragment를 반환한다. JSON API는 1차에서 별도 public contract로 만들지 않는다.

### Decision 5: Path validation

사용자 입력 path는 서버에서 `Path.expanduser().resolve()` 후 존재하는 directory인지 확인한다. 실패 시 HTTP 400과 오류 fragment를 반환한다. 분석 builder에는 resolve된 directory path를 넘기되, 출력 내부 path는 기존 builder의 root-relative POSIX 정책을 따른다.

### Decision 6: Browser open behavior

`codexray serve`는 기본적으로 `http://127.0.0.1:<port>/`를 시스템 브라우저로 연다. `--no-browser`를 주면 열지 않는다. 테스트와 자동화에 필요하기 때문이다.

### Decision 7: AI review opt-in

AI review endpoint는 Review 탭을 클릭하거나 Review 실행 버튼을 눌렀을 때만 호출된다. Overview나 Analyze 전체 실행에 포함하지 않는다. UI에는 "1-5 minutes" 수준의 명시 경고를 표시한다.

근거: AI 호출은 비용과 시간이 크고, 안전장치가 있더라도 결정론적 정량 분석 위에 얹는 정성 평가로 유지해야 한다.

### Decision 8: No persistent server cache

1차 구현은 요청마다 builder를 실행한다. 최근 path history는 browser localStorage에만 저장한다.

**대안:** path별 in-memory cache. 결과가 빠르게 보일 수 있지만 git 상태와 파일 변경을 놓칠 수 있어 1차에서는 제외한다.

### Decision 9: Package structure

```
src/codexray/web/
├── __init__.py
├── server.py
├── routes.py
├── render.py
├── templates/
│   ├── index.html
│   └── fragments/
└── static/
    ├── app.css
    └── app.js
```

분석 데이터 생성은 기존 capability builder/serializer를 재사용한다. 새 분석 로직은 만들지 않는다.

## Risks / Trade-offs

- **[리스크] CDN 차단 또는 오프라인**: htmx가 로드되지 않으면 탭 실행이 깨진다. 후속 변경에서 htmx vendoring으로 완전 로컬화한다.
- **[리스크] long-running review 요청 timeout**: 1차는 명시 클릭과 경고만 제공한다. polling/streaming은 후속.
- **[리스크] Markdown 렌더링 안전성**: 외부 markdown 라이브러리를 추가하지 않고 escaping + minimal formatting 또는 `<pre>` fallback으로 시작한다.
- **[트레이드오프] 요청마다 분석 재실행**: 단순하고 최신 결과를 보장하지만 탭 전환이 느릴 수 있다. self/CivilSim 검증 후 캐시가 필요하면 별도 변경으로 도입한다.
- **[리스크] localhost server lifecycle**: 포트 충돌 시 uvicorn error가 발생한다. 1차는 사용자가 `--port`로 변경한다.

## Open Questions

- htmx vendoring을 이번 변경에 포함할지 여부: 1차는 CDN, 후속에서 검토.
- Overview가 어떤 aggregate를 기본으로 보여줄지: 구현 중 report/quality/hotspots 데이터를 보고 최소 summary로 조정.
- Report Markdown을 HTML로 최소 변환할지 `<pre>`로 둘지: 테스트와 보안 단순성을 우선해 결정.
