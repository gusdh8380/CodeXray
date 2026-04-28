## Context

web-ui spec은 "한국어 설명 sidebar"를 정적 텍스트로 가진다. 사용자 원래 의도는 "raw 분석 결과 JSON을 시니어 개발자 관점에서 분석한 인사이트"였고, 정적 텍스트는 주니어 학습용으로 별도다. 이 변경은 의도와 구현의 차이를 메우면서 AI CLI 호출 패턴을 web UI에서 재사용 가능한 형태로 정착시킨다.

## Goals / Non-Goals

**Goals:**
- 시니어 패널: 사용자가 보고 있는 raw JSON을 입력으로 한 동적 인사이트 (3~5 불릿)
- 주니어 패널: 메트릭 개념 학습용 정적 텍스트 (항상 표시, 오프라인 가용)
- AI 호출은 명시 opt-in (latency 30초~수분)
- 같은 raw JSON · 같은 adapter · 같은 prompt version에 대해서는 같은 인사이트 (디스크 캐시)
- AI 미설정 / 실패 시 graceful fallback

**Non-Goals:**
- 모든 탭 클릭마다 자동 AI 호출
- 인사이트 history / diff / export
- 인사이트 검증·평가 시스템 (사용자 판단에 위임)
- 다중 모델 결과 비교
- AI subprocess hard-kill
- 캐시 GC (별도 변경)
- prompt v2 개정 (별도 변경)

## Decisions

### Decision 1: 시니어 = 동적, 주니어 = 정적

**대안 A** 둘 다 동적 (시니어/주니어 두 prompt로 각각 AI 호출)
**대안 B** 둘 다 정적 (현재 구현)
**선택** 시니어 동적 + 주니어 정적

근거: 주니어 학습 텍스트는 메트릭별 보편 개념이라 raw JSON에 의존하지 않고 정적이면 충분하다. 두 패널 모두 AI 호출하면 비용·latency가 두 배가 된다. 정적 fallback이 있어야 오프라인 / AI 미설정 환경에서도 도구가 가치 있다.

### Decision 2: AI 입력은 raw JSON 자체

**대안 A** rendered HTML을 AI에 입력
**대안 B** raw JSON을 AI에 입력 (선택)

근거: HTML은 presentation. AI가 정확히 분석하려면 구조화된 JSON이 더 정확하다. raw JSON은 builder의 1차 진실이고 readable HTML은 그 파생물이다. 사용자도 "raw json 분석 결과 파일을 보고 분석"이라고 명시했다.

### Decision 3: 디스크 캐시 + 결정론 흉내

**경로**: `~/.cache/codexray/insights/<sha256_key>.json`
**키**: `sha256(path | tab | raw_json_sha256 | adapter_id | prompt_version)`
**TTL**: 없음. raw JSON이 바뀌면 키가 바뀌어 자동 갱신. "다시 생성" 버튼이 강제 무효화.

근거: AI 응답은 비결정적이다. 캐시 없이는 매 클릭마다 30초~수분 재호출. 같은 입력 → 같은 결과를 흉내내고 비용·latency를 절감한다. raw_json_sha256을 키에 포함하므로 코드 변경으로 분석 결과가 달라지면 자동으로 재생성된다.

### Decision 4: AI review의 background job 패턴 재사용

`src/codexray/web/jobs.py`의 background job + polling + cancel 인프라를 그대로 사용한다. job kind에 `insights`를 추가한다.

근거: 두 종류의 job 인프라를 만들면 일관성이 깨진다. cancel UX, polling fragment, status state machine이 동일해야 사용자 멘탈 모델이 단순하다.

### Decision 5: 안전장치 (AI 응답 형식 강제)

응답 파서가 다음을 만족하지 못하면 결과를 `skipped`로 격리한다:
- 빈 본문
- 불릿 1개 미만 또는 10개 초과
- risk 0개 또는 next-action 0개
- 각 불릿 길이 5자 미만

근거: ai-review의 안전장치 패턴(빈 evidence_lines, 라인 범위 초과 등)과 일관. AI 응답 신뢰성을 제품 레벨에서 강제한다.

### Decision 6: prompt 버전 관리

`prompt_version = "v1"` 상수로 시작. 캐시 키에 포함한다. prompt 개정 시 v2로 올리면 모든 v1 캐시는 자연스럽게 무효화된다.

근거: prompt 변경이 무성의하게 캐시된 결과를 오염시키는 것을 방지한다.

### Decision 7: Dashboard 탭 처리는 본 변경에서 비활성화

Dashboard 탭은 raw 출력이 HTML이라 AI 입력으로 부적합하다(큰 텍스트 + presentation). 두 옵션 — (a) 같은 path의 합산 builder dict를 AI에 입력 (b) Dashboard에는 인사이트 패널 비활성화. 이 변경에서는 (b)로 비활성화하고 후속 변경에서 (a)를 검토한다.

### Decision 8: Adapter 선택은 기존 환경변수 그대로

`CODEXRAY_AI_BACKEND={auto,codex,claude}` 환경변수와 `select_adapter()`를 재사용한다. adapter_id는 캐시 키에 포함되므로 백엔드를 바꾸면 자동 재생성된다.

근거: 일관성. 새 환경변수를 추가하지 않는다.

## Risks / Trade-offs

- **[리스크] AI latency**: 30초~수분. opt-in + background job + cancel + 디스크 캐시로 완화.
- **[리스크] AI 응답 비결정**: 디스크 캐시로 사용자 체감은 결정론적. 단 prompt v1 품질이 약하면 모든 캐시 결과가 약해진다 — 후속 변경에서 v2 개선.
- **[리스크] 캐시 디렉토리 무한 증가**: 사용자가 여러 path를 분석하면 누적된다. 1차 단추는 GC 없음, 후속 변경에서 LRU 또는 명시 cleanup CLI 검토.
- **[트레이드오프] 정적 주니어 텍스트 품질**: 동적 생성보다 보편적이고 덜 맞춤화. 단순성·오프라인 가용성·비용 절감 가치가 더 크다.
- **[리스크] AI quota 비용**: codex/claude CLI 호출은 사용자 quota를 소비한다. 캐시·opt-in으로 완화.
- **[리스크] 안전장치가 AI 응답을 너무 자주 격리**: prompt v1이 형식을 정확히 따르지 못하면 사용자가 "skipped"만 본다. 1차 단추는 prompt를 명시적으로 형식 지시하고 후속 변경에서 v2로 다듬는다.

## Open Questions

- Dashboard 탭에 인사이트 적용은 합산 builder dict로 가능한가? (별도 변경)
- 캐시 GC 전략은? (별도 변경 — `codexray cache clear` CLI)
- 인사이트 prompt v2: 사용자 피드백 후 개선 (별도 변경)
- 인사이트를 코드 베이스 진단 리포트로 export 가능한가? (별도 변경)
- 인사이트를 두 시점 비교(`diff` 모드)로 활용 가능한가? (별도 변경 — diff 모드와 함께)
