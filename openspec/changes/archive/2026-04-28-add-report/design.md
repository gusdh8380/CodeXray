## Context

6개 분석 명령이 모두 안정. 이번 변경은 새 분석 로직 추가가 아니라 **컴포지션** — 기존 JSON 데이터를 사람 읽기 좋은 Markdown으로 묶기 + 룰 기반 권고를 생성. AI 정성 평가는 후속 변경. 1차에서 결정론적 룰만 도입해 안정 기반 마련.

## Goals / Non-Goals

**Goals:**
- 1페이지 Markdown 1개로 사용자가 의사결정에 필요한 정보 한눈에
- 결정론적 (같은 입력 = 같은 출력)
- 5초 예산 (6 builder 호출이지만 redundant work 1차 수용)
- 룰 기반 권고 — AI 비의존, 명세 가능

**Non-Goals:**
- AI 정성 평가 — 별도 후속 변경
- HTML/PDF 출력 — 후속
- 인터랙티브 (웹 UI) — 별도 capability
- 시각적 그래프 (DOT/SVG) — 후속
- 사용자 정의 권고 룰 (config) — 1차 비대상

## Decisions

### Decision 1: 별도 명령 (`report`) — 다른 명령 변경 없음
같은 패턴. 출력 형식이 Markdown으로 다르므로 별도 capability로 격리.

### Decision 2: 출력 형식 — Markdown
- GitHub-flavored Markdown 표 + 헤더 + 코드 블록
- `<!-- codexray-report-v1 -->` 주석으로 스키마 버전 마커
- 후속 변경에서 v2로 갈 때 마커 갱신
- `--format json` 같은 옵션은 1차 비대상 (Markdown만)

### Decision 3: 6개 builder 직접 호출
- `inventory.aggregate(root)`
- `graph.build_graph(root)`
- `metrics.build_metrics(graph)` (graph 재사용)
- `entrypoints.build_entrypoints(root)`
- `quality.build_quality(root)` — 내부에서 graph 다시 빌드 (redundant work)
- `hotspots.build_hotspots(root)` — 내부에서 graph + metrics 다시 빌드 (redundant work)

**redundant work**: graph 빌드가 3번 수행됨. 1차 수용 — CivilSim 53 노드에서 graph 0.5s × 3 = 1.5s + 다른 작업 = 5초 안에. 검증으로 확인. 5초 초과 시 `Pipeline` 클래스로 캐싱 도입.

### Decision 4: 룰 기반 권고 — 단일 모듈
- `report/recommendations.py`에 `generate(...) -> list[str]`
- 입력: quality, metrics, hotspots, entrypoints, inventory 결과 dict
- 출력: 우선순위 정렬된 권고 문자열 list
- 룰:
  1. **하강 임계 검사** — quality.dimensions 중 grade가 D/F인 차원에 대해 차원별 권고 생성
  2. **사이클 검사** — metrics.is_dag == False면 사이클 권고
  3. **Top hotspot** — hotspots.summary.hotspot >= 1이면 가장 큰 hotspot 권고
  4. **진입점 부재** — entrypoints가 0이면 "진입점이 식별되지 않음, 도달성 분석 불가능" 경고

### Decision 5: 권고 우선순위 — 점수 기반 정렬
각 권고에 우선순위 점수 부여:
- 100: 1순위 hotspot 권고 (사용자가 가장 먼저 행동할 영역)
- 80: 등급 F 차원 권고 (가장 약한 차원)
- 60: 사이클 권고 (구조적 문제)
- 40: 등급 D 차원 권고
- 20: 진입점 부재 경고 (정보성)

상위 5개만 리포트에 표시. 결정론적: 동률은 차원/카테고리 알파벳 순.

### Decision 6: 헤더의 "Date" — 실행 날짜 (KST 로컬 타임존)
- ISO-8601 형식 (`2026-04-28`)
- 결정론을 위해 — 실행 날짜는 결정론을 깨지만 사용자에게 의미 있는 정보. 테스트는 마커만 검증, 날짜 값은 검증 안 함.

### Decision 7: 패키지 구조
- `report/__init__.py` — `build_report`, `to_markdown`
- `report/build.py` — `build_report(root: Path) -> ReportData`
- `report/recommendations.py` — `generate(...) -> list[Recommendation]`
- `report/render.py` — `to_markdown(data: ReportData) -> str`
- `report/types.py` — `ReportData`, `Recommendation`

### Decision 8: ReportData = 모든 builder 결과 dict
- 단순 컨테이너 dataclass
- 후속에서 AI 권고 추가 시 같은 dataclass에 키 추가

## Risks / Trade-offs

- **[리스크] Redundant graph 빌드 3회** — 작은 트리에선 무관, 큰 트리에선 누적 비용. 검증으로 확인. 5초 초과 시 후속 변경에서 graph caching pipeline.
- **[리스크] 룰 기반 권고가 너무 일반적** — "테스트 추가" 같은 권고는 누구나 알 수 있음. AI 정성 평가 후속에서 특정 모듈·라인 수준 권고로 정밀화.
- **[리스크] Markdown 출력에 stdout/터미널 색상 등 환경 영향** — `to_markdown`은 순수 문자열 반환, color 없음. 결정론 보장.
- **[리스크] 종합 등급 표기가 사용자에게 잘못된 안정감을 줄 수 있음** — "B" 받았다고 안전하지 않음. 권고 문구에 "이 등급은 정량 신호 + AI 평가 결과 합산이 아님" 명시 가능 (1차 미도입).
- **[트레이드오프] 사용자별 임계치 커스터마이즈 불가** — 1차 고정. 나중에 환경변수·config로 조정 가능.

## Open Questions

- 권고 5개 상한이 적절한가? — 1차 5개. 검증으로 조정.
- 진입점 종류 분포(예: 34 unity_lifecycle)를 권고에 활용해야 하나? (Unity 프로젝트 식별 자동) — 1차 비대상.
- 등급 N/A 차원(예: documentation N/A in JS-only tree)을 권고에서 어떻게 다룰지 — 1차 단순 skip.
