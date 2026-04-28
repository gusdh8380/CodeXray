## Why

`docs/intent.md`의 must-have feature 5번은 "1페이지 종합 리포트 — 등급, **강점/약점 Top 3**, 핫스팟 리스트, 근거 라인 포함 권고"인데, 현재 `report` Markdown과 web Overview/Report 탭은 등급·hotspot·recommendation은 있지만 **"강점/약점 Top 3" 형식이 부재**하다. 이 결과로 Intent의 success criteria("리포트만 보고 다음에 무엇을 할지 결정 가능")가 실제 화면에서 충족되지 않고, 사용자가 "Overview에 잘한 점/아쉬운 점이 있으면 좋겠다"고 동일한 의도를 다시 표명하기에 이르렀다. Intent에 처음부터 명시되어 있던 핵심 산출물을 채운다.

## What Changes

- `summary` capability 신규 — 기존 quality + hotspots + metrics 결과를 입력으로, 결정론적 룰 기반으로 **강점 Top 3 / 약점 Top 3 / 다음 행동 Top 3**를 추출하는 cross-cutting builder.
- 각 항목은 한 줄 관찰 + 근거(파일·점수·등급·카운트) 의무 인용. constraints.md 원칙 "도구는 판단 근거이지 판단 자체가 아니다"와 직접 정렬.
- 룰 정의 (1차):
  - **강점**: quality dimensions 중 grade A/B 차원 + hotspot summary `stable` 비중 50% 이상 + DAG 여부(is_dag=true) + Top hotspot이 active_stable 카테고리.
  - **약점**: quality dimensions 중 grade D/F 차원 + `neglected_complex` 카테고리 파일 존재 + largest_scc_size > 1 + Top hotspot category=hotspot.
  - **다음 행동**: 약점 항목별 자동 매핑 (test grade F → "characterization test 우선", coupling F → "결합도 분해", neglected_complex 존재 → "소유권 정리", hotspot Top → "테스트 + 책임 분리", SCC > 1 → "순환 의존 끊기").
- Web UI Overview 탭 메인 영역 상단에 "강점 / 약점 / 다음 행동" 3 카드 그리드 추가.
- Web UI Report 탭 readable HTML 상단에 같은 3 섹션 추가.
- CLI `codexray report <path>` Markdown 출력에 같은 3 섹션 추가.
- AI 호출 없음 — 결정론적 룰만. 5초 게이트 그대로 통과.

## Capabilities

### New Capabilities
- `summary`: quality + hotspots + metrics + entrypoints 결과를 종합해 강점/약점/다음 행동 Top 3를 결정론적 룰로 추출하는 cross-cutting builder.

### Modified Capabilities
- `report`: Markdown 출력에 "강점 / 약점 / 다음 행동" 3 섹션이 등급 직후·핫스팟 직전에 포함되어야 함.
- `web-ui`: Overview 탭과 Report 탭의 readable HTML 상단에 같은 3 섹션이 표시되어야 하고, AI 호출 없이 즉시 렌더링되어야 함.

## Impact

- 신규 모듈: `src/codexray/summary/{__init__,types,build,serialize}.py` — 다른 capability와 동일한 디렉토리 패턴
- 변경 코드: `src/codexray/report/build.py` (summary builder 호출 추가), `src/codexray/report/render.py` 또는 markdown 생성 함수 (3 섹션), `src/codexray/web/render.py` (Overview·Report 탭 3 카드 그리드), `src/codexray/web/routes.py` (필요 시 summary endpoint)
- 신규 테스트: `tests/test_summary_build.py`, `tests/test_summary_rules.py` — 룰별 매핑·근거 인용·결정론
- 변경 테스트: `tests/test_report_recommendations.py`(또는 새 `test_report_strengths_weaknesses.py`), `tests/test_web_ui.py`
- 의존성 추가 없음
- AI 호출 없음, CLI JSON 스키마 변경 없음 (report Markdown만 추가, summary JSON은 신규)
- `docs/validation/summary-{self,civilsim}.md` 의무 캡처
