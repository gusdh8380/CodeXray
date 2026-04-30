## Summary
전반적으로 변경 의도와 구현은 대부분 맞지만, `vibe_coding` 카테고리의 예외 처리에서 1개 correctness 결함을 찾았습니다. Parser는 의도대로 `vibe_coding`을 valid로 보존하지만, payload builder가 다시 `code`로 강등해서 최종 UI 분류가 틀어집니다.

## Findings
| # | severity | file:line | 제목 | finding | suggested fix |
|---|---|---|---|---|---|
| F1 | high | src/codexray/web/briefing_payload.py:272 | AI `vibe_coding` action이 최종 payload에서 `code`로 강등됨 | AI가 실수로 `category: "vibe_coding"`을 반환하는 경우 parser는 보존하지만, `_build_next_actions`가 `code`/`structural` 외 값을 모두 `code`로 바꿔 최종 UI에 코드 측면으로 표시됩니다. 이는 명시된 의도와 `test_parse_next_actions_vibe_coding_category_passes_through`의 보장 범위를 payload 단계에서 깨뜨립니다. | payload builder에서도 `vibe_coding`을 허용 카테고리로 유지하세요. 예: `cat = a.category if a.category in {"code", "structural", "vibe_coding"} else "code"` 후 동일한 per-category cap 적용. |

## Detailed Findings

### F1 (high) src/codexray/web/briefing_payload.py:272 — "AI `vibe_coding` action이 최종 payload에서 `code`로 강등됨"

```python
for a in structured:
    cat = a.category if a.category in {"code", "structural"} else "code"
```

`ai_briefing._parse_next_actions`는 `_ALLOWED_CATEGORIES = {"code", "structural", "vibe_coding"}`로 `vibe_coding`을 valid로 인정하고, 테스트도 “AI is told not to generate vibe_coding, but if it does, parser keeps the value as-is”를 검증합니다. 하지만 최종 payload 생성 단계에서 같은 action이 `code`로 바뀝니다.

재현 시나리오: AI 응답에 `{..., "category": "vibe_coding"}`이 포함되면 `parse_ai_briefing_response()` 결과는 `category == "vibe_coding"`입니다. 이후 `build_briefing_payload()`가 `_build_next_actions()`를 거치며 해당 항목을 `category == "code"`로 직렬화하고, 프론트엔드는 이를 “코드 측면” 그룹에 렌더링합니다. 이는 사용자가 제공한 “code로 강등하지 않고 그대로 통과” 의도와 어긋납니다.

---

## Triage Decisions (사용자 + Claude, 2026-04-30)

| F# | 결정 | 이유 |
|---|---|---|
| F1 | **적용 (옵션 B — parser도 vibe_coding 거부)** | design.md D2: vibe_coding은 system이 vibe_insights에서 합성하는 카테고리. AI는 code/structural만 책임. 의도와 코드를 정렬하려면 parser도 같은 정책. 프롬프트 설명("그대로 통과")은 잘못된 묘사였음. severity는 med 평가(분류 미스, 데이터 손실 아님). |

## Severity Recalibration

- F1: Codex high → 사용자/Claude med 합의. AI가 vibe_coding 생성하는 케이스 자체가 프롬프트 위반이라 발생률 낮고, 영향은 UX 분류 미스에 한정.

## Applied Commits

- (TBD — F1 fix commit 추가 예정)

## Notes

- Codex가 200+ 라인 변경에서 1개 finding은 적은 편. 재실행 1회 (anti-goal 살짝 풀어서) 예정 — 추가 발견 검증.
- 이번 결과 자체로도 의도 vs 구현 갭 1개 정확히 잡음 → advisory 가치 입증.