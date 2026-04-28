## Context

`add-graph-csharp`이 namespace 단위 1:N 매핑으로 끝났다. CivilSim 검증에서 결합도 측정이 부풀려져 정량 평가에 노이즈를 키운다는 사실이 `add-quality-quant` 검증으로 드러났다. 이 변경은 type-resolution을 도입해 1:1로 좁히되, 외부 컴파일러(Roslyn) 없이 정규식·휴리스틱으로 실용적 정확도를 낸다.

## Goals / Non-Goals

**Goals:**
- C# `using N;`이 실제로 사용된 type만 internal 엣지로 매핑
- 파일 자체의 namespace에 속한 type 사용도 implicit internal 엣지
- CivilSim 검증에서 internal 엣지 수 감소 + coupling 점수 의미 있는 개선
- 5초 예산 유지
- Python·JS/TS 동작 무영향

**Non-Goals:**
- 정밀한 타입 시스템 분석 (제네릭 인스턴스, 상속 체인, 멤버 접근) — 후속
- alias `using A = X.Y;` 처리 — 후속
- `global using` 처리 — 후속
- `using static X.Y.Type;`의 멤버 단위 분석 — 1차에서는 그냥 type 사용으로 카운트
- attribute(`[XAttribute]`)·base class·인터페이스 implementation에서 type 사용 별도 가중 — 1차에선 모두 동등 토큰

## Decisions

### Decision 1: type 인덱스 — `(namespace, type_name) -> file`
- 트리의 모든 `.cs` 파일을 1회 스캔
- 각 파일에서:
  - 블록 namespace `namespace X { ... }` 또는 파일 스코프 `namespace X;` 안에 있는 `class|interface|struct|record|enum Name` 추출
  - 글로벌 namespace 안 type은 인덱스에 등록 안 함 (어차피 어떤 `using`으로도 매칭 안 됨)
- 동일 (namespace, type) 쌍이 여러 파일에 나오면 (예: partial class) — 1차에서는 마지막 등록만 유지 (간단성 우선). partial class 정확도는 후속.

### Decision 2: namespace 경계 파서 — 단순 brace 카운터
- 정규식으로 `namespace X { ... }` 시작 찾고, `{`/`}` 카운터로 끝 위치 계산
- 문자열·주석 안의 `{`/`}`는 거짓양성 가능성 있지만 일반 C# 파일에서 드묾 → 1차 수용
- 파일 스코프 (`namespace X;`)는 나머지 전부가 X 범위
- 한 파일에 여러 namespace 블록 가능

### Decision 3: type 사용 추출 — 주석·문자열 제거 후 PascalCase 토큰
- 정규식으로 문자열 리터럴(`"..."`, `'...'`), 라인 주석(`//...`), 블록 주석(`/* ... */`) 제거
- 그 다음 `\b[A-Z]\w*\b` 매칭 → set으로 dedupe
- 거짓양성 가능 (enum value, 상수, 정적 메서드명) — 모두 type 후보로 들어가지만 type 인덱스에 없으면 매칭 안 되므로 무해
- 거짓음성 — `var x = ...` (var는 type 추론) → 직접 사용된 type 이름은 좌변 RHS에 등장. 일반적으로 OK.

### Decision 4: resolve 결과 — list[Path]
- 빈 list = external (호출 측이 raw 문자열로 fallback)
- 비어있지 않은 list = internal 엣지 N개
- 자기 파일은 결과에서 제외

### Decision 5: 사용되지 않는 `using` 처리 — 엣지 생성 안 함
- `using N;`이 인덱스에 있고 파일에 어떤 N 안 type도 사용 안 하면 엣지 0개
- "external N"으로 fallback하지 않는다 — N은 분명 internal namespace이므로 external 라벨이 거짓
- 1차 결정. 사용자가 "이 using이 쓰이는지" 보고 싶으면 후속 변경에서 dead-using 검출 별도 분리

### Decision 6: implicit own-namespace scope
- 파일이 `namespace X { ... class X.A; ...}` 식으로 자신의 namespace 안에서 type을 쓸 때
- 코드에 `using X;` 안 적혀 있어도 같은 namespace 안 type은 자동 internal 매핑
- 즉 자기 namespace를 implicit `using`으로 취급
- spec에 "자기 declared namespace의 type도 implicit scope" scenario 추가

### Decision 7: 기존 spec scenario 갱신
- "1:N 엣지" 시나리오 (`A.cs`+`B.cs` 둘 다 App.Core, `Main.cs` using App.Core;) → 더 이상 단순히 2 엣지 안 만든다. Main.cs가 어떤 type을 쓰느냐에 따라:
  - A type만 사용 → A.cs로 1 엣지
  - B type만 사용 → B.cs로 1 엣지
  - A, B 둘 다 사용 → 2 엣지
  - 어느 것도 안 사용 → 0 엣지
- spec MODIFIED 항목으로 시나리오 수정

### Decision 8: 결정론
- 사용된 type set의 정렬 순서로 매칭 → resolve 반환 list가 정렬됨
- 그래프 결정론은 build.py가 set 기반으로 dedupe + sort하므로 무영향

## Risks / Trade-offs

- **[리스크] 거짓양성 type 사용 추출** (PascalCase 토큰이 type가 아닐 때) → type 인덱스에 없으면 무해. 인덱스에 있는데 우연히 같은 이름이면 잘못된 internal 엣지. 빈도 낮음.
- **[리스크] 거짓음성** — `var`, 동적 type, generic instantiation의 일부 type 누락. 1차 수용, 후속에서 정확도 향상.
- **[리스크] 사용되지 않는 `using` 0 엣지** — 사용자가 그래프에서 그 using을 못 봐서 혼란 가능. 후속 변경에서 dead-using 별도 출력 옵션 검토.
- **[트레이드오프] 일부 internal 엣지 감소** — CivilSim에서 457 → 더 작은 수. 결합도 점수 상승 예상. 좋은 방향이지만 `add-graph-csharp` 검증 메모와 수치 차이 발생 — 새 검증 메모 작성으로 추적.
- **[리스크] partial class 정확도** — 같은 (ns, type)가 여러 파일에 → 1차는 last-wins. 잘못된 1 파일에만 엣지가 갈 가능성. 1차 수용, 후속.

## Open Questions

- 사용된 type을 count로 보고 노드별 가중 fan-out 노출할지? (1차는 binary, 추후 가중 가능)
- 라이브러리 internal 사용(System, UnityEngine) 패턴이 일관되게 external로 떨어지는지 검증 메모로 확인
