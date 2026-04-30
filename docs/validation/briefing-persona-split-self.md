# briefing-persona-split — 자기 적용 검증

**날짜**: 2026-05-01
**대상**: CodeXray 자체 분석

## 검증 범위

이 변경은 (1) 페르소나 분리 (위/아래), (2) ai_prompt 6 라벨 3단 구조 도입, (3) 폴백 파서 강화, (4) 검토 경고 배너 톤 정돈 — 네 가지를 동시에 적용했다.

## 결과

### 자동 검증

- `uv run pytest tests/ -q` → **306 passed** (직전 302 + 새 4)
- `npm run build` → 372KB JS / 35KB CSS 정상 생성
- `openspec validate briefing-persona-split --strict` → 통과
- `uv run ruff check` → starter_guide.py / tests / briefing_payload.py 깨끗. ai_briefing.py 17개 E501 (모두 prompt 템플릿 f-string 내부 한국어 라인, 직전 baseline 12 + 신규 5, 같은 패턴 — 프로젝트 관행상 수용)

### 사용자 직접 검증

서버 재시작 후 사용자가 브라우저에서 분석을 돌렸고 다음 갭이 발견됨:

> "지금 바이브코딩 측면 부분에는 프롬프트가 없는데 의도된건가요?"

**원인**: `briefing_payload.py:_synthesize_vibe_coding_actions` 와 fallback hotspot/grade 합성 사이트 3곳이 `ai_prompt: ""` 를 하드코딩하고 있었음. 3 라벨 폴백 룰은 *비어있지 않은* 텍스트에만 적용되므로 빈 문자열은 그대로 통과했고, 결과적으로 bicep_coding 카드에 prompt 영역이 사라짐.

**수정**: 3개 합성 사이트(`_build_hotspot_review_prompt`, `_build_low_grade_prompt`, `_build_vibe_axis_weakness_prompt`)에서 6 라벨 결정론적 prompt 를 생성하도록 변경. 사용자가 재확인 → 통과.

## 한계 — 다음 변경에서 다룸

이 검증은 *코드/구현* 계 검증이며, *프롬프트 의미·내용* 의 평가는 아니다. 사용자가 후속 대화에서 더 본질적인 문제 두 가지를 제기:

1. **3축 점수가 하드코딩** — environment/process/handoff 가 특정 파일·패턴 존재 여부에 의존. 우리가 모르는 더 좋은 환경 구축 방식이 있어도 잡히지 않음.
2. **카드 3개 강제 매핑** — 약점이 적은 프로젝트도 억지로 카드 3개를 채움. 칭찬·침묵 시점이 없음.

이 두 문제는 GPT Deep Research 결과와 함께 다음 변경 `vibe-insights-realign` 에서 처리한다 (axes.py 재설계, 점수 → 4 단계 상태, 카드 수 동적 0-3 등). 따라서 본 변경 archive 후 즉시 다음 변경 시작.

## 결론

- 페르소나 분리 (위/아래), 6 라벨 ai_prompt 골격, 폴백 파서, 결정론적 합성 prompt 까지 모두 정상 작동.
- ai_prompt 의 라벨 두 개와 axes 재설계는 다음 변경에서 갱신 예정 — 본 변경은 그 기반으로서 archive 가능.
- 본 변경의 핵심 가치(페르소나 정렬·프롬프트 골격 도입)는 다음 변경의 전제이므로 *유지된다*.
