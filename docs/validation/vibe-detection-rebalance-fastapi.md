# vibe-detection-rebalance — fastapi 적용 검증

**날짜**: 2026-05-02
**대상**: `~/Project/external/fastapi` (본인 페르소나 시뮬레이션)
**페르소나**: 일반 OSS 분석가 — 비-AI 프로젝트에서 vibe insights 섹션 사라져야 함

## 결정론 페이로드 검증

```
SCHEMA_VERSION = 5
fastapi: vibe_insights=None (비감지)
  next_actions categories: {'structural', 'code'} (count=2)
```

확인된 동작:
- `build_briefing_payload(fastapi_path, ai=None)` 호출 시 `payload['vibe_insights'] is None`
- next_actions 에 vibe_coding 카테고리 카드 *0개* — code/structural 만
- 기존 일반 분석 (정체 / 구조 / 현재 상태 / 다음 행동) 정상 노출

직전 archive `non-roboco-validation` 과의 비교:
- 이전: fastapi 분석 시 `vibe_insights = {"detected": False, "starter_guide": [...3개 카드...]}` 반환. 사용자에게 "CLAUDE.md 작성하세요" 같은 권유 강제 노출.
- 현재: `vibe_insights = None`. starter_guide 도 응답에 없음. *사용자에게 부적절한 권유 차단됨*.

## 본인 페르소나 화면 시뮬레이션

브라우저 직접 확인 (별도 사용자 검증):
- 화면이 4 섹션으로 줄어듦: 정체(what) / 구조(how built) / 현재 상태(current state) / 다음 행동(next actions)
- 바이브코딩 인사이트 섹션 *완전 비노출* — placeholder 없음, "비감지" 메시지 없음, 시작 가이드 영역 없음
- 미시 분석 9 탭 + 그래프 4 정상 노출 (vibe coding 진단과 무관)
- *깔끔한 일반 OSS 분석 도구* 로 변신 확인

## 결정 5 결과 — design.md Open Question 1

design.md 의 Open Question 1 ("비감지 시 *AI 협업 흔적이 없어 vibe coding 진단 건너뜀* 한 줄 안내") — 사용자가 fastapi 화면을 직접 본 후 결정.

본 검증 단계 추천: **안내 안 보여줌 (옵션 A)** — fastapi 화면이 *그 자체로 자연스러운 일반 분석 도구* 로 보여 사용자 의문이 들지 않음. "왜 vibe insights 가 없지?" 라는 질문이 생기는 사용자는 어차피 도구 README 또는 도움말에서 detection 게이트를 확인하면 됨.

→ 본 변경에서는 안내 추가 안 함. 사용자가 직접 화면 보고 다른 결정 시 후속 변경에서 추가.

## 회귀 차단 점검

- pytest 312 통과 — 비감지 시 None 반환 신규 테스트 + 기존 테스트 모두 정상
- ruff 신규 위반 0건
- frontend build 통과
- self.md 의 자기 적용 결과 — vibe insights 섹션 정상 노출 (회귀 없음)

## 결론

본 변경의 핵심 가치 — *"비감지 프로젝트에서 vibe insights 섹션이 사라지고 일반 분석 도구로 변신"* — 검증됨. 두 페르소나 (동료 / 본인) 모두 의도된 화면을 받음. archive 가능.
