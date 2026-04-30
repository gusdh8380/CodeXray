## Context

자체 분석 결과 "다음 행동" 추천이 엔트리포인트 파일을 위험 1·2위로 잡는 false positive를 일으킨다. 근본적으로는 추천 엔진의 시그널 다양성과 도메인 인식이 부족한 탓이지만, 그 큰 작업은 별도 변경의 몫이다. 본 변경은 **사용자가 추천을 비판적으로 받아들이게 만드는 데** 집중한다.

핵심 가설 — 추천을 카테고리(코드 / 구조 / 바이브코딩)로 분리하면 사용자가 어떤 종류의 행동인지 한 눈에 파악하고, 자기 상황에 맞는 우선순위를 매길 수 있다. 또한 "AI가 자동 생성한 추천이라 부정확할 수 있음" 경고를 명시하면 무비판적 적용을 줄일 수 있다.

## Decision Points

### D1. 카테고리 분류 — 누가 결정하나
**선택지:**
- (a) AI가 프롬프트에서 직접 분류
- (b) 백엔드가 키워드/규칙 기반으로 분류
- (c) 하이브리드 — AI가 일차 분류, 백엔드가 sanity check

**결정: (a)** — AI가 직접 카테고리 필드를 채워서 반환.

**이유:** AI는 행동의 성격(코드 변경 vs 아키텍처 vs 프로세스)을 의미론적으로 가장 잘 판단함. 백엔드 키워드 분류는 단어 함정에 빠지기 쉬움 (예: "리팩토링"이라는 단어로는 코드/구조 구분 불가). 본 변경은 분류 정확도 자체를 검증하지 않으므로 단순화된 (a)로 충분. 추후 sanity check가 필요하면 별도 변경에서 추가.

### D2. vibe_coding 카테고리 데이터 출처
**선택지:**
- (a) AI가 vibe_insights 데이터를 보고 vibe_coding 카테고리 행동 직접 생성
- (b) 기존 `briefing.vibe_insights.next_actions` 또는 `starter_guide` 를 그대로 vibe_coding 카테고리에 흡수

**결정: (b)**

**이유:** vibe_insights는 이미 자체 next_actions / starter_guide 를 생성한다 (감지/미감지에 따라). AI에게 또 생성시키면 중복 + 일관성 문제 발생. 백엔드에서 vibe_insights 결과를 가져와 `category="vibe_coding"` 으로 표시 + 평면 리스트에 합치는 게 단순. AI는 `code` / `structural` 두 카테고리만 책임.

### D3. 데이터 형태 — 평면 리스트 vs 그룹화 dict
**선택지:**
- (a) `next_actions: [{..., category: "code" | "structural" | "vibe_coding"}]`
- (b) `next_actions: { code: [...], structural: [...], vibe_coding: [...] }`

**결정: (a)**

**이유:** 평면 리스트가 직렬화 단순, 카테고리 추가/이름변경 시 키 추가만 됨, 프론트가 `groupBy(category)`로 한 줄 처리 가능. (b)는 비어있는 카테고리 처리가 모호 (`null` vs `[]` vs 키 누락). 결정론적 어서션도 (a)가 단순.

### D4. 경고 배너 배치 / 디자인
**선택지:**
- (a) 다음 행동 섹션 상단에 항상 표시
- (b) 첫 방문에만 표시 + dismissable
- (c) 추천 카드 옆 작은 (?) 툴팁

**결정: (a)** — 항상 표시.

**이유:** 본 변경의 핵심은 "사용자가 무비판적으로 적용하지 않게 하기"이므로 매번 보여야 효과 있음. dismissable은 점점 안 보게 됨. amber 톤으로 부담스럽지 않게, 한 줄짜리 배너. dark 테마에서도 보이게 색상 토큰 검증.

### D5. 카테고리 누락 / fallback
**선택지:**
- (a) 카테고리 누락 시 기본 `code`
- (b) 카테고리 누락 항목은 표시 안 함
- (c) 별도 "기타" 그룹

**결정: (a)** — 누락 시 `code` 기본값.

**이유:** 캐시된 v4 응답이나 AI가 카테고리 필드를 빼먹은 경우에도 화면이 비지 않게. `code`는 가장 일반적이라 안전한 기본값. parse 단에서 `category not in {"code", "structural", "vibe_coding"}` 이면 `code`로 강제.

### D6. SCHEMA_VERSION bump 여부
**결정: 2 → 3.**

**이유:** payload의 `next_actions[].category` 필드는 신규 키. 클라이언트가 이를 기대하면 캐시된 v2 응답은 깨짐. 단, 백엔드는 v2 응답을 받으면 모든 항목을 `category="code"` 로 강제하는 호환 처리. PROMPT_VERSION도 v4 → v5 (AI 응답 캐시 무효화).

## Risks / Trade-offs

| 위험 | 영향 | 완화 |
|---|---|---|
| AI가 카테고리 분류를 자주 틀림 | 화면 그룹이 부자연스러워짐 | 본 변경 범위 밖 — 후속 변경에서 sanity check |
| vibe_coding 카테고리가 vibe_insights 섹션과 시각적 중복 | 화면 정보 중복 | 같은 데이터를 두 위치에서 표시하지만 맥락이 다름 (섹션은 진단, 다음 행동은 액션). 후속 변경에서 통합 검토 가능 |
| 경고 배너가 사용자에게 "도구 못 믿을 것" 인상을 줄 수 있음 | 신뢰 저하 | 톤을 "검토 후 진행하면 됩니다" 식 협력적으로. amber 톤 (위험이 아닌 주의) |
| 카테고리당 1~3개 제한이 빡빡하면 중요한 행동 누락 | 추천 누락 | 카테고리 비어있어도 허용 — AI가 카테고리에 해당하는 게 없으면 빈 배열. 화면은 빈 그룹 숨김 |
| schema_version bump이 다운스트림 캐시 무효화 외에 깨짐 유발 | API 호환성 | 클라이언트는 SPA 단일 + 결과 캐시 없음 → 영향 거의 없음 |

## Out of Scope

- 추천 내용 자체의 정확도 검증 (시니어 동의 수준) — 별도 변경 `senior-grade-recommendations`
- 시그널 다양화 (함수 길이, 복잡도, 테스트 부재 등 추가 신호) — 별도 변경
- 프레임워크 관용구 인식 (Typer/FastAPI/Pydantic 등) — 별도 변경
- 후처리 sanity filter — 별도 변경
- vibe_insights 섹션과 vibe_coding 카테고리의 시각 중복 해소 — 별도 변경
- 카테고리 사용자 커스터마이징 (필터/숨기기) — 별도 변경

## Migration

- 캐시된 v4 PROMPT_VERSION 응답은 자동 폐기 (PROMPT_VERSION v5)
- 캐시된 v2 SCHEMA_VERSION briefing은 자동 폐기 (SCHEMA_VERSION 3)
- 클라이언트 코드 (TypeScript types)는 본 변경에서 함께 갱신, 별도 호환 단계 불필요
