## Why

지금까지 만든 6개 명령(inventory/graph/metrics/entrypoints/quality/hotspots)은 모두 JSON 또는 표를 따로 출력한다. 사용자의 실제 의사결정 자료는 "1페이지 요약 + 우선순위 + 권고"다. AI 정성 평가(#3) 도입 전에, AI 비의존 결정론적 종합 리포트를 한 번 만들어 두면 후속 AI 단계가 같은 구조 위에 권고 텍스트를 더하기만 하면 된다.

## What Changes

- 새 CLI 진입점: `codexray report <path>` — 6개 파이프라인 결과를 합쳐 Markdown 1개를 stdout으로 출력
- 출력 형식: GitHub-flavored Markdown 1페이지 (사람 읽기 우선, 머신 읽기는 기존 JSON 명령 활용)
- 섹션 구성:
  1. **헤더** — 경로, 실행 날짜
  2. **종합 등급** — quality overall + 4차원 표
  3. **인벤토리** — 언어별 파일 수·LoC·최종 수정일
  4. **구조** — 노드/엣지 수, SCC 통계, 진입점 수, 진입점 종류 분포
  5. **Top Hotspots** — 상위 5개 (path · change_count · coupling · category)
  6. **권고** — 룰 기반 제안 (예: test grade F → "테스트 부족, 핵심 매니저부터 추가"; 큰 SCC → "사이클 분해 검토"; 낮은 documentation → "public API 문서화"; 1순위 hotspot → "이 파일 책임 분리 검토")
- 룰 기반 권고 (1차 비-AI):
  - quality.test.grade == F → "test ratio {x}, 핵심 모듈부터 테스트 추가"
  - quality.documentation.grade == F → "{x}/{y} 문서화, public API부터"
  - quality.coupling.grade in {D, F} → "결합도 높음. 중심 모듈 분해 검토"
  - metrics.is_dag == False → "사이클 발견 (largest SCC = {n})"
  - hotspots[0]가 있으면 → "최우선 hotspot: {path} (change={c}, coupling={k})"
- 출력 스키마 v1 — Markdown 형식 자체 + `<!-- codexray-report-v1 -->` 주석 마커로 버전 표기
- `inventory`/`graph`/`metrics`/`entrypoints`/`quality`/`hotspots` 명령은 변경 없음

## Capabilities

### New Capabilities
- `report`: 모든 분석 결과를 1페이지 Markdown으로 종합하고 룰 기반 권고를 생성하는 능력. 후속 AI 정성 평가가 같은 종합 위에 정성 권고를 더한다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/report/` 서브패키지
  - `report/build.py` — 6개 builder 호출 + 종합
  - `report/recommendations.py` — 룰 기반 권고 생성
  - `report/render.py` — Markdown 렌더링
  - `report/__init__.py`
- 신규 의존성 없음 (모두 stdlib + 기존 모듈)
- CLI에 `report` 서브커맨드 추가
- 검증: CodeXray 자기 + CivilSim, 5초 내, 결과 Markdown을 `docs/validation/report-{self,civilsim}.md`에 저장
- 구현 비용 작음 (composition만)
