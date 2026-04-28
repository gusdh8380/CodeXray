## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/ai/__init__.py` — 공개 API
- [x] 1.2 `src/codexray/ai/types.py` — `DimensionReview`, `FileReview`, `ReviewResult`, `Skipped`

## 2. 프롬프트 + 응답 파서

- [x] 2.1 `ai/prompt.py` — `build_prompt(rel_path: str, source: str) -> str`
- [x] 2.2 라인 번호 접두 + 한국어 4차원 평가 지시 + JSON 스키마 명시
- [x] 2.3 `parse_response(text: str, max_line: int) -> tuple[dict | None, str | None]`
- [x] 2.4 ```json ``` 블록 정규식 추출
- [x] 2.5 스키마 검증 — 4 차원 / 각 키 4개 / score 0-100 / evidence_lines 비어있지 않음·라인 범위 / comment·suggestion·limitations 비어있지 않음 / confidence enum
- [x] 2.6 단위 테스트 — 12 케이스 커버 (유효 / 누락 / 빈 evidence / 범위 초과 / 잘못된 confidence / 코드 블록 누락 / 비-JSON / 빈 limitations / 빈 comment 등)

## 3. 어댑터

- [x] 3.1 `ai/adapters.py` — `AIAdapter` Protocol, `AIAdapterError`
- [x] 3.2 `CodexCLIAdapter` — `codex exec --color never --skip-git-repo-check --ephemeral --output-last-message <tmp>` (실측 검증 후 확정)
- [x] 3.3 `ClaudeCLIAdapter` — `claude -p`
- [x] 3.4 `select_adapter(env)` — `CODEXRAY_AI_BACKEND` 처리 + `shutil.which` 우선순위 codex > claude
- [x] 3.5 단위 테스트 (mock subprocess) — 11 케이스 (자동/강제/미설치/잘못된 값 etc.)

## 4. 빌더

- [x] 4.1 `ai/build.py` — `build_review(root, top_n=5, adapter=None)`
- [x] 4.2 hotspots → category="hotspot" 정렬 → Top N
- [x] 4.3 source 읽기 → max_line 계산 → prompt 빌드 → adapter.review
- [x] 4.4 응답 파싱 → 유효하면 reviews에, 무효하면 skipped에
- [x] 4.5 reviews/skipped path 사전순 정렬
- [x] 4.6 단위 테스트 (페이크 어댑터) — 5 케이스 (정상 / invalid 모두 skip / N 캡 / hotspot 0개 / 정렬)

## 5. 직렬화

- [x] 5.1 `ai/serialize.py` — `to_json`
- [x] 5.2 단위 테스트는 build/cli 테스트로 커버

## 6. CLI 통합

- [x] 6.1 `cli.py`에 `review` 서브커맨드
- [x] 6.2 경로 검증 재사용
- [x] 6.3 `select_adapter()` 호출, stderr에 backend 안내, AIAdapterError 시 친절한 에러
- [x] 6.4 환경변수 `CODEXRAY_AI_TOP_N` 처리 + 잘못된 값 거부
- [x] 6.5 단위 테스트 — 5 케이스 (스키마 / missing path / no backend / N 오버라이드 / N 잘못)

## 7. 검증

- [x] 7.1 통합 테스트 — 페이크 어댑터로 mock 응답
- [x] 7.2 안전장치 회귀 — 빈 evidence_lines·범위 초과·잘못된 confidence·빈 limitations 모두 skipped
- [x] 7.3 환경변수 회귀 — `CODEXRAY_AI_BACKEND={codex,claude,auto}`, `CODEXRAY_AI_TOP_N`
- [x] 7.4 실측 — codex 백엔드, top 1 hotspot에 대해 실제 호출 → 유효 JSON + 한국어 권고 확인
- [x] 7.5 CodeXray 자기 자신 실측 — `cli.py` 리뷰, 공통 처리 헬퍼 추출 권고. `docs/validation/review-self.md`
- [x] 7.6 CivilSim 실측 — `GameManager.cs` 리뷰, 서비스 로케이터/도메인 파사드 분해 권고. `docs/validation/review-civilsim.md`
- [x] 7.7 `openspec validate add-ai-review` 통과
- [x] 7.8 `ruff check` + `pytest` 모두 통과 (224/224)
