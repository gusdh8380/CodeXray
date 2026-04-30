# Codex Review Prompt — categorized-next-actions

당신은 시니어 Python/TypeScript 리뷰어다. 아래 변경(commit `5e09d56`)을 검토하라.

## 컨텍스트 (한 줄)

CodeXray의 "다음 행동" 추천을 3 카테고리(code / structural / vibe_coding)로 분류하고 검토 경고 배너를 추가하는 변경.

## 검토 우선순위 (이 순서로만)

1. **Correctness** — 실제 동작이 의도와 어긋나는 부분, 엣지 케이스 누락, 타입/None 처리 빠진 곳, 캐시 무효화/schema bump 인정 여부, 동시성/입력 경계 결함, 직렬화 결정론성 깨지는 곳
2. **Maintainability** — 향후 변경 비용을 명백히 키우는 패턴 (단, "더 분리하라" 같은 추측은 금지). 강력한 근거가 있는 항목만.
3. **Deadweight** — 미사용 import, 죽은 분기, 명백한 중복 코드, 더 이상 호출되지 않는 함수

## 검토에서 반드시 제외할 것

- "이 함수를 더 작게 분리해라" — **강력한 결함 근거 없으면 노이즈**. 이 프로젝트는 이미 "엔트리포인트 false positive" 문제를 인지하고 있음
- 스타일 / 네이밍 미세 조정 (ruff / biome 통과 시 OK)
- "주석 추가해라" — 의도가 자명한 코드는 주석 불필요
- 테스트 커버리지 일반론 — "더 많은 테스트" 같은 추상 추천 금지. 누락된 **구체적 엣지 케이스**가 있으면 그것만 지적
- 변경 범위 밖(이번 commit 외) 코드에 대한 의견 — 이번 변경이 직접 만든 결함만
- **추천 품질 자체** — "AI가 더 좋은 추천 하게 만들어라" 같은 의견 금지. 이번 변경의 명시적 out-of-scope (별도 후속 변경 `senior-grade-recommendations`로 위임됨)

## 알아둬야 할 의도

- `vibe_coding` 카테고리는 AI가 생성하지 않고 백엔드가 `vibe_insights` 데이터에서 합성. AI 프롬프트에는 "vibe_coding 생성 금지" 명시. AI가 그래도 생성하면 백엔드가 `code` 카테고리로 강등하지 않고 그대로 통과 (parser는 vibe_coding을 valid로 인정). 이는 의도된 동작 — payload 빌더가 별도로 구현하는 합성과 충돌하지 않음.
- 카테고리당 최대 3개, 합계 최대 9개. 빈 카테고리(0개)도 허용.
- `SCHEMA_VERSION` 2→3, `PROMPT_VERSION` v4→v5 — 둘 다 캐시 자동 무효화 위한 의도된 bump.
- 경고 배너는 dismissable 아님 (의도). 사용자가 매번 보게 하는 게 핵심.

## 출력 형식

다음 마크다운 테이블 + 상세 섹션:

```markdown
## Summary
(한 단락 — 전반적 인상, 발견 개수, 가장 중요한 한두 가지)

## Findings
| # | severity | file:line | 제목 | finding | suggested fix |
|---|---|---|---|---|---|
| F1 | high | src/path.py:42 | ... | ... | ... |
| F2 | med  | ... | ... | ... | ... |

## Detailed Findings

### F1 (high) src/.../foo.py:42 — "..."
(코드 인용 + 왜 결함인지 한 단락)

### F2 (med) ...
...
```

severity 기준:
- **high** — 반드시 수정해야 하는 실제 결함 (버그 / 보안 / 데이터 손상). 구체적 재현 시나리오 필수.
- **med** — 검토 후 결정할 가치 있는 maintainability 이슈. 강력한 근거 있을 때만.
- **low** — 선택. deadweight나 사소한 정합성 이슈만.

finding이 0개여도 OK. 그 경우 "No issues found" 명시 + 왜 그렇게 판단했는지 한 단락 (어떤 측면을 봤는지).

검토 시작.
