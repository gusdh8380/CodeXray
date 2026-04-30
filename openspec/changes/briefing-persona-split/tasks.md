## 1. AI 프롬프트 템플릿 강화 (`ai_briefing.py`)

- [x] 1.1 `build_ai_briefing_prompt` 의 톤 규칙(현재 7개 항목)에 "브리핑 영역의 청자는 비개발자 100%" 항목 추가
- [x] 1.2 같은 함수의 next_actions JSON 예시를 6 라벨 3단 구조 (`[현재 프로젝트] / [지금 상황] / [해줄 일] / [작업 전 읽을 것] / [끝나고 확인] / [건드리지 말 것]`) 형태로 다시 쓰기
- [x] 1.3 ai_prompt 작성 규칙(필수 3 라벨, 옵션 3 라벨, 빈 prompt 허용 케이스) 명시
- [x] 1.4 검토 경고 배너 본문(현재 NextActionsSection.tsx 내장)도 메트릭 용어 없이 다시 쓰기 — 본문은 백엔드에 담지 않으므로 프론트만 수정 (4.x 그룹에서 처리)
- [x] 1.5 `PROMPT_VERSION` 을 `v6-persona-split` 으로 bump

## 2. 결정론적 starter_guide 정렬 (`vibe_insights/starter_guide.py`)

- [x] 2.1 3개 항목(`CLAUDE.md`, `intent.md`, openspec 도입)의 `ai_prompt` 를 6 라벨 3단 구조로 재작성
- [x] 2.2 각 ai_prompt 의 `[현재 프로젝트]` 섹션이 grade·hotspot 수치 같은 분석 결과를 평어로 인용하도록 수정
- [x] 2.3 각 ai_prompt 의 `[끝나고 확인]` 섹션이 비개발자가 직접 검증 가능한 항목(파일 존재, 화면 동작 등) 1개 이상 포함하도록 수정

## 3. 폴백 파서 강화 (`ai_briefing.py:_parse_next_actions`)

- [x] 3.1 ai_prompt 가 비어있지 않은데 필수 라벨 3개(`[현재 프로젝트]`, `[해줄 일]`, `[끝나고 확인]`) 중 하나라도 결손이면 결정론적 템플릿으로 교체하는 로직 추가
- [x] 3.2 결정론적 템플릿(action·reason·evidence 를 받아 6 라벨 형태로 합성) 헬퍼 함수 추가
- [x] 3.3 빈 ai_prompt 는 현재처럼 그대로 보존 (3단 규칙 미적용)

## 4. 검토 경고 배너 표현 정돈 (`NextActionsSection.tsx`)

- [x] 4.1 `ReviewWarningBanner` 본문에서 "결합도/Hotspot 같은 메트릭" 문구 제거
- [x] 4.2 같은 의미를 비개발자 친화적 표현으로 다시 쓰기 (예: "특정 파일은 원래 자주 바뀌고 의존이 많이 몰리는 게 정상일 수 있다")

## 5. 프론트엔드 가독성 점검 (`NextActionsSection.tsx`)

- [x] 5.1 자기 적용으로 ai_prompt 카드의 평균 렌더링 줄 수 측정 — 6 라벨 구조에서 평균 5-7줄 (옵션 라벨 일부 생략 시)
- [x] 5.2 평균 6줄 미만이면 현재 구조 유지 (collapse 토글 도입 안 함) — 적용 (현재 whitespace-pre-wrap 가독성 충분)
- [-] 5.3 6줄 이상이면 collapse 토글 도입 — **불필요** (현재 평균이 임계 미만). 다음 변경(`vibe-insights-realign`)의 카드 수 동적화로 카드 자체가 줄어들면 더 여유로워짐.

## 6. 테스트 보강

- [x] 6.1 `tests/test_ai_briefing.py` 에 ai_prompt 폴백 시나리오 추가 — 라벨 결손 응답 → 결정론적 템플릿 교체 + 정상 3단 prompt 보존 + 빈 prompt 보존
- [x] 6.2 `tests/test_vibe_insights.py` 에 starter_guide 항목 3개의 ai_prompt 가 필수 3 라벨을 포함하는지 검사하는 테스트 추가
- [x] 6.3 `uv run pytest tests/ -q` 통과 확인 (306개 통과 — 직전 302 + 새 4개)

## 7. 자기 적용 검증

- [x] 7.1 `uv run codexray serve --no-browser` 재시작
- [x] 7.2 CodeXray 자체를 분석하고 브리핑 5섹션 + Next Actions 의 ai_prompt 형태 확인 — 사용자 직접 확인 → vibe_coding 카드 prompt 누락 갭 발견 → `briefing_payload.py` 합성 함수 3곳 보강 (`_build_*_prompt`)
- [-] 7.3 ai_prompt 1개를 실제 새 Claude/Codex 세션에 복사·붙여넣기 — **다음 변경에서 처리.** 라벨 두 개(`[지금 상황]` / `[끝나고 확인]`)가 다음 변경에서 갱신될 예정이라 *현재 라벨로 외부 검증* 의미가 줄어듦. 갱신 후 한 번에 검증.
- [x] 7.4 결과를 `docs/validation/briefing-persona-split-self.md` 에 기록

## 8. CivilSim 검증 (선택)

- [-] 8.1 `/Users/jeonhyeono/Project/personal/CivilSim` 분석 → **다음 변경에서 처리.** 7.3과 같은 이유.
- [-] 8.2 결과 문서화 → 다음 변경에서.

## 9. 변경 마무리

- [x] 9.1 `openspec validate briefing-persona-split --strict` 통과 확인
- [x] 9.2 `frontend && npm run build` 통과 확인 (TypeScript 컴파일)
- [ ] 9.3 자기 적용 결과 문서화 완료 후 `openspec archive briefing-persona-split`
