## Context

기존 분석(inventory/graph/metrics/entrypoints/quality/hotspots/report)이 안정 상태. 이번 변경은 모델 위에 정성 평가를 얹는 첫 사이클. 결정론적 정량 분석과 비결정적 AI 분석을 명확히 분리(별도 명령, 별도 capability) 한다. 1차에서 어댑터 추상화로 모델 락인 회피, 안전장치(근거 라인·신뢰도·한계)를 스키마에 강제.

## Goals / Non-Goals

**Goals:**
- hotspot Top N 파일에 대해 4차원 AI 평가 + 근거 라인 + 개선 제안
- 어댑터로 codex/claude 둘 다 지원, 자동 감지
- 안전장치 강제 — invalid 평가는 skipped로 격리
- mock subprocess로 단위 테스트 결정론 확보
- opt-in (사용자가 `codexray review` 명시)

**Non-Goals:**
- 직접 SDK 호출(Anthropic, OpenAI) — 후속에서 옵션 어댑터로 추가
- 함수 단위 평가 — 1차는 파일 단위
- 멀티 모델 비교 — 후속
- 토큰·비용 트래킹 — 후속
- 스트리밍 출력 — 1차는 batch
- report 자동 통합 — 별도 후속(`report --with-review review.json`)
- 다국어 프롬프트(영어 vs 한국어) — 1차는 한국어 prompt + 한국어 출력 요구

## Decisions

### Decision 1: 어댑터 인터페이스 — 단일 메서드 `review(prompt) -> str`
```python
class AIAdapter(Protocol):
    name: str
    def review(self, prompt: str, timeout: int = 60) -> str: ...
```
- 입력: 완성된 프롬프트 문자열
- 출력: AI 응답 raw 문자열 (JSON 추출은 호출 측 책임)
- 예외: subprocess 실패·timeout은 `AIAdapterError` 던짐

### Decision 2: codex CLI 셸아웃
- 명령 가설: `codex exec --quiet --json "<prompt>"` (정확한 flag는 codex CLI 0.125 docs 확인 필요. 1차는 `subprocess.run(["codex", "exec"], input=prompt, ...)` 형태로 stdin 전달)
- stdout이 응답 본문이라고 가정. 만약 codex가 metadata 헤더를 섞으면 후속에서 파싱 보강.

### Decision 3: claude CLI 셸아웃
- 명령: `claude -p "<prompt>"` (Claude Code의 비대화 모드)
- stdout = 응답 본문. 색상·마크다운 metadata 섞일 수 있음 → JSON 추출 시 정규식으로 ```json ... ``` 블록 우선 파싱.

### Decision 4: 자동 감지 — `select_adapter()`
- 우선순위 (default `auto`): codex > claude
- `which codex` 성공 → CodexCLIAdapter 반환
- 아니면 `which claude` 성공 → ClaudeCLIAdapter 반환
- 둘 다 없으면 `AIAdapterError("no AI backend available — install codex or claude CLI")`
- `CODEXRAY_AI_BACKEND=codex` 강제 시 codex만 시도, 미설치면 즉시 에러
- `CODEXRAY_AI_BACKEND=claude` 강제 시 claude만 시도

### Decision 5: 프롬프트 — 한국어, 결정론적 구조 강제
한 파일당 1개 프롬프트:
```
당신은 코드 리뷰어입니다. 아래 파일을 읽고 4차원으로 평가하십시오: 가독성, 설계, 유지보수성, 위험.

규칙:
- 각 차원에 0-100 점수, 근거가 되는 라인 번호 list(>=1개), 1-2문장 코멘트, 1-2문장 개선 제안.
- evidence_lines가 비면 그 차원은 invalid.
- confidence는 "low"/"medium"/"high" 중 하나. 파일이 짧거나 컨텍스트 부족하면 low.
- limitations는 보지 못한 부분(예: 호출자, 테스트 부재)을 1-2문장으로.
- 출력은 ```json ... ``` 코드 블록으로 감싼 단일 JSON. 다른 텍스트 금지.

JSON 스키마:
{
  "dimensions": {
    "readability":     {"score": int, "evidence_lines": [int], "comment": str, "suggestion": str},
    "design":          {"score": int, "evidence_lines": [int], "comment": str, "suggestion": str},
    "maintainability": {"score": int, "evidence_lines": [int], "comment": str, "suggestion": str},
    "risk":            {"score": int, "evidence_lines": [int], "comment": str, "suggestion": str}
  },
  "confidence": "low" | "medium" | "high",
  "limitations": str
}

파일: {relative_path}
```
{numbered_source}
```
```
- numbered_source: 각 라인 앞에 `{line_number}: ` 접두 (모델이 evidence_lines를 정확히 짚도록)

