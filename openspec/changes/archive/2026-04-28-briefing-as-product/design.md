## Context

현재 index.html에는 탭 12개가 나란히 있고, 분석은 탭을 클릭해야 시작된다. 경로를 바꿔도 재분석 트리거가 없어서 사용자가 탭을 다시 클릭해야 한다는 것을 알아야 한다. Briefing이 첫 탭이지만 다른 탭들과 시각적으로 구분이 없어서 "이게 메인이다"라는 느낌이 없다.

## Goals / Non-Goals

**Goals:**
- 경로 입력 → "분석하기" 버튼 클릭 → Briefing 자동 시작
- 탭 구조를 Briefing(메인) + 상세보기(접힌 상태) 두 레벨로 재편
- 대시보드 노드 뷰포트 이탈 수정
- Vibe Coding 인사이트 슬라이드 추가 (잘한것/못한것)

**Non-Goals:**
- 탭 제거 — 기존 탭은 상세보기 섹션으로 유지
- 새 분석 엔진 추가
- 반응형 모바일 최적화

## Decisions

### 1. "분석하기" 버튼
경로 입력 폼에 `hx-post="/api/briefing"` 버튼을 추가한다. 이 버튼이 클릭되면 Briefing 탭이 active로 설정되고 분석이 시작된다. Enter 키 제출도 같은 버튼을 트리거하도록 기존 `rerunActiveTab()` 로직을 수정한다.

대안 검토: path 변경 감지 → 자동 재분석. 너무 공격적이고 사용자가 타이핑 중일 때 분석이 시작될 수 있어 명시적 버튼이 낫다.

### 2. 탭 구조 재편
- **상단 고정**: Briefing 탭만 표시 (또는 탭 자체 숨김)
- **하단 "상세 분석" 섹션**: `<details>` 태그로 기존 탭들 접어두기. 클릭하면 펼쳐지고 탭 선택 가능.

HTML 구조:
```
[분석하기 버튼] ← 메인 액션
[result-panel] ← Briefing 결과
<details class="detail-tabs">
  <summary>상세 분석 보기</summary>
  [기존 탭들: Overview, Inventory, Metrics, Quality, Hotspots, Report, Review, Graph, Entrypoints, Dashboard, Vibe Coding]
</details>
```

### 3. 대시보드 D3 레이아웃 수정
현재 문제: `forceSimulation` 실행 후 노드가 캔버스 밖으로 이탈.

수정 방법:
- `forceBoundary` 또는 `forceX/forceY` + collision 추가로 노드를 SVG bounds 내로 제한
- 뷰박스(viewBox) 설정으로 줌/패닝 기본 지원
- 중요 노드(coupling 높은 것) 크기·색상 강조

### 4. Vibe Coding 인사이트 슬라이드
기존 `codebase-briefing`의 vibe-coding process evidence(process_commits, git history)를 재활용.

슬라이드 내용:
- 잘한 것: OpenSpec 사용, 검증 문서 작성, 커밋 품질 등
- 못한 것: 테스트 부재, 문서화 부족, hotspot 방치 등
- 프로세스 근거: 감지된 프로세스 카테고리 목록

기존 `BriefingCard` 구조에 `vibe_coding` 섹션 추가. `build_codebase_briefing()`에서 기존 vibe_coding_report + hotspots + quality 데이터로 생성.

## Risks / Trade-offs

- `<details>` 탭 접기는 접근성이 좋지만 SEO나 딥링크가 어려움 → 로컬 도구이므로 무관
- Vibe Coding 슬라이드는 git history 없을 때 빈 상태 → "제작 과정 정보 없음" 표시로 처리
- 대시보드 D3 수정 후 기존 테스트는 iframe 내부 HTML을 검증하지 않으므로 테스트 영향 없음
