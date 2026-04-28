## 1. AI Briefing 모듈 신규 작성 (src/codexray/web/ai_briefing.py)

- [x] 1.1 `AIBriefingResult` dataclass 정의 — `executive`, `architecture`, `quality_risk`, `next_actions: tuple[str, ...]`, `key_insight`, `backend`, `schema_version` 필드
- [x] 1.2 `build_evidence_bundle(root, briefing, metrics, quality, hotspots, inventory, graph) -> str` — 전체 분석 결과를 JSON 문자열로 묶는 함수
- [x] 1.3 `build_ai_briefing_prompt(evidence_json: str) -> str` — 한국어 종합 분석 요청 프롬프트 생성
- [x] 1.4 `parse_ai_briefing_response(text: str) -> AIBriefingResult | None` — AI 응답 파싱 (JSON 블록 추출 + 필드 검증)
- [x] 1.5 `cache_key(root, evidence_json, adapter_id) -> str` — sha256 기반 캐시 키
- [x] 1.6 `cache_get(key) -> AIBriefingResult | None` / `cache_put(key, result)` — `~/.cache/codexray/ai-briefing/` 디스크 캐시
- [x] 1.7 `build_ai_briefing(root, adapter) -> tuple[AIBriefingResult | None, str | None]` — 전체 분석기 실행 → 증거 번들 → AI 호출 → 파싱 → 결과 반환

## 2. Background Job 추가 (jobs.py)

- [x] 2.1 `AIBriefingJob` dataclass — `id`, `root`, `status`, `step`, `result`, `error` 필드
- [x] 2.2 `start_ai_briefing_job(root: Path) -> AIBriefingJob` — background thread 시작
- [x] 2.3 `get_ai_briefing_job(job_id: str) -> AIBriefingJob | None`
- [x] 2.4 `cancel_ai_briefing_job(job_id: str) -> AIBriefingJob | None`
- [x] 2.5 `_run_ai_briefing(job_id, root)` — 단계별 step 업데이트하며 실행 (Python 분석 → 증거 수집 → AI 해석)

## 3. Routes 변경 (routes.py)

- [x] 3.1 `POST /api/briefing` → `start_ai_briefing_job(root)` 시작 후 polling fragment 즉시 반환
- [x] 3.2 `GET /api/briefing/status/{job_id}` 엔드포인트 추가 — running/done/cancelled/failed 상태 분기
- [x] 3.3 done 상태: AI 결과 있으면 `render_ai_briefing_result()`, 없으면 `render_ai_briefing_fallback()` 반환

## 4. Render 함수 추가 (render.py)

- [x] 4.1 `render_ai_briefing_running(job: AIBriefingJob) -> str` — 단계 진행 메시지 + polling htmx 속성 포함
- [x] 4.2 `render_ai_briefing_result(result: AIBriefingResult) -> str` — executive / architecture / quality_risk / next_actions 섹션 HTML
- [x] 4.3 `render_ai_briefing_fallback(briefing: CodebaseBriefing, reason: str) -> str` — 기존 결정론적 Briefing + "AI 해석 없이 표시 중" 배너
- [x] 4.4 `render_ai_briefing_cancelled(job) -> str` / `render_ai_briefing_failed(job) -> str`

## 5. 검증

- [x] 5.1 `uv run pytest tests/ -x` 전체 통과 확인
- [x] 5.2 CivilSim 경로로 Briefing 실행 → 로딩 단계 메시지 확인
- [x] 5.3 AI 완료 후 결과 화면 — executive / architecture / quality_risk / next_actions 섹션 노출 확인
- [x] 5.4 AI 어댑터 없는 환경에서 폴백 배너 + 결정론적 Briefing 표시 확인
