## Why

지금까지 만든 분석은 모두 정량 신호다 — 사용자에게 "F입니다"는 알려주지만 *왜* F인지·*어디 라인*이 문제인지·*어떻게* 고치라는지는 답하지 못한다. `intent.md` MVP #3 "정성 평가(AI)"는 점수 + 근거 코드 인용 + 개선 제안 4차원(가독성·설계·유지보수성·위험)을 요구한다. `constraints.md`의 Top risk("AI 평가 부정확 → 잘못된 의사결정")를 막기 위해 — opt-in, 근거 라인 인용 필수, 신뢰도/한계 명시, 사용자 거절·재평가 가능 — 안전장치를 명세에 박는다. 첫 단추는 hotspot Top N 파일에 한정, 어댑터 패턴(codex / claude CLI 셸아웃)으로 모델 락인 회피.

## What Changes

- 새 CLI 진입점: `codexray review <path>` — hotspot Top N 파일에 대해 AI 정성 평가, JSON 출력
- 어댑터 패턴: `CodexCLIAdapter`(`codex exec` 셸아웃) + `ClaudeCLIAdapter`(`claude -p` 셸아웃)
- 자동 감지 우선순위: codex → claude → "no AI backend available" 에러
- 환경변수 `CODEXRAY_AI_BACKEND ∈ {auto, codex, claude}` 강제 (default `auto`)
- 환경변수 `CODEXRAY_AI_TOP_N` (default 5) — 검토할 hotspot 파일 수
- 출력 JSON 스키마 v1 (신규 capability `ai-review`):
  ```json
  {
    "schema_version": 1,
    "backend": "codex",
    "files_reviewed": 5,
    "skipped": [{"path": "...", "reason": "..."}],
    "reviews": [
      {
        "path": "Assets/Scripts/Core/GameManager.cs",
        "dimensions": {
          "readability":     {"score": 60, "evidence_lines": [42,156], "comment": "...", "suggestion": "..."},
          "design":          {"score": 50, "evidence_lines": [203], "comment": "...", "suggestion": "..."},
          "maintainability": {"score": 55, "evidence_lines": [89,124], "comment": "...", "suggestion": "..."},
          "risk":            {"score": 65, "evidence_lines": [203], "comment": "...", "suggestion": "..."}
        },
        "confidence": "medium",
        "limitations": "테스트 파일·호출자 컨텍스트 미참조"
      }
    ]
  }
  ```
- AI 안전장치 (constraints.md):
  - **근거 라인 필수** — 각 차원의 `evidence_lines`가 비어있으면 그 차원은 invalid로 표기, `skipped`에 reason과 함께 등록
  - **신뢰도 표기** — `confidence ∈ {low, medium, high}`, default low (불확실 시 보수적)
  - **한계 표기** — `limitations` 비어있으면 invalid
  - **opt-in** — `codexray report`는 AI 결과 자동 포함 X. 별도 명령 또는 `--with-review path/to/review.json`로 명시적
- 다른 명령은 변경 없음

## Capabilities

### New Capabilities
- `ai-review`: 코드베이스 hotspot Top N 파일에 대해 AI 정성 평가(가독성·설계·유지보수성·위험 4차원 + 근거 라인 + 개선 제안)를 어댑터(codex/claude CLI)로 호출해 JSON으로 노출하는 능력. 후속 변경(report 통합, 대시보드)이 동일 JSON을 입력으로 받는다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/ai/` 서브패키지
  - `ai/types.py` — `DimensionReview`, `FileReview`, `ReviewResult`, `Skipped`
  - `ai/prompt.py` — 프롬프트 템플릿 + 응답 파싱·검증
  - `ai/adapters.py` — `CodexCLIAdapter`, `ClaudeCLIAdapter`, `select_adapter()`
  - `ai/build.py` — `build_review(root, top_n) -> ReviewResult`
  - `ai/serialize.py`, `ai/__init__.py`
- 신규 의존성 없음 (subprocess + json 표준 라이브러리)
- CLI에 `review` 서브커맨드 추가
- 검증:
  - 단위 테스트: subprocess mock으로 어댑터·파서·검증 로직
  - 통합 테스트: 환경변수로 `CODEXRAY_AI_BACKEND=auto`일 때 어댑터 자동 선택 시뮬레이션
  - 실측: opt-in (`CODEXRAY_TEST_REAL_AI=1`이고 backend 설치돼야)
- 5초 예산은 이 명령에 적용하지 않음 — AI 호출은 모델 응답 시간에 의존. 60s/파일 × 5 파일 = 5분 timeout 내에서 통과
