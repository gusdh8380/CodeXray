## Why

`metrics`는 노드별 결합도 신호를, `quality`는 코드베이스 전체 등급을 준다. 그러나 사용자의 의사결정 — "어디부터 손봐야 하는가" — 는 두 차원의 조합에서 나온다: **자주 바뀌고 결합도가 큰 파일**(잦은 변경 위험 + 영향 범위 큼)이 우선 개선 후보. 1차에서 `git log` 변경 빈도 × 결합도 매트릭스를 한 번 만들고, 후속(종합 리포트·AI 정성 평가)이 같은 데이터를 받게 한다.

## What Changes

- 새 CLI 진입점: `codexray hotspots <path>` — git log 1회 + 그래프 1회 + 매트릭스 분류 + JSON 출력
- 변경 빈도(change_count): `git log --name-only --pretty=format:` 기반, 분석 대상 노드(Python/JS/TS/C#)에 한정
- 결합도(coupling): metrics의 `fan_in + fan_out + external_fan_out` (노드별 합)
- 매트릭스 분류 (각 차원의 중앙값 기준):
  - **hotspot**: high change × high coupling — 우선 개선 후보
  - **active_stable**: high change × low coupling — 자주 바뀌지만 결합 작음 (보통 OK)
  - **neglected_complex**: low change × high coupling — 안 건드리지만 영향 큼 (정리·이해 후보)
  - **stable**: low change × low coupling — 관망
- 출력 JSON 스키마 v1 (신규 capability `hotspots`):
  ```json
  {
    "schema_version": 1,
    "thresholds": {"change_count_median": 4, "coupling_median": 3},
    "summary": {
      "hotspot": 5,
      "active_stable": 3,
      "neglected_complex": 7,
      "stable": 18
    },
    "files": [
      {
        "path": "src/codexray/cli.py",
        "change_count": 12,
        "coupling": 8,
        "category": "hotspot"
      }
    ]
  }
  ```
- git 저장소가 아닌 트리에 대해서는 stderr에 1줄 안내 + change_count는 0으로 두고 분류는 coupling 단일 차원으로 폴백 (high coupling만 hotspot, 나머지 stable). 사용자가 git이 아닌 트리(unzipped 다운로드 등)도 분석 가능해야 함.

## Capabilities

### New Capabilities
- `hotspots`: 변경 빈도와 결합도를 결합한 노드별 분류 매트릭스를 JSON으로 노출하는 능력. 후속 종합 리포트와 AI 정성 평가가 우선순위로 사용한다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/hotspots/` 서브패키지
  - `hotspots/git_log.py` — `subprocess`로 git log 호출, 파일별 카운트
  - `hotspots/build.py`, `serialize.py`, `types.py`
- 신규 의존성 없음 (stdlib subprocess)
- CLI에 `hotspots` 서브커맨드 추가
- 검증: CodeXray 자기 + CivilSim, 5초 내, hotspot/active_stable/neglected_complex/stable 분포 캡처
- 비-git 트리 케이스 통합 테스트 1개
