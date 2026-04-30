# Codex Review Prompt v2 — categorized-next-actions (re-review)

당신은 시니어 Python/TypeScript 리뷰어다. 동일한 변경(commit `5e09d56`)을 **두 번째로** 검토하라. 이전 회차에서 1개 finding(`vibe_coding` 강등 일관성)을 잡아 이미 수정됨. 이번에는 **첫 회차에서 놓쳤을 만한 이슈를 더 적극적으로 찾아라**.

## 검토 우선순위

1. **Correctness** — 엣지 케이스 누락, None/empty/타입 문제, 캐시 무효화 정합성, 직렬화 결정론성, 동시성, 입력 경계
2. **Maintainability** — 향후 변경 비용을 키우는 패턴. 강한 응집도 위반 / 명확한 SRP 위반이면 분리 제안 OK (단, 구체적 결함을 짚으면서). 추상적 "더 모듈화" 는 여전히 노이즈
3. **Deadweight / consistency** — 미사용 import, 죽은 분기, 중복 코드, 명명 불일치, 죽은 동작 분기
4. **Frontend specific** — React 상태/이펙트 정합성, 접근성 (ARIA / role), key 안정성, 라이트/다크 토큰 일관성
5. **Backend specific** — 캐시 키 + schema_version 정합성, dataclass slots 위반, 한국어 텍스트 escape, 직렬화 byte-stability

## 이번엔 적극 검토할 것 (첫 회 anti-goal에서 풀어줌)

- 응집도가 명백히 깨진 함수가 있다면 분리 제안 OK (구체적 함수명 + 무엇이 깨졌는지 한 줄로 명시)
- 누락된 구체적 엣지 케이스 (예: "axes 가 빈 배열인 경우" 같은 case 시나리오)
- 프롬프트 텍스트의 ambiguity — AI가 잘못 해석할 수 있는 룰
- 캐시 schema/prompt version 의 cross-impact — 둘 다 bump 했는데 다운스트림 invalidation 로직이 정확한지

## 여전히 제외

- 변경 범위 밖(이번 commit 외) 코드
- 스타일 / 네이밍 미세 (linter pass면 OK)
- "주석 추가해라" — 의도가 자명하면 불필요
- 추천 품질 자체 (out-of-scope, 별도 변경 `senior-grade-recommendations`)
- 첫 회차에서 이미 잡힌 F1 (vibe_coding 강등) 은 fix 진행됨 — 같은 항목 재제기 금지

## 알아둬야 할 사실

- F1 fix: parser 의 `_AI_ALLOWED_CATEGORIES = {"code", "structural"}` 로 축소. AI 의 vibe_coding 응답은 code 로 강등됨. payload 동작과 정렬됨.
- vibe_coding 카테고리는 백엔드의 `_synthesize_vibe_coding_actions` 가 vibe_insights 데이터에서 합성.
- SCHEMA_VERSION 2→3 (briefing payload), AI cache SCHEMA_VERSION 4→5 — 둘은 다른 스킴.
- PROMPT_VERSION v4→v5.

## 출력 형식

```markdown
## Summary
(한 단락)

## Findings
| # | severity | file:line | 제목 | finding | suggested fix |
|---|---|---|---|---|---|

## Detailed Findings
### F1 (severity) path:line — title
(코드 인용 + 분석)
```

severity 기준 동일:
- **high** — 실제 결함 (재현 시나리오 필수)
- **med** — 검토할 가치 있는 maintainability
- **low** — 선택 / 사소한 정합성

finding 0개여도 OK. "no additional issues" 라고 답하고 어떤 측면을 추가로 확인했는지 한 단락.

검토 시작.
