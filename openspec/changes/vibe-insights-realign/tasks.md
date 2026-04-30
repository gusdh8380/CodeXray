## 1. axes.py 3축 재설계

- [ ] 1.1 `src/codexray/vibe_insights/axes.py` 의 `environment / process / handoff` 3 함수 → `intent / verification / continuity` 로 함수 시그니처·이름 교체
- [ ] 1.2 각 축의 신호 수집을 design.md Decision 1 의 *broadened 신호 풀* 대로 구현:
      `intent` = (a) AI 지속 지시 문서 1종 이상 (CLAUDE.md / AGENTS.md / .cursorrules / .github/copilot-instructions.md / .windsurf/* / .aider.conf.yml / .continue/* — 어느 것이든) + 충실도(≥500 chars + 헤더 ≥2), (b) 프로젝트 의도 문서 1종 이상 (README purpose 문단 / docs/intent.md / VISION.md / ABOUT.md / PROJECT.md / OVERVIEW.md / openspec/project.md), (c) 의도+비의도 명문화 (Not 섹션 / docs/adr/ / docs/decisions/ / CHANGELOG reasoning / openspec proposal Why)
- [ ] 1.3 `verification` = (a) 손 검증 흔적 (docs/validation/ / screenshots/ / demo/ / 수동 테스트 체크리스트), (b) 자동 테스트 (tests/ / __tests__/ / *_test.py / *.test.ts 등 언어별 표준) + CI (.github/workflows/ / .gitlab-ci.yml / .circleci/ 등), (c) 재현 가능 실행 경로 (README 명령어 블록 / package.json scripts / pyproject scripts / Makefile / justfile / Dockerfile / docker-compose.yml / .env.sample)
- [ ] 1.4 `continuity` = (a) 작게 이어가기 (작은 PR/commit 빈도 + saved plans: openspec tasks / PLANS.md / TODO.md / ROADMAP.md / .github/ISSUE_TEMPLATE), (b) 학습 반영 (docs/retro/ / docs/postmortem/ / docs/lessons/ / CHANGELOG 갱신 빈도 / 지시 문서 git log 갱신), (c) 핸드오프 문서 (HANDOFF.md / ONBOARDING.md / CONTRIBUTING.md)
- [ ] 1.4a README purpose 문단 감지 휴리스틱 구현 — 첫 1-3 단락 안에 "what / purpose / why / 이 프로젝트는 / 이 도구는" 키워드 + 단락 길이 ≥ 200 chars
- [ ] 1.5 점수 산정 결과를 4 단계 상태(`strong / moderate / weak / unknown`) + `signal_count` + `top_signals` 로 변환하는 헬퍼 추가
- [ ] 1.6 임계값 초안 적용: `strong` ≥ 4 + 핵심 신호 모두 충족, `moderate` ≥ 2, `weak` ≥ 1, `unknown` 데이터 부족
- [ ] 1.7 가장 약한 축 선택 — 동률 시 `intent > verification > continuity` 우선순위 적용

## 2. 약한 process proxy 보조 정보로 분리

- [ ] 2.1 axes.py 에서 feat/fix 비율, spec 커밋 시점 순서, hotspot 누적 속도, intent 문서 업데이트 빈도 — 모두 *상태 결정 로직에서 제거*
- [ ] 2.2 별도 함수 `build_process_proxies()` 신설 — 위 정보를 보조 정보로 수집해 별도 dataclass 로 반환
- [ ] 2.3 vibe_insights builder 에서 `process_proxies` 필드를 결과에 분리해 포함

## 3. 사각지대(blind_spots) 명시

- [ ] 3.1 vibe_insights builder 에서 `blind_spots` 필드 신규 — 다음 4 항목 고정:
      "사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가",
      "다음 행동의 우선순위를 사람이 정하고 있는가",
      "손으로 한 검증이 실제로 매번 굴러가는가",
      "외부 도구(Notion, Confluence, Slack, Linear 등)와 README 같은 문서의 질적 깊이 는 자동 판단 못 합니다"
- [ ] 3.2 사각지대는 평가에 따라 동적으로 변하지 않고 *항상 고정 노출*. 단, 결손 카운트나 점수 산정에는 합산하지 않음

## 4. SCHEMA_VERSION + 직렬화 갱신

- [ ] 4.1 `vibe_insights/serialize.py` 의 직렬화 형식을 새 3 축 키(`intent / verification / continuity`) + `state` + `signal_count` + `top_signals` + `blind_spots` + `process_proxies` 로 갱신
- [ ] 4.2 `web/briefing_payload.py` 의 vibe coding 섹션 빌더 갱신
- [ ] 4.3 `SCHEMA_VERSION 5` → **6** bump (`web/ai_briefing.py` + 다른 SCHEMA_VERSION 정의 위치 동기)
- [ ] 4.4 결정론적 직렬화 byte-identical 테스트 통과 확인

## 5. ai_prompt 라벨 v7 갱신 (`ai_briefing.py` + 합성 함수들)

- [ ] 5.1 `build_ai_briefing_prompt` 의 6 라벨 예시·규칙에서 `[지금 상황]` → `[이번 변경의 이유]`, `[끝나고 확인]` → `[성공 기준과 직접 확인 방법]` 로 교체
- [ ] 5.2 같은 함수의 ai_prompt 작성 규칙 본문 — 새 라벨 두 개의 *목적과 작성 가이드* 정확히 반영 (이유 = 동기 강조, 성공 기준 = 객관 완료 + 직접 확인)
- [ ] 5.3 `_REQUIRED_PROMPT_LABELS` 상수를 `("[현재 프로젝트]", "[해줄 일]", "[성공 기준과 직접 확인 방법]")` 로 교체
- [ ] 5.4 `_synthesize_deterministic_prompt` 폴백 템플릿 — 새 6 라벨 본문으로 다시 작성
- [ ] 5.5 `briefing_payload.py` 의 `_build_hotspot_review_prompt`, `_build_low_grade_prompt`, `_build_vibe_axis_weakness_prompt` — 새 라벨 6 개로 다시 작성
- [ ] 5.6 `vibe_insights/starter_guide.py` 의 3 항목 ai_prompt — 새 라벨 6 개로 다시 작성
- [ ] 5.7 `PROMPT_VERSION` v6-persona-split → **v7-realign** bump

## 6. 카드 수 동적 정책 (`briefing_payload.py:_build_next_actions` + `_synthesize_vibe_coding_actions`)

- [ ] 6.1 약점 → 카드 강제 매핑 로직 제거 (`weaknesses[:_PER_CATEGORY_LIMIT]` 식 제거)
- [ ] 6.2 레버리지 합성 헬퍼 — 결손 신호들의 *공통 root* 기반으로 카드를 합성하는 함수 추가. 같은 작업으로 둘 이상 신호 해결 가능하면 하나의 카드로
- [ ] 6.3 카드 수 정책: 가장 큰 root 1 개 → 카드 1, 독립 root 2 → 카드 2, 독립 고확신 root 3 → 카드 3, 고확신 root 0 → 카드 0
- [ ] 6.4 카테고리당 최대 3 개 제한(`_PER_CATEGORY_LIMIT`) 폐지 — 전체 0–3 한도만 유지
- [ ] 6.5 0개 카드 분기 — `praise / judgment_pending / silent` 셋 중 하나로 zero-action 상태 반환

## 7. 침묵·칭찬·판단 보류 분기

- [ ] 7.1 `_zero_action_state(insights)` 헬퍼 신설 — 입력: vibe_insights 결과 + axis states + signals. 출력: `praise (with one-line message)` 또는 `judgment_pending (with reason)` 또는 `silent`
- [ ] 7.2 칭찬 메시지 템플릿 — 강한 긍정 신호 ≥ 1 일 때 그 신호를 인용한 한 줄 (예: "validation 디렉토리에 N 개 문서가 매 변경마다 갱신되고 있습니다 — 이 습관 유지하세요")
- [ ] 7.3 판단 보류 메시지 — 결손이 모두 사각지대일 때 "코드만 봐선 추가 진단 어려움 — 사용자 대화·시연이 필요합니다"
- [ ] 7.4 침묵 — 메시지 없음 (드문 케이스, 빈도 측정 위해 로그 한 줄 남김)
- [ ] 7.5 payload 에 `zero_action_state` 필드 추가 (위 셋 중 하나, next_actions 가 빈 경우에만 의미 있음)

## 8. 프론트엔드 — 4단계 상태 표시

- [ ] 8.1 `frontend/src/components/micro/VibeCodingTab.tsx` (또는 `BriefingScreen.tsx` 의 vibe coding 섹션) — 점수 0-100 표시 컴포넌트 → 4 단계 상태 라벨 + 신호 개수 + 대표 근거 컴포넌트로 교체
- [ ] 8.2 상태별 색상·아이콘 매핑 (강함=초록, 보통=황, 약함=빨강, 판단유보=회색) — 색맹 보조용 라벨 텍스트도 함께
- [ ] 8.3 0-100 점수는 디버그 토글에서만 노출 (또는 완전 비노출. 구현 단계 판단)

## 9. 프론트엔드 — 카드 0–3개 동적 + zero-action 메시지

- [ ] 9.1 `NextActionsSection.tsx` — `next_actions` 빈 리스트 + `zero_action_state` 분기 처리 추가
- [ ] 9.2 `praise` 분기 — "유지할 습관" 한 줄 카드 (배경 톤 다르게, 초록 계열)
- [ ] 9.3 `judgment_pending` 분기 — "코드만 봐선 추가 진단 어려움" 메시지 카드 (배경 톤 회색)
- [ ] 9.4 `silent` 분기 — 영역 자체 숨김 또는 보조 텍스트만

## 10. 프론트엔드 — blind spot 고정 블록

- [ ] 10.1 신규 컴포넌트 `BlindSpotBlock.tsx` 추가
- [ ] 10.2 `payload.blind_spots` 의 항목들을 자가 점검 체크리스트 톤으로 렌더
- [ ] 10.3 위치: `NextActionsSection` 직후 또는 vibe coding 섹션 하단 (구현 시 가독성 보고 결정)
- [ ] 10.4 톤: "이 셋은 코드만 봐서는 판단 못 합니다. 화면 상태와 무관하게 자가 점검해 주세요" 같은 자가 책임 환기 표현

## 11. 프론트엔드 — process proxies 보조 패널

- [ ] 11.1 신규 컴포넌트 `ProcessProxiesPanel.tsx` 추가 (collapsable 토글 또는 작은 글씨 보조)
- [ ] 11.2 헤더에 "참고용 — 단독 판정 근거 아님" 명시
- [ ] 11.3 vibe coding 섹션 안에서 *축 상태 라벨 옆이 아니라* 별도 영역에 배치

## 12. 슬로건 노출 (선택)

- [ ] 12.1 vibe coding 섹션 헤더 또는 intent_alignment 옆에 슬로건 한 줄 ("주인이 있는 프로젝트") 노출
- [ ] 12.2 hover/클릭 시 운영 정의 (외부화된 의도 / 독립 검증 / 인간 최종 판단) 표시 — 구현 단계 판단

## 12b. 평가 철학 토글 (Decision 10)

- [ ] 12b.1 신규 컴포넌트 `EvaluationPhilosophyToggle.tsx` 추가 — collapsable, 기본 접힘
- [ ] 12b.2 라벨: "이 도구가 바이브코딩을 어떻게 평가하나요?"
- [ ] 12b.3 위치: vibe coding 섹션 최하단 (blind spot 블록 아래)
- [ ] 12b.4 콘텐츠 8 sub-section 렌더 (사용자 검토 후 확정된 텍스트):
      슬로건 → 운영 정의 → 8 신호 → 3축 매핑 → 4 단계 상태 의미 →
      카드 수 정책 → 사각지대 → 출처
- [ ] 12b.5 콘텐츠는 *정적 텍스트* (분석 결과 의존 X) — 별도 모듈 (`philosophy_content.ts` 또는 markdown 파일) 로 분리
- [ ] 12b.6 출처 인용은 영어 원문 그대로 표시 OK (한국어 번역 병기는 선택)
- [ ] 12b.7 비개발자 청자 톤 유지 (메트릭 용어 직접 사용 금지, codebase-briefing 톤 규칙 준수)

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
