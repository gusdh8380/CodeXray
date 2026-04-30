## 1. axes.py 3축 재설계

- [x] 1.1 `src/codexray/vibe_insights/axes.py` 의 `environment / process / handoff` 3 함수 → `intent / verification / continuity` 로 함수 시그니처·이름 교체
- [x] 1.2 각 축의 신호 수집을 design.md Decision 1 의 *broadened 신호 풀* 대로 구현:
      `intent` = (a) AI 지속 지시 문서 1종 이상 (CLAUDE.md / AGENTS.md / .cursorrules / .github/copilot-instructions.md / .windsurf/* / .aider.conf.yml / .continue/* — 어느 것이든) + 충실도(≥500 chars + 헤더 ≥2), (b) 프로젝트 의도 문서 1종 이상 (README purpose 문단 / docs/intent.md / VISION.md / ABOUT.md / PROJECT.md / OVERVIEW.md / openspec/project.md), (c) 의도+비의도 명문화 (Not 섹션 / docs/adr/ / docs/decisions/ / CHANGELOG reasoning / openspec proposal Why)
- [x] 1.3 `verification` = (a) 손 검증 흔적 (docs/validation/ / screenshots/ / demo/ / 수동 테스트 체크리스트), (b) 자동 테스트 (tests/ / __tests__/ / *_test.py / *.test.ts 등 언어별 표준) + CI (.github/workflows/ / .gitlab-ci.yml / .circleci/ 등), (c) 재현 가능 실행 경로 (README 명령어 블록 / package.json scripts / pyproject scripts / Makefile / justfile / Dockerfile / docker-compose.yml / .env.sample)
- [x] 1.4 `continuity` = (a) 작게 이어가기 (작은 PR/commit 빈도 + saved plans: openspec tasks / PLANS.md / TODO.md / ROADMAP.md / .github/ISSUE_TEMPLATE), (b) 학습 반영 (docs/retro/ / docs/postmortem/ / docs/lessons/ / CHANGELOG 갱신 빈도 / 지시 문서 git log 갱신), (c) 핸드오프 문서 (HANDOFF.md / ONBOARDING.md / CONTRIBUTING.md)
- [x] 1.4a README purpose 문단 감지 휴리스틱 구현 — 첫 1-3 단락 안에 "what / purpose / why / 이 프로젝트는 / 이 도구는" 키워드 + 단락 길이 ≥ 200 chars
- [x] 1.5 점수 산정 결과를 4 단계 상태(`strong / moderate / weak / unknown`) + `signal_count` + `top_signals` 로 변환하는 헬퍼 추가
- [x] 1.6 임계값 비율 적용: `strong` ≥ 70% + 핵심 신호 충족, `moderate` ≥ 40%, `weak` ≥ 10%, `unknown` 신호 0
- [x] 1.7 가장 약한 축 선택 — `_STATE_RANK` 로 정렬 (briefing_payload.py)

## 2. 약한 process proxy 보조 정보로 분리

- [x] 2.1 axes.py 에서 feat/fix 비율, spec 커밋 시점 순서, hotspot 누적 속도, intent 문서 업데이트 빈도 — 모두 *상태 결정 로직에서 제거*
- [x] 2.2 별도 함수 `build_process_proxies()` 신설 — 위 정보를 보조 정보로 수집해 dict 로 반환
- [x] 2.3 vibe_insights builder 에서 `process_proxies` 필드를 결과에 분리해 포함

## 3. 사각지대(blind_spots) 명시

- [x] 3.1 axes.py 에 `BLIND_SPOTS` 상수 4 항목 + `get_blind_spots()` 헬퍼. builder.py 가 detected/not-detected 둘 다에서 `blind_spots` 필드 포함
- [x] 3.2 사각지대는 평가에 따라 동적으로 변하지 않고 *항상 고정 노출*. 결손 카운트나 점수 산정에는 합산하지 않음 (axes.py 에서 분리)

## 4. SCHEMA_VERSION + 직렬화 갱신

- [x] 4.1 `vibe_insights/builder.py` 의 직렬화 출력을 새 3 축 키 + `state` + `signal_count` + `top_signals` + `blind_spots` + `process_proxies` 로 갱신
- [x] 4.2 `web/briefing_payload.py` 의 vibe coding 섹션 빌더 갱신 — 새 axis name + state 사용. 9-룰 엔진은 Phase 2 에서.
- [x] 4.3 `web/briefing_payload.py:SCHEMA_VERSION` 3 → 4 bump. `web/ai_briefing.py:SCHEMA_VERSION` 은 PROMPT_VERSION 함께 Phase 2 에서 bump.
- [x] 4.4 결정론적 직렬화 통과 — 307 tests pass

## 5. ai_prompt 라벨 v7 갱신 (`ai_briefing.py` + 합성 함수들)

- [x] 5.1 `build_ai_briefing_prompt` 6 라벨 예시·규칙 교체 — `[지금 상황]` → `[이번 변경의 이유]`, `[끝나고 확인]` → `[성공 기준과 직접 확인 방법]`
- [x] 5.2 같은 함수의 ai_prompt 작성 규칙 — 새 라벨 두 개의 목적·가이드 반영 (이유=동기, 성공 기준=객관 완료 + 직접 확인)
- [x] 5.3 `_REQUIRED_PROMPT_LABELS` 새 라벨 셋으로 교체
- [x] 5.4 `_synthesize_deterministic_prompt` 폴백 템플릿 — v7 라벨로 재작성
- [x] 5.5 `briefing_payload.py` 의 합성 함수 3개 — v7 라벨로 재작성
- [x] 5.6 `vibe_insights/starter_guide.py` 3 항목 ai_prompt — v7 라벨로 재작성
- [x] 5.7 `PROMPT_VERSION` v6-persona-split → **v7-realign**, `SCHEMA_VERSION` 5 → **6**

## 6. 카드 수 동적 정책 + 9 룰 엔진

- [x] 6.1 `_VIBE_RULES` 상수 9 룰 박음 (axis_name, sub_cat_label, action_title)
- [x] 6.2 `_synthesize_vibe_coding_actions` 재작성 — 결손 sub-cat 매칭 → 룰 작업으로 카드 1개씩, 축당 최대 1
- [x] 6.3 가장 약한 축부터 정렬 (state rank → declaration order tiebreak: intent > verification > continuity)
- [x] 6.4 카드 cap = `_PER_CATEGORY_LIMIT` (3) 유지. 코드/구조 카테고리는 AI가 자체 처리. 전체 카드 cap 은 Phase 3 에서 추가 검토.
- [x] 6.5 0개 카드 분기는 7.x 그룹에서 처리

## 7. 침묵·칭찬·판단 보류 분기

- [x] 7.1 `_build_zero_action_state(vibe_insights)` 헬퍼 신설 — `praise / judgment_pending / silent` 분기
- [x] 7.2 `_build_praise_message` — 강한 축 1·2·3개 케이스별 메시지 + top_signals 인용
- [x] 7.3 판단 보류 메시지 — 모든 축 unknown 일 때 발동
- [x] 7.4 침묵 — 메시지 빈 문자열
- [x] 7.5 payload 에 `zero_action_state` 필드 추가 (next_actions 빈 경우에만 의미)

## 8. 프론트엔드 — 4단계 상태 표시

- [x] 8.1 `VibeInsightsSection.tsx` 의 `AxisCard` 재작성 — 점수 0-100 → 4 단계 상태 라벨 + 신호 개수 + 대표 근거
- [x] 8.2 상태별 색상 매핑 — `STATE_STYLES` (강함=초록 / 보통=황 / 약함=빨강 / 판단유보=회색) + 라벨 텍스트
- [x] 8.3 0-100 원시 점수는 payload `_raw_score` 에 보존하되 화면 미노출

## 9. 프론트엔드 — 카드 0–3개 동적 + zero-action 메시지

- [x] 9.1 `NextActionsSection.tsx` — `zeroActionState` prop 추가, 빈 리스트 분기에서 `ZeroActionView` 렌더
- [x] 9.2 `praise` 분기 — `CheckCircle2` 아이콘 + 초록 계열 박스 + 메시지 노출
- [x] 9.3 `judgment_pending` 분기 — `HelpCircle` 아이콘 + 회색 계열 박스
- [x] 9.4 `silent` 분기 — 보조 텍스트 한 줄

## 10. 프론트엔드 — blind spot 고정 블록

- [x] 10.1 신규 컴포넌트 `BlindSpotBlock.tsx`
- [x] 10.2 `payload.vibe_insights.blind_spots` 4 항목 자가 점검 체크리스트로 렌더
- [x] 10.3 위치: vibe coding 섹션 하단 (`VibeInsightsSection` 안에서)
- [x] 10.4 톤: "이 항목들은 코드만 봐서는 판단할 수 없습니다. 화면 상태와 무관하게 직접 자가 점검해 주세요"

## 11. 프론트엔드 — process proxies 보조 패널

- [x] 11.1 신규 컴포넌트 `ProcessProxiesPanel.tsx` (collapsable, 기본 접힘)
- [x] 11.2 헤더: `참고용 — 단독 판정 근거 아님` (백엔드 note 인용)
- [x] 11.3 vibe coding 섹션 안 별도 영역 (축 상태 카드와 분리)

## 12. 슬로건 노출 (선택)

- [x] 12.1 vibe coding 섹션 헤더 아래에 슬로건 한 줄 노출 (italic, "주인이 있는 프로젝트")
- [-] 12.2 hover/클릭 시 운영 정의 표시 — 철학 토글이 같은 역할 함, 중복 회피로 미구현

## 12b. 평가 철학 토글 (Decision 10)

- [x] 12b.1 신규 컴포넌트 `EvaluationPhilosophyToggle.tsx` (collapsable, 기본 접힘)
- [x] 12b.2 라벨: "이 도구가 바이브코딩을 어떻게 평가하나요?"
- [x] 12b.3 위치: vibe coding 섹션 최하단 (`VibeInsightsSection` 안)
- [x] 12b.4 콘텐츠 8 sub-section 모두 렌더 (사용자 검토 통과 콘텐츠)
- [x] 12b.5 콘텐츠는 컴포넌트 내부 정적 텍스트 (분석 결과 의존 X) — 별도 모듈 분리는 추후 정리 시
- [x] 12b.6 출처 인용 — Anthropic / OpenAI / Karpathy / Simon Willison / Kent Beck 등 한 줄씩
- [x] 12b.7 비개발자 청자 톤 유지 — 메트릭 용어 사용 안 함

## 13. 테스트 보강

- [ ] 13.1 `tests/test_vibe_insights.py` — 새 3 축 함수 단위 테스트 (각 축이 입력 흔적에 따라 적절한 상태를 반환)
- [ ] 13.2 `tests/test_vibe_insights.py` — `blind_spots` 가 항상 2 개 항목 포함 + 점수 산정에 미반영 검증
- [ ] 13.3 `tests/test_vibe_insights.py` — `process_proxies` 가 분리되어 보조 필드로 반환됨 검증
- [ ] 13.4 `tests/test_ai_briefing.py` — 새 v7 라벨 셋 (`[성공 기준과 직접 확인 방법]` 포함)으로 정상 prompt 보존 + 폴백 시나리오 갱신
- [ ] 13.5 `tests/test_ai_briefing.py` — `[끝나고 확인]` 같은 옛 라벨 결손 시 폴백 트리거 (backward-compat parser 동작)
- [ ] 13.6 `tests/` (briefing_payload 레벨) — 카드 수 0/1/2/3 각 시나리오 + zero_action_state 분기 (`praise / judgment_pending / silent`) 단위 테스트
- [ ] 13.7 starter_guide ai_prompt — v7 라벨 검증 테스트 갱신
- [ ] 13.8 `uv run pytest tests/ -q` 통과 확인

## 14. 자기 적용 검증 (편향 없는 평가 확인)

- [ ] 14.1 서버 재시작 후 CodeXray 자체 분석
- [ ] 14.2 3 축 상태 (`intent / verification / continuity`) 가 어떤 라벨로 분류되는지 확인 — 사용자 합의 받음 (CodeXray 자체는 모두 `strong` 또는 `intent / continuity` 가 `strong`, `verification` 이 `moderate` 정도가 자연스러움)
- [ ] 14.3 다음 행동 카드 수 — 자기 적용에서 0–3 중 어디로 정착하는지 측정
- [ ] 14.4 blind spot 블록 렌더링 확인 (4 항목 모두 노출)
- [ ] 14.5 ai_prompt 1 개를 실제 새 Claude/Codex 세션에 복사해서 의도대로 작동하는지 확인
- [ ] 14.6 결과를 `docs/validation/vibe-insights-realign-self.md` 에 기록

## 15. Non-ROBOCO 레포 검증 (편향 검증의 핵심)

- [ ] 15.1 *OpenSpec/ROBOCO 안 쓰는 메이저 OSS* 레포 1-2개 분석 — 후보: vite, fastapi, ruff, sveltekit 같은 일반 OSS
- [ ] 15.2 분석 결과 확인 — 잘 만들어진 레포가 모두 "약함" 으로 분류되지 않는지 (편향 없는지) 검증
- [ ] 15.3 결과를 `docs/validation/vibe-insights-realign-non-roboco.md` 에 기록
- [ ] 15.4 (선택) `/Users/jeonhyeono/Project/personal/CivilSim` (Unity C#) 도 분석 후 `docs/validation/vibe-insights-realign-civilsim.md` 에 기록

## 16. 변경 마무리

- [ ] 16.1 `openspec validate vibe-insights-realign --strict` 통과 확인
- [ ] 16.2 `cd frontend && npm run build` 통과 확인
- [ ] 16.3 자기 적용 결과 문서화 완료 후 `openspec archive vibe-insights-realign`
