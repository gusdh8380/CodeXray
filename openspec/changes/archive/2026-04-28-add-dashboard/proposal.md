## Why

`intent.md` MVP #6: "인터랙티브 대시보드 — 그래프 노드 클릭 / 함수·클래스 검색 / 파일별 평가+요약+제안". 지금까지 만든 7개 명령은 모두 JSON 또는 Markdown 출력 — 사용자가 트리 구조 + 핫스팟 + 결합도를 시각적으로 빠르게 훑기 어렵다. 1차 단추는 **단일 self-contained HTML 파일** — `constraints.md`("로컬 실행 우선, SaaS 호스팅 X")와 일관, 빌드 파이프라인·서버 의존 없음, 사용자가 `open` 한 번으로 동작.

## What Changes

- 새 CLI 진입점: `codexray dashboard <path>` — 분석 데이터를 합쳐 단일 HTML 문서를 stdout으로 출력
  - 사용 패턴: `codexray dashboard . > dashboard.html && open dashboard.html`
- 출력은 self-contained HTML — 모든 데이터는 `<script type="application/json">` 인라인, D3.js만 CDN에서 로드 (오프라인 사용은 후속)
- 시각화 (1차):
  - **force-directed 그래프** — graph internal 엣지 기반, 노드 색상은 hotspot category(`hotspot`/`active_stable`/`neglected_complex`/`stable`), 노드 크기는 `coupling`(fan_in+fan_out+external_fan_out) 비례
  - **검색 박스** — 파일 path 부분 일치 필터링, 매칭 노드만 강조
  - **상세 패널** — 노드 클릭 시 path / language / coupling 분해 / change_count / hotspot category / 진입점 종류 표시
  - **상단 헤더** — 코드베이스 path · 분석 날짜 · 종합 등급(quality.overall)
  - **범례** — 4 카테고리 색상
- 데이터 소스: `inventory`, `graph`, `metrics`, `entrypoints`, `quality`, `hotspots` 모두 호출하고 결과를 인라인 JSON 6개 블록으로 임베드. AI `review` 결과는 1차에서 미통합(후속 변경)
- 출력 스키마 v1 (신규 capability `dashboard`):
  - HTML 문서에 `<!-- codexray-dashboard-v1 -->` 마커 1회
  - 인라인 JSON 블록 ID: `codexray-data-{name}` (name ∈ {inventory, graph, metrics, entrypoints, quality, hotspots})
- 다른 명령은 변경 없음

## Capabilities

### New Capabilities
- `dashboard`: 분석 결과 6종을 단일 self-contained HTML로 임베드하고 force-directed 그래프 + 검색 + 노드 클릭 상세 패널을 제공하는 능력. 후속 변경(AI review 통합, 함수 단위 노드 분해)은 같은 HTML 위에 추가된다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/dashboard/` 서브패키지
  - `dashboard/types.py` — `DashboardData`
  - `dashboard/build.py` — 6 builder 호출 + 데이터 종합
  - `dashboard/render.py` — HTML 렌더링 (Python f-string 또는 string.Template)
  - `dashboard/template.py` — HTML/CSS/JS 정적 템플릿 (긴 multi-line 문자열)
  - `dashboard/__init__.py`
- 신규 의존성 없음 (Python 측). HTML 측은 D3.js v7 CDN
- CLI에 `dashboard` 서브커맨드 추가
- 검증: CodeXray 자기 + CivilSim 두 트리에서 HTML 파일 생성, 시각적 검증은 사용자 수동 (`open`으로 열어 확인)
- 출력 크기: 노드 수 ≤ 500까지 부담 없음. CivilSim 53 노드 + 178 엣지 = 수십 KB 예상
- 5초 예산 적용 (HTML 빌드 자체는 빠름 — `report`처럼 다수 builder 호출이 큰 비용)
