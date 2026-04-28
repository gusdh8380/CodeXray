## Context

`docs/intent.md` MVP feature 5번이 처음부터 "강점/약점 Top 3"를 요구했지만 구현된 적 없다. 사용자 표명 "Overview에 잘한 점/아쉬운 점이 있으면 좋겠다"는 같은 요구를 다시 가져온 것이다. 현재 quality / hotspots / metrics / entrypoints builder가 모두 결정론적 JSON을 출력하므로, 그 위에 light aggregation 룰만 얹으면 5초 게이트 안에서 "강점 Top 3 / 약점 Top 3 / 다음 행동 Top 3" 추출이 가능하다. AI는 본 변경에서 사용하지 않는다 — Intent의 success criteria("리포트만 보고 다음 행동 결정")는 결정론적 룰만으로 충분히 만족된다.

## Goals / Non-Goals

**Goals:**
- Intent 5번 "강점/약점 Top 3" 채움
- 결정론적 룰 기반 추출 (같은 입력 → 같은 출력)
- 모든 항목에 근거 인용 의무 (file path / score / grade / count)
- CLI · Markdown · Web UI Overview · Web UI Report 4 출구에 일관 표시
- 5초 게이트 통과 (light aggregation, 새 builder 추가 비용 무시 가능)
- self + CivilSim 두 트리에서 의미 있는 결과

**Non-Goals:**
- AI 호출 (룰 기반만)
- 사용자 정의 임계치 (모든 cutoff은 design.md에 명시 + 후속 변경에서 조정)
- Top N 가변 (3 고정)
- 시계열 추세 / diff 모드 (별도 변경)
- Markdown PDF 출력 (별도 변경)
- 강점/약점 항목의 자연어 풀어쓰기 AI (결정론 위반)

## Decisions

### Decision 1: 새 capability `summary` (cross-cutting builder)

**대안 A** `report` capability 안에 흡수 — 새 builder 안 만듦
**대안 B** 신규 `summary` capability — 자체 builder + spec + types (선택)

근거: `summary`는 quality + hotspots + metrics 결과를 *집계*하는 명확한 책임이 있고, web UI Overview / Report 둘 다 같은 결과를 재사용하므로 builder 분리가 자연스럽다. report capability에 흡수하면 web UI에서 report builder를 통째로 호출해야 하는 사이드 이펙트가 생긴다. 신규 capability가 깔끔.

### Decision 2: 결정론적 룰 (1차 cutoff)

**강점 룰**:
- (S1) `quality.dimensions[*].grade` 중 A 또는 B인 차원 — 차원 이름 + 점수 + 등급 인용
- (S2) `hotspots.summary.stable / total >= 0.5` — stable ratio + count 인용
- (S3) `metrics.graph.is_dag == true` — "순환 없음" + node_count 인용
- (S4) Top hotspot의 `category == "active_stable"` — path + change_count 인용

**약점 룰**:
- (W1) `quality.dimensions[*].grade` 중 D 또는 F인 차원 — 차원 이름 + 점수 + 등급 인용
- (W2) `neglected_complex` 카테고리 파일 존재 — Top 1 path + coupling 인용
- (W3) `metrics.graph.largest_scc_size > 1` — SCC 크기 + 예시 노드 인용
- (W4) Top hotspot의 `category == "hotspot"` — path + change_count × coupling 인용

**다음 행동 매핑** (각 약점 → 행동):
- W1 test 차원 D/F → "characterization test 우선 보강"
- W1 coupling 차원 D/F → "결합도 분해 (책임 분리)"
- W1 documentation D/F → "문서화 진입점 작성"
- W1 cohesion D/F → "모듈 책임 재정렬"
- W2 → "neglected_complex 파일 소유권·테스트 정리"
- W3 → "최대 SCC 끊기 (한 모듈 추출)"
- W4 → "Top hotspot에 테스트 + 책임 분리"

**Top 3 선정 우선순위** (강점·약점 모두): grade F > grade D > 카테고리 매칭(W2/W4) > SCC > 그 외. 동률은 알파벳 정렬.

근거: cutoff은 *기존 quality*의 A~F 등급에 의존하므로 일관성 보장. 추가 임계치 없음. 후속 변경에서 cutoff 조정.

### Decision 3: 근거 인용 의무

각 항목 (`Strength` / `Weakness` / `Action`)의 dataclass에 `evidence: dict[str, str | int]` 필드 의무. constraints.md "도구는 판단 근거이지 판단 자체가 아니다"의 직접 적용. AI review의 `evidence_lines`와 같은 정신.

### Decision 4: 출구 4개에 일관 렌더링

- CLI Markdown report — 등급 직후 / 핫스팟 직전에 3 섹션 삽입
- Web Overview 탭 메인 영역 — 3 카드 그리드 (강점 / 약점 / 다음 행동) — 각 카드는 Top 3 불릿 + 근거 부속 표시
- Web Report 탭 readable HTML — Markdown 와 같은 3 섹션
- (CLI JSON으로 별도 `codexray summary <path>` 명령은 후속 변경 — 본 변경에서는 builder · render · report integration까지)

### Decision 5: 결정론 보장

`Strength` / `Weakness` / `Action` 항목 정렬 키:
1. severity tier (F > D > A/B)
2. evidence numeric (높은 score · count 우선)
3. 마지막 tiebreak는 알파벳 (path 또는 dimension 이름)

같은 입력 → 같은 stdout 바이트. 회귀 테스트로 강제.

### Decision 6: 5초 게이트

`build_summary(root)`은 quality + hotspots + metrics + entrypoints + inventory 결과를 받아 light aggregation만 수행. 이미 모두 5초 안에 빌드되므로 추가 비용은 무시 수준. 단 `report` builder가 한 번에 모두 빌드하던 것을 재사용 — 중복 호출 회피.

## Risks / Trade-offs

- **[리스크] 룰이 단순해 사용자 코드베이스에 일관되지 않을 수 있음** → 1차 cutoff은 보수적으로 설정 (A/B = 강점, D/F = 약점). 후속 변경에서 사용자 피드백 반영해 조정.
- **[리스크] Top 3 고정이 작은 코드베이스에서 어색** → fallback: 항목이 3개 미만이면 있는 만큼만, 0개면 "특이사항 없음" placeholder.
- **[트레이드오프] AI 미사용으로 항목이 메마름** → constraints.md "도구는 근거" 정신으로 충분. AI는 후속 변경에서 강점/약점 한 줄 풀어쓰기로 *opt-in 추가* 가능.
- **[리스크] report builder가 summary builder를 다시 호출하면 중복 계산** → report builder가 입력으로 quality·hotspots·metrics를 이미 가짐. summary builder는 그것을 인자로 받게 시그니처 잡고 중복 계산 없음.
- **[리스크] 룰 확장 시 매핑 폭증** → 다음 행동 매핑은 사전(dict) 기반이라 후속 cutoff 추가가 쉬움. 1차 7~8개 매핑으로 시작.

## Open Questions

- 강점이 정말 0개일 때 사용자 신뢰는? (1차에서 placeholder로 처리, 후속에서 metric/entrypoint 다양화)
- `codexray summary <path>` 별도 CLI 명령으로 분리할 가치? (본 변경에서는 미포함, 후속에서 결정)
- 다음 행동 매핑을 사용자가 customize 할 수 있어야 하는지 (현재는 코드 안 dict)
