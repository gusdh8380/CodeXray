## 1. "분석하기" 버튼 추가

- [x] 1.1 `index.html` path form에 `hx-post="/api/briefing"` 버튼 "분석하기" 추가 — Briefing 탭을 active로 설정하고 result-panel을 업데이트하는 primary-action 버튼
- [x] 1.2 `app.js` Enter 키 제출이 "분석하기" 버튼을 클릭하도록 `rerunActiveTab()` 대신 버튼 click 트리거로 수정

## 2. 탭 구조 재편 (index.html + app.css)

- [x] 2.1 `index.html`에서 Briefing 탭 버튼 제외한 모든 탭을 `<details class="detail-tabs"><summary>상세 분석 보기</summary>...</details>` 로 감싸기
- [x] 2.2 `app.css`에 `.detail-tabs` 스타일 추가 — 접힌 상태에서 subtle하게 표시, 펼쳤을 때 기존 탭 스타일 유지

## 3. 대시보드 노드 뷰포트 이탈 수정 (dashboard/template.py)

- [x] 3.1 D3 simulation에 `forceX(width/2).strength(0.08)` + `forceY(height/2).strength(0.08)` 추가하여 노드를 중앙 방향으로 당기기
- [x] 3.2 tick 핸들러에서 각 노드의 x/y를 `Math.max(r, Math.min(width-r, d.x))` 로 clamp하여 뷰포트 이탈 방지
- [x] 3.3 coupling 높은 노드(상위 10%) 반지름을 1.5배, 색상을 강조색으로 변경

## 4. Vibe Coding 인사이트 슬라이드 (briefing/build.py)

- [x] 4.1 `_build_vibe_insights(vibe, quality, hotspots, history) -> BriefingSlide` 함수 작성
  - 잘한 것: history.process_commits에서 감지된 카테고리 목록 + vibe 아티팩트
  - 못한 것: quality dimension 낮은 것, hotspot 수, 테스트 부재 여부
  - 폴백: process_commits 없으면 "프로세스 증거 미감지" 메시지
- [x] 4.2 `build_codebase_briefing()`에서 `presentation_slides` 튜플에 Vibe Coding 슬라이드 추가 (How Built 슬라이드 뒤에)

## 5. 테스트 업데이트 및 검증

- [x] 5.1 `uv run pytest tests/ -x` 전체 통과 확인 — index.html/탭 구조 변경에 따른 어서션 업데이트
- [x] 5.2 브라우저에서 CivilSim 경로 입력 후 "분석하기" 버튼 클릭 → Briefing 자동 시작 확인
- [x] 5.3 "상세 분석 보기" 클릭 → 탭들 펼쳐짐 확인
- [x] 5.4 대시보드 탭에서 노드가 뷰포트 안에 모두 보이는지 확인
- [x] 5.5 Briefing 슬라이드 중 Vibe Coding 슬라이드가 표시되는지 확인
