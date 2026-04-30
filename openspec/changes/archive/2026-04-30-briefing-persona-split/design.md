## Context

직전 변경(`categorized-next-actions`, archive 2026-04-30)에서 다음 행동을 3 카테고리(코드/구조/바이브코딩)로 분류하고 각 항목에 `ai_prompt` 필드를 추가했다. 그러나 페르소나 우선순위가 명시되지 않아 `ai_prompt` 형태가 "한 문단 명령" 수준으로 머물렀고, 비개발자가 다음 AI 세션에 그대로 들고 가서 쓰기에는 컨텍스트가 결손돼 있다.

`docs/intent.md` 페르소나 우선순위 갱신(2026-04-30, 직전)으로 다음이 못 박혔다:

- 1순위: 비개발자 바이브코더
- 위(브리핑) = 비개발자 영역, 아래(상세 분석 토글) = 개발자 영역
- 디자인 결정 충돌 시 비개발자가 이긴다

이번 변경은 그 결정을 코드와 스펙까지 내려보내는 첫 변경이다.

현재 상태:
- `src/codexray/web/ai_briefing.py:243` `build_ai_briefing_prompt` — JSON 응답 스키마 + `ai_prompt` 예시("src/foo.py를 두 부분으로 나누세요. ...")가 한 문장 수준
- `src/codexray/vibe_insights/starter_guide.py` — vibe_coding 카테고리 항목이 한 문단 prompt
- `PROMPT_VERSION = "v5-categorized-actions"`, `SCHEMA_VERSION = 5`

## Goals / Non-Goals

**Goals:**
- 브리핑 영역(상단)을 비개발자 청자 100%로 못 박는다 — 메트릭 용어 차단 규칙이 스펙에 명시된다.
- Next Actions의 `ai_prompt` 필드가 "현재 프로젝트 컨텍스트 / 작업 단계 / 끝나고 확인할 검증 체크리스트" 3단 구조를 갖는다. 비개발자가 새 AI 세션(컨텍스트 0)에 그대로 복사해도 쓸 수 있어야 한다.
- 위/아래 영역의 페르소나 분리가 `web-ui` 스펙에 명문화된다.
- 검토 경고 배너의 표현이 비개발자 친화적으로 정돈된다.

**Non-Goals:**
- 상세 분석 토글(미시 탭 9개)의 톤·구조 변경 — 정의상 개발자 영역, 손대지 않음.
- AI 어댑터 자체 변경(codex/claude CLI 추상화) — 프롬프트 텍스트만 바꿈.
- 새 카테고리 도입 또는 카테고리 삭제 — 직전 변경에서 확정된 3종 유지.
- "AI 브리핑 생략" 옵션 도입 — 시니어 사용자 비용 최적화는 별도 변경에서.
- 결정론적 데이터 스키마 변경 — `SCHEMA_VERSION` 유지.

## Decisions

### Decision 1: ai_prompt 3단 구조의 섹션 헤더 형식

채택: 한국어 헤더를 텍스트 본문에 그대로 박는다.
```
[현재 프로젝트] {레포가 뭐 하는지 한두 줄}
[지금 상황] {분석에서 발견된 구체 문제 — evidence 인용}
[해줄 일] {원래 action을 실행 가능한 단계로 풀어쓰기}
[작업 전 읽을 것] {관련 파일/문서 경로 — 있으면}
[끝나고 확인] {비개발자가 사용자 시점에서 확인할 항목 + 회귀 체크}
[건드리지 말 것] {스코프 제약 — 있으면}
```

대안 1: JSON 객체 (`{"context": ..., "task": ..., "verify": ...}`) — `SCHEMA_VERSION` bump 필요, 프론트 렌더링·복사 UX 복잡해짐. 반려.

대안 2: Markdown headers (`## 현재 프로젝트`) — Claude/Codex CLI에 붙여넣을 때 모델이 헤더로 해석할 수 있음. `[...]` 대괄호 라벨이 더 안전.

대안 3: 자유 형식, AI에게 톤만 지시 — 일관성 보장 안 됨. 결정론적 starter_guide와 AI 결과의 톤이 갈리는 결과를 직전 변경에서 이미 봤음. 반려.

### Decision 2: 3단 구조 규칙의 거주 위치 (스펙)

채택: `codebase-briefing` 스펙에 "Next action AI 프롬프트 3단 구조" 요구사항을 신설하여 *briefing payload에 들어가는 모든 `ai_prompt`*에 적용한다(소스가 AI든 starter_guide든). `vibe-coding-insights` 스펙에는 행동 항목 구조에 `ai_prompt` 필드를 추가하고 3단 규칙은 codebase-briefing을 참조한다.

대안: 두 스펙에 규칙을 중복 명시 — drift 위험. 반려.

### Decision 3: PROMPT_VERSION bump, SCHEMA_VERSION 유지

채택: `PROMPT_VERSION` v5-categorized-actions → v6-persona-split. `SCHEMA_VERSION = 5` 유지.

