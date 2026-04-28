## Context

현재 Briefing 탭은 Python이 결정론적으로 슬라이드 텍스트를 생성한다. 수치는 정확하지만 "발표 자료"로 쓸 수 있는 수준의 해석이 없다. 동시에 시니어 인사이트 기능이 이미 각 탭의 raw JSON을 Claude/Codex CLI에 넘겨 해석을 받는 패턴을 구현해놓았다. 이 두 가지를 합치는 것이 이번 변경의 핵심이다.

## Goals / Non-Goals

**Goals:**
- Briefing 탭이 AI 해석을 포함한 종합 분석 결과를 보여준다
- 모든 분석 증거(inventory, graph, metrics, quality, hotspots)를 한 번에 AI에 넘겨 일관된 해석을 받는다
- 분석 진행 상태를 단계별로 보여주는 로딩 UX
- AI 미사용 시 기존 결정론적 Briefing으로 폴백

**Non-Goals:**
- 기존 데이터 탭(Metrics, Hotspots, Quality 등) 제거 — 증거 보기로 유지
- 탭마다 별도 AI 호출 — 하나의 종합 호출로 처리
- 새로운 분석 지표 추가
- 스트리밍 / SSE — 기존 polling 패턴 재사용

## Decisions

### 1. AI 호출 위치: `/api/briefing` 엔드포인트에서

기존 `/api/briefing`이 이미 모든 분석기를 실행한다. 여기서 모든 raw JSON 증거를 묶어 AI에 넘기는 단계를 추가한다. 새 엔드포인트 불필요.

대안 검토: 별도 `/api/ai-analysis` 엔드포인트 — 오버엔지니어링. 기존 흐름 재사용이 단순하다.

### 2. 로딩 패턴: 기존 background job + polling 재사용

Review 탭, 시니어 인사이트와 동일한 패턴.
1. POST /api/briefing → background job 시작 → 즉시 polling fragment 반환
2. GET /api/briefing/status/{job_id} → 완료 시 결과 fragment 반환

단계 진행 메시지: "Python 분석 중...", "증거 수집 완료", "AI 해석 중...", "완료"

### 3. AI 입력 형식

기존 briefing 결정론적 증거(presenter_summary, slides 등) + raw JSON 요약:
```json
{
  "inventory": { "total_loc": ..., "languages": [...] },
  "quality": { "overall_grade": ..., "dimensions": {...} },
  "hotspots": { "top_files": [...], "summary": {...} },
  "metrics": { "avg_coupling": ..., "top_coupled": [...] },
  "graph": { "node_count": ..., "is_dag": ... }
}
```

프롬프트 구조: 시니어 인사이트 패턴과 동일하게 한국어 분석 요청.

### 4. AI 출력 형식

AI가 구조화된 JSON으로 응답:
```json
{
  "executive": "...",
  "architecture": "...",
  "quality_risk": "...",
  "next_actions": ["...", "..."],
  "key_insight": "..."
}
```

파싱 실패 시 raw 텍스트를 단일 섹션으로 표시.

### 5. 폴백 전략

AI 어댑터 미설정 또는 호출 실패 → 기존 결정론적 Briefing 표시 + 상단 배너 "AI 해석 없이 표시 중 — claude 또는 codex CLI 설정 후 재분석하세요"

### 6. 기존 데이터 탭 유지

Metrics, Hotspots, Quality 탭은 그대로 유지. Briefing 결과 하단에 "근거 데이터 보기" 링크로 안내. 탭 구조 변경 최소화.

## Risks / Trade-offs

- AI 호출 시간 30-90초 → 로딩 UX로 완화. 사용자가 대기 시간을 인지함.
- AI 응답 품질 편차 → 기존 insights 안전장치 재사용 (형식 검증)
- 기존 테스트 `test_web_ui.py` 중 briefing 어서션 업데이트 필요
- AI 비용 — 레포 분석당 1회 호출, 캐싱으로 재분석 방지