### Decision 6: 응답 파싱·검증
- ```json ... ``` 블록 정규식 추출
- `json.loads()` 후 스키마 검증:
  - 4 차원 모두 존재 + 각 키 4개 (`score`, `evidence_lines`, `comment`, `suggestion`)
  - score는 int, 0-100 범위
  - evidence_lines는 비어있지 않은 int list
  - comment·suggestion·limitations는 비어있지 않은 string
  - confidence는 enum 3개 중 하나
- 검증 실패 → `Skipped(path, reason)` 등록, 파일 review에서 제외

### Decision 7: hotspot Top N — `build_hotspots`에서 가져오기
- `hotspots.build_hotspots(root)` 호출
- `category == "hotspot"` 파일들을 `change_count * coupling` 내림차순 정렬
- Top N (default 5, env `CODEXRAY_AI_TOP_N`)
- N이 hotspot 수보다 크면 그냥 hotspot 전부

### Decision 8: 패키지 구조 — `src/codexray/ai/`
- `ai/types.py` — `DimensionReview`, `FileReview`, `ReviewResult`, `Skipped`
- `ai/prompt.py` — `build_prompt(rel_path, source) -> str`, `parse_response(text) -> dict | None`
- `ai/adapters.py` — `AIAdapterError`, `CodexCLIAdapter`, `ClaudeCLIAdapter`, `select_adapter(env)`
- `ai/build.py` — `build_review(root, top_n=5, adapter=None) -> ReviewResult`
- `ai/serialize.py`, `ai/__init__.py`

### Decision 9: 테스트 전략
- 단위 테스트 — `subprocess.run` mock으로 어댑터 호출 검증
- 프롬프트 빌더 — 입력→문자열 결정론 검증
- 응답 파서 — 유효 JSON, 누락 키, 잘못된 score 범위, 빈 evidence_lines, 잘못된 confidence 등 5+ 케이스
- `select_adapter` — `shutil.which` mock으로 우선순위·env 강제 검증
- 통합 — `build_review`에 페이크 어댑터 주입 → ReviewResult 검증
- 실측 — `CODEXRAY_TEST_REAL_AI=1` 환경변수로 enable, 기본 skip

### Decision 10: opt-in 강조 — CLI 명령에 명시 사용 가능 backend 표시
`codexray review <path>` 실행 시:
1. 어댑터 자동 선택, stderr에 1줄 안내: `using AI backend: codex` (또는 claude)
2. 미설치 시 친절한 에러 (어떻게 설치할지 + opt-in 의도 명시)

## Risks / Trade-offs

- **[리스크] CLI 명령 인자/플래그가 도구 버전마다 다름** → 어댑터를 단순 stdin/stdout 패턴으로 짜고 실측에서 깨지면 후속에서 보정. 1차 가설 명세에 박음.
- **[리스크] AI 응답이 JSON 아닌 일반 텍스트로 오는 경우** → ```json ... ``` 블록 정규식 못 찾으면 `Skipped` 등록. 사용자에게 stderr 1줄 경고. retry 안 함 (1차).
- **[리스크] 모델이 잘못된 라인 번호 인용** → 검증 단계에서 라인 번호가 파일 LoC 범위 안인지 검사. 범위 밖이면 invalid.
- **[리스크] 프롬프트 누수(시스템 프롬프트 무시)** → "다른 텍스트 금지" 명시 + 코드 블록 추출로 부분적으로 견고. 1차 수용.
- **[트레이드오프] 한국어 프롬프트 → 영어 코드베이스에서 어색한 코멘트 가능** → 1차 결정. 사용자(한국어 사용자)에게 우선 가치. 후속 변경에서 언어 옵션화.
- **[리스크] Real AI 호출 시 토큰 비용** → 1차에는 트래킹 없음. 사용자가 본인 구독 한도 안에서 자유. 명세에 5분 timeout으로 무한루프 방지.
- **[리스크] hotspot 0개인 코드베이스** → ReviewResult 비어있음. 정상 동작 (스키마 v1 비어 있는 reviews 허용).

## Open Questions

- codex CLI 0.125의 정확한 비대화 invocation? (실측 단계에서 확인. 그동안 어댑터는 가설 명세대로)
- `claude -p`가 응답 외 색상·헤더를 stdout에 섞는지? (실측에서 확인. ```json ``` 블록 추출이 첫 방어선)
- Top N 결정 — 5가 적절? CivilSim hotspot 23개 중 5개로 시작. 사용자 의견 받아 조정.
- limitations 필수화가 너무 강한 강제? 일부 파일은 진짜 한계 없을 수 있음. 1차에선 의무, 후속 조정 가능.