근거: JSON 키 셋 불변(`action, reason, evidence, ai_prompt, category`). 문자열 *내용*만 길어지므로 데이터 스키마는 그대로다. 캐시 키에 `PROMPT_VERSION`이 포함되므로 자동 무효화 — 별도 마이그레이션 없음.

### Decision 4: 빈 ai_prompt 허용 유지

채택: 기존 fallback (AI 응답에 ai_prompt 누락 시 빈 문자열) 동작 유지. 3단 구조 규칙은 *비어있지 않은* `ai_prompt`에만 적용.

근거: 현재 `_parse_next_actions` 동작과 호환. 빈 prompt면 프론트 카드는 ai_prompt 영역을 숨긴다(이미 구현됨, `NextActionsSection.tsx:163`).

### Decision 5: starter_guide.py도 같은 3단 구조로 통일

채택: `vibe_insights/starter_guide.py`의 3개 항목(`CLAUDE.md` 작성 / `intent.md` / openspec 도입)을 같은 6 라벨 형태로 다시 작성한다.

근거: 사용자가 코드/구조/바이브코딩 카테고리를 한 화면에서 보는데 톤이 갈리면 학습 비용. 결정론적이라 PROMPT_VERSION과 무관.

### Decision 6: 검토 경고 배너 표현 정돈

채택: 현재 문구("AI가 자동 생성한 추천이라 그대로 적용하면 부적절할 수 있습니다. 특히 결합도/Hotspot 같은 메트릭은 ...")에서 "결합도/Hotspot" 같은 메트릭 용어를 비개발자 친화 표현으로 바꾼다(예: "특정 파일은 원래 자주 바뀌고 의존이 많이 몰리는 게 정상일 수 있으니 ..."). 메시지 본질은 유지.

근거: Not 항목 "브리핑 영역에서 메트릭 용어 도입 안 함"과 정렬.

### Decision 7: 프론트 카드 collapse 여부는 구현 단계 판단

채택: 디자인 차원에서는 "ai_prompt가 길어진다 → 가독성 검토"만 명시. 실제 collapse 컴포넌트 도입 여부는 구현 시 직접 보고 결정.

근거: 6 라벨이 항상 다 채워지진 않으므로(예: 작업 전 읽을 것·건드리지 말 것은 옵션) 평균 길이 측정이 먼저. 미리 토글 도입하면 과설계 위험.

## Risks / Trade-offs

- **[리스크] AI 응답 토큰 증가로 응답 시간/비용 상승** → mitigation: AI 호출 후 응답 길이 로그 1회 측정. 평균 토큰이 직전 대비 1.5배 미만이면 수용. 1.5배 이상이면 작업 단계의 "단계 풀어쓰기"를 "최대 3 sub-steps"로 제한하는 보강안을 별도 변경으로.
- **[리스크] 카드 길이 증가로 비개발자도 안 읽음** → mitigation: 자기 적용 검증(`docs/validation/briefing-persona-split-self.md`)에서 실제 렌더링 길이 측정 + 실제 사용 시도. 너무 길면 collapse 토글 도입.
- **[리스크] AI가 3단 형식을 자주 깨고 자유 형식으로 회귀** → mitigation: parser에서 6 라벨 중 최소 3개([현재 프로젝트], [해줄 일], [끝나고 확인]) 검출 안 되면 fallback ai_prompt를 결정론적 템플릿으로 강제 교체. tasks.md에 적시.
- **[리스크] 시니어 사용자가 "잔소리네" 느껴 매번 상세 토글 직행** → mitigation: 이번 변경 범위 밖. Intent 결정상 수용 가능한 트레이드오프. 사용 패턴 누적 후 별도 변경에서 "AI 브리핑 끄기" 옵션 검토.
- **[트레이드오프] 결정론적 starter_guide 항목 3개도 다시 쓰는 작업이 추가됨** → 일관성 가치가 작업량을 정당화. 톤 갈리는 게 더 큰 비용.
- **[리스크] 캐시 무효화 1회 비용** → 모든 분석이 한 번 AI를 다시 부른다. 자기 적용 외에는 영향 없음(개인 머신).

## Migration Plan

1. PROMPT_VERSION bump → 캐시 자동 무효화. 별도 cache clear 불필요.
2. 기존 캐시 디렉토리(`~/.cache/codexray/ai-briefing/`)의 v5 키 파일은 그대로 유지(검색 시 무시됨). 사용자가 원하면 수동 삭제 가능.
3. 롤백 전략: PROMPT_VERSION을 v5로 되돌리고 `build_ai_briefing_prompt` 변경을 revert. SCHEMA_VERSION 유지이므로 데이터 마이그레이션 없음.

## Open Questions

(없음 — 의사결정은 위 7건에 모두 반영. 구현 중 새로 발견되는 ambiguity는 tasks.md에 동적으로 반영.)
