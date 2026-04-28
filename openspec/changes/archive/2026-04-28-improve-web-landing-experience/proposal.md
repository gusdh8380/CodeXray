## Why

비개발자가 처음 웹 UI를 열면 Inventory 탭의 숫자 테이블을 먼저 보게 된다.
"웹 화면 자체가 발표 자료로 쓸 수 있을 만큼 깔끔하다"는 Intent를 달성하려면
Briefing이 랜딩 경험이어야 하고, 원시 데이터 탭은 뒤로 밀려야 한다.

## What Changes

- Briefing 탭을 기본 활성 탭(랜딩 뷰)으로 변경
- 탭 순서 재구성: Briefing → Overview → 상세 탭들 (Inventory, Metrics, Quality, Hotspots, Report, AI Review)
- 상세 탭 그룹에 "Developer Detail" 레이블 또는 시각적 구분선 추가
- 각 탭의 raw JSON `_raw_details` 섹션 제거 (개발자 디버그용 노이즈)
- Insight 텍스트 영어 → 한국어 통일

## Capabilities

### New Capabilities
- (없음)

### Modified Capabilities
- `web-ui`: 탭 순서 및 기본 활성 탭 변경, raw details 제거, insight 텍스트 한국어화
- `codebase-briefing`: Briefing이 랜딩 뷰가 되므로 첫 슬라이드 진입 경험 보강

## Impact

- `src/codexray/web/render.py` — `_raw_details` 제거, insight 텍스트 한국어화
- `src/codexray/web/templates/` — 탭 순서 및 기본 탭 변경
- `src/codexray/web/static/app.js` (또는 인라인 JS) — 기본 활성 탭 로직
- 기존 테스트 `tests/test_web_ui.py` — 탭 순서 관련 어서션 업데이트 필요
