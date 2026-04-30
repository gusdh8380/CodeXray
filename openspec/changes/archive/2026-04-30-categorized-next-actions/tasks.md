## 1. AI 프롬프트 + 데이터 모델

- [x] 1.1 `AINextAction` dataclass 에 `category: str` 필드 추가 (default `"code"`)
- [x] 1.2 AI 프롬프트 텍스트에 카테고리 룰 추가 — "next_actions 의 각 항목은 category 필드를 포함하고 값은 'code' 또는 'structural'. vibe_coding 은 시스템이 따로 채우니 생성 금지"
- [x] 1.3 프롬프트의 JSON 예시도 `category` 필드 반영
- [x] 1.4 `_parse_next_actions` 가 누락된 category 또는 허용되지 않는 값을 `code` 로 강제 (codex review F1 후속 — vibe_coding 도 거부, design.md D2 정렬)
- [x] 1.5 `PROMPT_VERSION` v4 → v5 (`"v5-categorized-actions"`)

## 2. vibe_coding 카테고리 합성

- [x] 2.1 `_build_next_actions` 가 `briefing.vibe_insights.next_actions` 또는 `starter_guide` 에서 항목을 가져와 `category="vibe_coding"` 으로 변환
- [x] 2.2 변환 시 필드 매핑 — vibe_insights 의 `{action, reason, ai_prompt}` 에 evidence가 없으면 합성 ("바이브코딩 신호 미감지 — 첫 걸음 추천")
- [x] 2.3 starter_guide 만 있는 경우(미감지 레포)도 동일하게 vibe_coding 카테고리에 합성
- [x] 2.4 카테고리 항목 수 제한 — 카테고리당 최대 3개, 합쳐서 최대 9개

## 3. payload + schema 변경

- [x] 3.1 `briefing_payload._build_next_actions` 가 평면 리스트 반환 (각 항목에 `category` 필드 포함)
- [x] 3.2 `SCHEMA_VERSION` 2 → 3
- [x] 3.3 직렬화 어서션 갱신 — schema_version=3, next_actions 항목에 category 필드 존재

## 4. 프론트엔드 — 카테고리 그룹 + 경고 배너

- [x] 4.1 `frontend/src/lib/api.ts` `NextAction` 타입에 `category: "code" | "structural" | "vibe_coding"` 추가 + `NextActionCategory` union
- [x] 4.2 `NextActionsSection.tsx` 가 `groupByCategory` 로 3 그룹 렌더링
- [x] 4.3 빈 그룹은 화면에 표시 안 함
- [x] 4.4 그룹 순서 고정: 코드 → 구조 → 바이브코딩
- [x] 4.5 그룹 헤더 한국어 라벨 + 작은 보조 설명 + 아이콘 (Code2 / Boxes / Sprout)
- [x] 4.6 섹션 상단에 amber 경고 배너 컴포넌트 (AlertTriangle, dismissable 아님, 라이트/다크 모두 가독성)

## 5. 테스트

- [x] 5.1 `tests/test_ai_briefing.py` — `_parse_next_actions` 가 누락된 category 를 `code` 로 fallback
- [x] 5.2 `tests/test_ai_briefing.py` — 허용되지 않는 category(`"foo"`)도 `code` 로 fallback (vibe_coding 도 동일하게 거부)
- [x] 5.3 `tests/test_briefing.py` — payload 의 `schema_version == 3`, next_actions 모든 항목에 category 필드 존재
- [x] 5.4 `tests/test_briefing.py` — vibe_coding 카테고리 항목이 vibe_insights 데이터에서 합성됨
- [x] 5.5 카테고리당 최대 3개 어서션
- [x] 5.6 frontend `npm run build` 통과 (372KB JS / 115KB gzip)

## 6. 검증

- [x] 6.1 `uv run pytest tests/ -q` 전체 통과 (302 tests, 신규 5개 포함)
- [x] 6.2 `cd frontend && npm run build` 성공
- [x] 6.3 CodeXray 자체 분석 시 다음 행동이 3 카테고리로 분리되어 표시 (서버 재시작 후 확인)
- [x] 6.4 경고 배너 라이트/다크 양쪽에서 가독성 (amber 토큰 검증)
- [x] 6.5 캐시된 v4/schema_version=2 응답이 자동 무효화되어 v5/schema_version=3 으로 재생성 (PROMPT_VERSION/SCHEMA_VERSION bump 메커니즘 자체로 자동)
- [x] 6.6 AI 미사용(폴백) 케이스에서도 vibe_coding 카테고리는 채워짐 (vibe_insights 데이터로)

## 7. 변경 archive

- [x] 7.1 본 변경 archive
- [x] 7.2 main spec sync — codebase-briefing, react-frontend 갱신

## 8. Codex review (이번 변경에서 추가된 advisory 사이클)

- [x] 8.1 codex review #1 (strict prompt) — F1 (vibe_coding 강등 일관성) 발견, option B 적용 (commit 4add8bc)
- [x] 8.2 codex review #2 (loose prompt) — F1(v2) typo `_AI_AI_ALLOWED_CATEGORIES` 발견, 즉시 수정 (commit dda899a)
- [x] 8.3 review files 영구 보관 — `docs/reviews/2026-04-30-categorized-next-actions.md` + `-v2.md` + `prompts/`
- [x] 8.4 lessons learned 저장 — `~/.claude/projects/.../memory/feedback_bg_task_verification.md`, `feedback_replace_all_substring_pitfall.md`
