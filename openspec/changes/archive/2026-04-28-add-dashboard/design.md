## Context

7개 분석 명령 안정. 이번 변경은 시각화 — 새 분석 로직 X, 기존 데이터를 브라우저에서 보기 좋게 합치기. 1차 단추는 의도적으로 단순 — 빌드 파이프라인·로컬 서버 없이 단일 HTML로 시작. 사용자 환경(Mac + 브라우저)에서 즉시 동작.

## Goals / Non-Goals

**Goals:**
- 단일 HTML 파일 (외부 데이터 fetch 없음) — file:// 로 열어도 동작
- 6개 분석 데이터(inventory/graph/metrics/entrypoints/quality/hotspots) 한 번에 시각화
- 노드 클릭 → 상세 패널 즉시 갱신
- 검색 박스 → 파일 path 부분 일치
- 결정론적 HTML 출력 (날짜 외 동일 입력 = 동일 출력)
- 기존 analytics 5초 예산 위에서 HTML 렌더 자체는 < 1s

**Non-Goals:**
- AI review 결과 임베드 — 후속 변경 `add-dashboard-with-review`
- 함수 단위 시각화 — 호출 그래프 capability가 추가된 후
- Diff/Compare 두 코드베이스 — 별도 기능
- 시간 축 애니메이션 (변경 빈도 over time) — 후속
- 사용자 환경설정·테마 — 후속
- 오프라인 D3 임베드 — CDN으로 시작, 후속 변경에서 D3 인라인 가능
- HTTP 서버 모드(`codexray dashboard --serve`) — 후속
- React/Vue 등 SPA 프레임워크 — 1차 비대상

## Decisions

### Decision 1: 출력 — stdout HTML
- 다른 명령과 일관 (`>` 리다이렉트 자유)
- `codexray dashboard . > dashboard.html`

### Decision 2: 단일 self-contained HTML
- `<script type="application/json" id="codexray-data-{name}">...JSON...</script>` 6 블록
- D3.js v7 — CDN script tag (`https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js`)
- 모든 시각화 JS는 인라인 `<script>` 1개
- CSS도 인라인 `<style>` 1개

**대안 기각:**
- React/Vue: 빌드 파이프라인 필요, 1차 비대상
- iframe + 외부 JSON: 보안·로컬 file:// 환경에서 fetch 불가 (CORS), 1차 비대상

### Decision 3: D3.js force-directed
- 표준 그래프 시각화. 코드량 작고 D3 v7는 안정.
- 대안: cytoscape.js(360KB, 더 무겁지만 인터랙션 풍부) — 후속 변경 검토
- 대안: DIY canvas force simulation — 코드 더 많고 유지보수 비용 큼

### Decision 4: 노드 색상 — hotspot category 4가지
- `hotspot`: 빨강 (#dc2626)
- `active_stable`: 주황 (#f59e0b)
- `neglected_complex`: 노랑 (#eab308)
- `stable`: 회색 (#9ca3af)

근거: hotspot이 사용자의 우선 의사결정 차원. 색상 4가지로 그래프 한눈에 분포 확인 가능.

**대안:** 언어별 색상, 결합도 그라데이션 등 — 후속 변경에서 토글 옵션화.

### Decision 5: 노드 크기 — log(coupling + 1) × 4 + 4
- 결합도 큰 노드가 시각적으로 두드러짐
- 로그 스케일 — 한 노드의 coupling이 매우 커도 화면 안에 들어옴
- 최소 4px(zero-coupling 노드도 보임), 최대 ~50px 수준

### Decision 6: 엣지
- internal 엣지만 (external은 노드에 상응 노드 없음)
- 화살표 마커로 방향 표시
- 회색 (#cbd5e1), 두께 1.5px

### Decision 7: 상세 패널 항목
노드 클릭 시 표시:
- `path` (큰 글씨)
- `language`
- `coupling` 분해: `fan_in`, `fan_out`, `external_fan_out`
- `change_count` (git 비저장소면 N/A)
- `hotspot category` (배지)
- `entrypoint kinds` (해당 노드가 진입점이면 종류 list)

후속에 추가 가능: AI review 요약, source preview snippet.

### Decision 8: 검색
- 단순 case-insensitive substring 매치
- 매칭 노드는 highlight (테두리), 비매칭은 opacity 0.2
- 검색 빈 문자열 → 모두 일반 표시

### Decision 9: 패키지 구조 — `src/codexray/dashboard/`
- `dashboard/types.py` — `DashboardData`
- `dashboard/build.py` — 6 builder 호출 → DashboardData
- `dashboard/template.py` — `HTML_TEMPLATE` 모듈 변수 (큰 multi-line 문자열)
- `dashboard/render.py` — `to_html(data) -> str`
- `dashboard/__init__.py`

### Decision 10: 결정론
- `generated_date`만 비결정적 (사용자에게 의미 있음)
- nodes/edges/quality/hotspots 모두 기존 결정론 유지
- 테스트는 마커 + 인라인 JSON 키 존재만 검증, 날짜 미검증

## Risks / Trade-offs

- **[리스크] D3 CDN 차단·오프라인** → 그래프 안 보임. 텍스트 기반 데이터(JSON)는 보임. 후속 변경에서 D3 인라인 옵션화.
- **[리스크] 노드 수 1000+ 트리에서 force simulation 느림** → 1차 검증은 53(CivilSim)·30(CodeXray) 노드. 큰 트리는 후속 변경에서 노드 군집 또는 viewport-based 가상화.
- **[리스크] file:// 보안 정책** → 인라인 JSON·CDN script만 쓰면 OK. fetch/XHR 없음.
- **[트레이드오프] 단일 HTML 크기 큼** → CivilSim 53 노드 + 178 엣지 + 모든 분석 데이터 = ~50KB 추정. 후속에서 압축·data shrink 옵션.
- **[리스크] 사용자가 수동으로 `open` 해야 함** → CLI에 `--open` 플래그 1차 비도입(검증을 사용자에게 떠넘김). 후속에서 `subprocess.run(["open", path])` 옵션.

## Open Questions

- D3 v7 vs cytoscape — 1차는 D3로. 인터랙션 한계 도달 시 후속에서 cytoscape로 마이그레이션.
- 진입점 노드 강조(별 아이콘 등) — 1차 미도입, 후속에서 시각 보강.
- Quality dimension 차원별 색상 토글 — 후속.
