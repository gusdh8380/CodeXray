## Summary
Reviewed the current state after the F1 fix, focusing on parser/cache invalidation, payload synthesis, frontend grouping, and build/test behavior. I found one additional high-severity regression: the F1 fix renamed the allowed-category constant inconsistently, so AI responses with object-form `next_actions` now crash during parsing.

## Findings
| # | severity | file:line | 제목 | finding | suggested fix |
|---|---|---|---|---|---|
| F1 | high | `src/codexray/web/ai_briefing.py:33` | allowed category 상수 오타로 AI briefing 파싱 실패 | `_AI_AI_ALLOWED_CATEGORIES`로 정의했지만 `_parse_next_actions`와 `cache_get`은 `_AI_ALLOWED_CATEGORIES`를 참조합니다. AI가 정상 JSON object action을 반환하면 `NameError`가 발생해 briefing job이 실패합니다. 재현: `uv run pytest tests/test_ai_briefing.py -q`에서 4개 실패. | 상수 정의를 `_AI_ALLOWED_CATEGORIES = {"code", "structural"}`로 고치거나 참조부를 정의명에 맞추세요. `cache_get` 경로도 같이 커버하는 테스트를 추가하면 좋습니다. |

## Detailed Findings

### F1 (high) `src/codexray/web/ai_briefing.py:33` — allowed category 상수 오타로 AI briefing 파싱 실패

```python
# AI 응답에 vibe_coding 이 들어와도 code 로 강등 — design.md D2 결정 일관 적용.
_AI_AI_ALLOWED_CATEGORIES = {"code", "structural"}
...
if category not in _AI_ALLOWED_CATEGORIES:
    category = "code"
```

F1의 정책 수정 자체는 맞지만, 정의된 이름과 참조 이름이 다릅니다. 이 때문에 object-form `next_actions`를 파싱하는 정상 경로가 즉시 `NameError`로 깨집니다. 실제 재현 결과 `tests/test_ai_briefing.py`의 dict action 케이스 4개가 모두 실패했고, string-form action만 우연히 이 분기를 타지 않아 통과했습니다.

`cache_get`도 같은 미정의 이름을 사용하므로, v5 캐시가 존재하는 경우 캐시 복원 중에도 동일하게 터질 수 있습니다.  
확인한 보조 게이트: `uv run pytest tests/test_briefing.py -q`는 통과, `cd frontend && npm run build`도 통과했습니다.

---

## Triage Decisions (2026-04-30)

| F# | 결정 | 이유 |
|---|---|---|
| F1 (v2) | **즉시 적용** — `_AI_AI_ALLOWED_CATEGORIES` → `_AI_ALLOWED_CATEGORIES` (오타 수정) | 정의명을 참조명에 맞춤. dict-form action 파싱이 `NameError`로 깨지던 결함을 즉시 봉합. **Codex severity high — 사용자/Claude high 합의** (실제 결함, 캐시 hit 경로도 NameError) |

## Root Cause Notes

- F1 (v1) fix 적용 시 Edit#1 에서 `_ALLOWED_CATEGORIES` → `_AI_ALLOWED_CATEGORIES` 정의 변경
- Edit#2 (replace_all) 에서 `_ALLOWED_CATEGORIES` → `_AI_ALLOWED_CATEGORIES` 일괄 치환을 한 번 더 함
- replace_all 이 substring 매칭이라 line 33의 `_AI_ALLOWED_CATEGORIES` 안에 포함된 `_ALLOWED_CATEGORIES` 가 한 번 더 prefix 받아 `_AI_AI_ALLOWED_CATEGORIES` 로 변형됨
- Lines 333, 400 은 원본이 `_ALLOWED_CATEGORIES` 였으므로 정상적으로 `_AI_ALLOWED_CATEGORIES` 로 치환됨
- 결과: 정의 != 참조 → `NameError`
- 검증 누락: 직후 pytest bg 작업의 notification 만 신뢰하고 실제 출력 (`4 failed`)을 읽지 않음 → 파일에 깨진 상태 그대로 commit

## Process Lessons

- **bg task notification ≠ test 통과**. 무조건 출력 파일 읽기.
- **replace_all 은 substring 매칭** — 첫 번째 치환이 만들어낸 문자열에 원본 패턴이 포함되면 위험. 안전한 방법은 (a) 더 긴 unique context 로 첫 edit 하고 두 번째 edit 도 unique context 로 하기, 또는 (b) replace_all 후 즉시 grep 으로 검증.
- 이번 사례가 **정확히 article 이 말한 "writer 자기 리뷰의 사각지대"** — 제가 변경 직후 같은 코드를 봐도 typo 못 보고 넘어감. Codex가 외부 시선으로 즉시 캐치.

## Applied Commits

- (TBD — F1(v2) typo fix)