## Why

직전 변경(`briefing-persona-split`, 2026-04-30 archive)이 페르소나 분리 + ai_prompt 6 라벨 골격을 도입한 직후, 사용자가 두 가지 본질 문제를 제기했고 GPT Deep Research(2026-05-01)가 확인·강화했다:

1. **3축 점수가 하드코딩** — environment / process / handoff 가 특정 파일·패턴 존재 여부에 의존. 우리가 인지하지 못한 더 좋은 환경 구축 방식이 있어도 약점으로 표시되어 사용자가 "내 방식이 틀렸나" 오해. 측정 가능한 흔적과 측정 불가능한 차원이 한 점수 안에 섞여 있어 *흔적 기반 가짜 정확성* 위험.
2. **카드 3개 강제 매핑** — 약점이 적은 프로젝트도 합성 함수가 카드 3개를 채움. 약점 0개 시 칭찬·침묵 정의 없음. 결과적으로 "이거라도 더 해라" 가짜 노이즈.

리서치는 한 줄 정의를 *운영 가능한 3구조*로 재작성을 권고: **외부화된 의도 / 독립 검증 / 인간 최종 판단**. 이 셋이 그대로 새 3축이 되어야 하고, 점수는 0–100 → 4단계 상태(강함/보통/약함/판단유보)로, 카드 수는 강제 3개 → 레버리지 기준 동적 0–3개로 가야 한다. 또한 *측정 못 하는 차원*("이 도구가 못 본 것")을 화면에 상시 노출해 정직성을 확보한다.

## What Changes

- **3축 재설계**: `environment / process / handoff` → `intent / verification / continuity` (의도 / 검증 / 이어받기). 각 축의 측정 신호 명세 갱신.
- **점수 표시 변경 (BREAKING — payload 시각 표현)**: 0–100 숫자 점수 노출 → **4단계 상태(`strong / moderate / weak / unknown`) + 근거 신호 개수 + 대표 근거 2-3개**. 원시 점수는 디버그/실험 용도로만 보존(payload 비노출 또는 별도 필드).
- **8 운영 정의 명문화**: 흔적 기반 6개(의도 글, 의도+비의도 먼저, 손 검증, 재현 가능 실행 경로, 학습 반영, 작게 이어가기) + 대화·관찰 필요 2개(설명 가능, 사람이 다음 행동 결정). 후자는 점수 산정에서 제외하고 *blind spot* 으로 별도 표기.
- **카드 생성 정책 변경**: 가장 약한 축에서 강제 3개 → **레버리지 기준 + 동적 0–3개, 기본값 1개**. 0개도 정식 상태(고확신 액션 없음 = 정직).
- **침묵 vs 칭찬 분리**: 액션 0개 + 강한 긍정 신호 1개 이상 → "유지할 습관 한 줄" 한 줄만. 액션 0개 + 사각지대만 남음 → "판단 보류: 대화 필요" 표시.
- **blind spot 상시 노출**: Briefing 영역 하단에 "이 도구가 못 본 것" 고정 블록. What/Why/Next 설명 가능 / 손 검증 실제 사용자 / 다음 행동 결정자 — 셋 최소.
- **약한 process proxy 강등**: feat/fix 비율, spec 커밋 시점 등은 *단독 판정 근거에서 제외*. 보조 정보 패널로만 노출(있으면 좋음 정보).
- **ai_prompt 6 라벨 두 개 갱신** (BREAKING — PROMPT_VERSION bump):
  - `[지금 상황]` → `[이번 변경의 이유]` (상태 서술 → 동기 강조)
  - `[끝나고 확인]` → `[성공 기준과 직접 확인 방법]` (검증 순서 → 완료 기준 + 검증)
- **Intent 정렬**: `docs/intent.md` 의 운영 정의(2026-05-01 추가) 와 vibe-coding-insights 스펙을 동기화. 슬로건("주인이 있는 프로젝트")은 사용자 노출용 그대로, 운영 정의는 스펙 기준으로.

## Capabilities

### New Capabilities
(없음 — 기존 capability 재구성)

### Modified Capabilities

- `vibe-coding-insights`: 3축 재설계, 8 운영 정의, 점수 4단계 상태, 카드 정책, blind spot, 약한 proxy 강등 — 본 변경의 본체.
- `codebase-briefing`: ai_prompt 6 라벨 두 개 갱신, 카드 수 동적 정책, 상태 표시 갱신, blind spot 노출 시나리오.
- `web-ui`: UI 차원의 상태 표시 / 카드 0–3개 동적 / blind spot 고정 블록 시나리오 추가.

## Impact

- **코드**:
  - `src/codexray/vibe_insights/axes.py` — 3축 정의·점수 산정 로직 재설계 (가장 큰 변경)
  - `src/codexray/vibe_insights/builder.py`, `serialize.py` — 3축 키·표시 변경에 따라 일관성 확보
  - `src/codexray/web/briefing_payload.py` — 카드 합성 정책 (레버리지·동적 0–3, 침묵·칭찬·blind spot 분리)
  - `src/codexray/web/ai_briefing.py` — ai_prompt 라벨 갱신, PROMPT_VERSION v6 → v7-realign, parser 폴백 라벨 셋 업데이트
  - `src/codexray/vibe_insights/starter_guide.py` — 새 라벨로 재작성 (3 항목)
  - `src/codexray/web/briefing_payload.py` 의 3개 합성 prompt 함수 — 새 라벨로 재작성
  - 프론트엔드: `VibeCodingTab.tsx`(또는 동등) — 4단계 상태 표시, blind spot 블록, 카드 0개 칭찬 패턴

- **버전**: `PROMPT_VERSION` v6-persona-split → v7-realign. `SCHEMA_VERSION 5` → **6** (blind spot 필드 + 4단계 상태 필드 추가, payload JSON 형태 변경).

- **캐시**: `~/.cache/codexray/ai-briefing/` v6 키 자동 무효화.

- **테스트**: axes.py 테스트 큰 폭 갱신, briefing_payload 카드 정책 테스트 신규, ai_prompt 폴백 라벨 셋 갱신, starter_guide 라벨 검증 갱신.

- **검증 자료**: `docs/validation/vibe-insights-realign-self.md`, 선택적으로 CivilSim.

- **외부 호환성**: payload JSON 일부 키 변경 (axis name 변경, 점수 표현 변경). 직전 변경 archive 후 1일 만의 변경이라 외부 소비자 영향 없음 (자기 적용 + CivilSim 만 소비).

- **문서**: `docs/intent.md` 의 운영 정의는 직전에 이미 갱신됨. 본 변경은 그 운영 정의를 스펙·코드까지 끌어내림.
