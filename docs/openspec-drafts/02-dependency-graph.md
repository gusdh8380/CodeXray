# Draft proposal — `add-dependency-graph`

> 두 번째. 인벤토리에서 본 파일 목록 위에 모듈 간 의존성 그래프를 얹는다.
> MVP 기능 #1(구조 분석)의 두 번째 조각.

## /opsx:propose payload (복사해서 붙여넣기)

```
add-dependency-graph: 인벤토리 위에 import/require 기반 모듈 의존성 그래프를 추출.

Why
- 인벤토리만으로는 "구조"를 보여주지 못한다. 의존성 그래프가 핫스팟 매트릭스, 영향 범위
  역추적, 진입점 식별의 공통 기반이다. 한 번 만들어두면 이후 변경들이 모두 이 그래프를
  소비할 수 있다.

What changes
- CLI: `codexray graph <path>` — JSON으로 노드/엣지 출력
- 노드: 파일 단위 (모듈은 후속)
- 엣지: import/require 정적 파싱 (Python `import`, JS/TS `import`/`require`)
- 순환 의존 탐지 + 카운트 보고
- 인벤토리 결과(`codexray inventory`)와 동일 입력 인터페이스 공유

Non-goals
- 호출 관계(함수·클래스 단위) — 별도 변경
- 진입점 자동 식별 — 별도 변경
- 시각화(웹 대시보드) — 별도 변경
- Java / C# 파서 — 첫 통과는 Python + JS/TS만

Validation target
- 사용자의 작은 게임 프로젝트에서 노드/엣지 카운트가 손으로 센 것과 일치
- 의도적으로 만든 순환 의존 케이스가 탐지됨
```

## 왜 두 번째인가
- 인벤토리(파일 목록) → 그래프(엣지) 순서가 자연스럽다.
- 시각화·핫스팟·영향 분석 모두 이 그래프에 의존. 데이터 모델을 먼저 굳히고 시각화는 나중.
