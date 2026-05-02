## 1. 백엔드 — vibe_insights 모듈

- [x] 1.1 `src/codexray/vibe_insights/builder.py` — `build_vibe_insights` 의 `detected=False` 분기를 *None 반환* 으로 변경. dict + starter_guide + blind_spots 반환 부분 삭제
- [x] 1.2 `src/codexray/vibe_insights/__init__.py` — `build_starter_guide` export 제거
- [x] 1.3 `src/codexray/vibe_insights/starter_guide.py` *파일 삭제*
- [x] 1.4 axes.py 의 `get_blind_spots()` 호출 위치 점검 — detected=True 경로 안에서만 호출되는지 확인 (이미 그래야 정상)

## 2. 백엔드 — briefing payload + AI prompt

- [x] 2.1 `src/codexray/web/briefing_payload.py` — `vibe_insights` 변수가 None 일 때 페이로드의 `vibe_insights` 키를 None 으로 설정 (또는 키 자체 부재)
- [x] 2.2 `briefing_payload.py` — `_synthesize_vibe_coding_actions` 가 None 입력 시 빈 리스트 반환하도록 가드. starter_guide 참조 코드 제거
- [x] 2.3 `briefing_payload.py` — SCHEMA_VERSION 6 → 7 bump
- [x] 2.4 `src/codexray/web/ai_briefing.py` — vibe coding 비감지 시 prompt 컨텍스트에서 vibe insights 부분 제외. 시작 가이드 prompt 템플릿 코드 제거. PROMPT_VERSION 검토 (필요 시 v7-realign → v8-detection-rebalance)
- [x] 2.5 캐시 키 검증 — SCHEMA_VERSION/PROMPT_VERSION bump 로 자기 적용 시 캐시 자동 무효화 동작 확인

## 3. 백엔드 — 테스트 갱신

- [x] 3.1 `tests/vibe_insights/` 의 starter_guide 관련 테스트 *전체 제거*
- [x] 3.2 `tests/vibe_insights/test_builder.py` (또는 동등 위치) 에 *비감지 시 None 반환* 테스트 추가
- [x] 3.3 `tests/web/test_briefing_payload.py` 에 *비감지 시 vibe_insights 필드 None* + *vibe_coding 카테고리 카드 0개* 테스트 추가
- [x] 3.4 `tests/scripts/test_validate_external_repos.py` 의 fixture 가 비감지 케이스를 다루는지 확인 — 필요 시 갱신
- [x] 3.5 `uv run pytest tests/ -q` 통과 (예상: 309 → 약간 감소 후 신규 추가로 비슷한 수준)

## 4. 프론트엔드 — 타입 + 조건부 렌더링

- [x] 4.1 `frontend/src/lib/api.ts` — `BriefingPayload.vibe_insights` 를 `VibeInsights | null` 로 옵셔널화. `StarterGuideItem` 타입 *제거*. `VibeInsights` 타입에서 `starter_guide` 필드 제거
- [x] 4.2 `frontend/src/components/briefing/BriefingScreen.tsx` — `<VibeInsightsSection />` 호출 위에 `{data.vibe_insights && ...}` 조건부 렌더링
- [x] 4.3 `frontend/src/components/briefing/VibeInsightsSection.tsx` — `data.detected` 분기 / `<StarterGuide />` / `<StarterGuideCard />` / `<CopyPromptBox />` (시작 가이드용) 함수 *전체 삭제*. 컴포넌트는 항상 `detected: true` 가정
- [x] 4.4 사용되지 않는 import (`useState` from CopyPromptBox 등) 정리

## 5. 프론트엔드 — 빌드 + 시각 확인

- [x] 5.1 `cd frontend && npm run build` 통과
- [x] 5.2 dev server 띄워 자기 적용 (CodeXray 자체 분석) 시 vibe insights 섹션 정상 노출 확인
- [x] 5.3 dev server 에서 fastapi 분석 시 vibe insights 섹션 *사라짐* 확인 + 다른 섹션 (What/How Built/Current State/Next Actions/미시 분석) 정상 노출 — API 직접 검증으로 vibe_insights=None 확인

## 6. 검증 문서

- [x] 6.1 `docs/validation/vibe-detection-rebalance-self.md` — 자기 적용 결과 (동료 페르소나 시뮬레이션). 화면 변화 없어야 함을 명시
- [x] 6.2 `docs/validation/vibe-detection-rebalance-fastapi.md` — fastapi 적용 결과 (본인 페르소나 시뮬레이션). vibe insights 섹션 사라짐 + 일반 분석 정상 노출 명시. 스크린샷 또는 텍스트로 화면 모양 캡처
- [x] 6.3 design.md Open Question 1 (비감지 시 한 줄 안내 노출 여부) 사용자 직접 결정 결과 기록 — 본 검증 단계 추천: 안내 안 보여줌 (옵션 A). fastapi.md 에 명시

## 7. 검증 + 문서화

- [x] 7.1 `uv run pytest tests/ -q` 전체 통과
- [x] 7.2 `cd frontend && npm run build` 전체 통과
- [x] 7.3 `openspec validate vibe-detection-rebalance --strict` 통과
- [x] 7.4 `uv run ruff check src/ tests/ scripts/` 통과
- [x] 7.5 CLAUDE.md "Current Sprint" 갱신 — 본 변경의 결과 + 후속 변경 후보 정리
- [x] 7.6 git commit (atomic 단위, 단일 PR 가정)

## 8. Archive

- [x] 8.1 `openspec archive vibe-detection-rebalance` (실패 시 incomplete 태스크 점검 후 재시도)
- [x] 8.2 archive 후 main spec 동기화 확인 — vibe-coding-insights / codebase-briefing / react-frontend 모두 갱신됐는지
- [x] 8.3 후속 변경 후보 (예: README 외부 vibe coding 자료 링크 추가, vibe-signal-pool-expand) 를 CLAUDE.md 에 정리
