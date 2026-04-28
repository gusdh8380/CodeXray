## Context

`metrics`(0.49s, 노드별 fan_in/fan_out)와 `quality`(코드베이스 등급)는 잡혔지만 둘이 노드 단위에서 결합되어 있지 않다. 사용자의 "어디부터?" 질문에 답하려면 변경 활동(과거 행동 신호)과 결합도(현재 영향 신호)를 한 매트릭스에 묶어야 한다. 1차에서 임계치는 중앙값 기반 단순 분할, 후속에서 더 정밀한 quartile/percentile 도입 가능.

## Goals / Non-Goals

**Goals:**
- 변경 빈도 + 결합도 두 차원 매트릭스로 우선 개선 후보 식별
- 5초 예산 내
- git 비저장소 폴백 동작
- 후속(종합 리포트, AI 정성 평가)이 받을 안정 스키마 v1
- 결정론적 출력

**Non-Goals:**
- 변경 *작성자*·라인 수 변경량 분석 — 1차는 파일 단위 변경 카운트만
- 시간 가중치 (최근 변경이 과거 변경보다 무거움) — 1차 동일 가중
- 작성자 응집 (한 사람만 만진 파일) — 후속
- 함수 단위 hotspot — 파일 단위만
- AI 추천·진단 — 정성 평가는 후속

## Decisions

### Decision 1: 별도 명령 (`hotspots`)
같은 패턴 (graph/metrics/entrypoints/quality). 출력 스키마 분리.

### Decision 2: 변경 빈도 — `git log --name-only --pretty=format: -- <path>`
- 호출은 한 번. 출력 파싱: 빈 라인 무시, 파일별 카운트
- 분석 대상 노드(graph 노드)에 한정해 카운트 — graph node에 없는 파일은 무시 (배제 디렉토리·비대상 언어 정리 일관성 확보)
- 시간 범위 옵션은 1차 비대상 (전체 history)

**대안 기각:**
- `git log --numstat`: 라인 변경량 정보 추가하나 파일 카운트만으로 충분. 후속에서 도입.
- `pygit2` 같은 라이브러리: 외부 의존 추가, 1차 비대상.

### Decision 3: 결합도 — `fan_in + fan_out + external_fan_out`
- 한 노드의 종합 결합 신호. internal·external 모두 영향 측면에서 동등 취급.
- metrics와 같은 데이터 (`metrics.NodeMetrics`)를 재사용 — `metrics.build_metrics(graph)` 호출
- 노드별 coupling = `fan_in + fan_out + external_fan_out`

**대안:** internal만, external 별도 가중. 1차에선 통합 단순 합. 후속 변경에서 정밀화.

### Decision 4: 임계치 — 중앙값
- 두 차원 각각 분석 대상 노드들의 중앙값을 임계치로
- 중앙값 ≤ 값 → "high"
- 중앙값 < 값 → "low"
- 모든 값이 동일하면 모두 "low"로 처리 (분포 정보 부족 시 보수적)

**이유:** 단순·결정론적·자동 적응. 후속에서 quartile 또는 사용자 옵션화 가능.

**대안 기각:**
- 절대 임계치(예: change_count > 5): 코드베이스마다 분포 다름.
- 평균: 이상치(매우 큰 파일)에 끌림.
- Quartile: 1차에선 4분류 매트릭스에 과함.

### Decision 5: 분류 매트릭스 — 4 카테고리
- high change × high coupling → `hotspot` (우선 개선)
- high change × low coupling → `active_stable` (모니터)
- low change × high coupling → `neglected_complex` (정리·이해)
- low change × low coupling → `stable` (관망)

### Decision 6: 비-git 트리 폴백
- `git rev-parse --is-inside-work-tree`로 사전 체크
- 실패 시: change_count=0 모든 파일, coupling만으로 분류 (median 기반):
  - high coupling → `hotspot`
  - low coupling → `stable`
  - active_stable / neglected_complex 카테고리는 항상 0
- stderr에 "warning: not a git repository, change frequency unavailable" 1줄

### Decision 7: 출력 — 결정론적 정렬
- `files` 배열은 `path` 사전순
- 카테고리별 카운트는 summary에 4개 키 모두 포함 (값 0 가능)
- thresholds도 노출 — 사용자가 임계치 의미 검증 가능

### Decision 8: 패키지 구조 — `src/codexray/hotspots/`
- `hotspots/types.py` — `FileHotspot`, `Thresholds`, `HotspotsReport`
- `hotspots/git_log.py` — `change_counts(root, paths) -> dict[str, int]`
- `hotspots/build.py` — `build_hotspots(root) -> HotspotsReport`
- `hotspots/serialize.py`
- `hotspots/__init__.py`

### Decision 9: subprocess 안전성
- `subprocess.run` with `cwd=root`, `capture_output=True`, `text=True`, `check=False`
- 타임아웃 30초 (5초 예산보다 큼, 비정상 시만 발동)
- 결과 비-zero exit: change_counts 빈 dict + stderr 경고
- shell=False, 명시 인자 list

## Risks / Trade-offs

- **[리스크] git history 매우 길고 큰 트리에서 `git log --name-only` 시간** — CivilSim 50k 파일 + 수천 커밋 가정 시 1초 이내 예상. 검증으로 확인.
- **[리스크] 임계치 중앙값이 작은 코드베이스(<10 파일)에서 노이즈** — 1차 수용. 검증 메모에 명시.
- **[리스크] 비-git 트리에서 hotspot 분류가 coupling 단독 → 부정확한 우선순위 신호** — stderr 경고로 사용자 알림.
- **[리스크] 파일 rename 시 git log 카운트 분리** — `--follow` 미사용 (1차 수용). 후속에서 `--follow` 도입 검토.
- **[트레이드오프] 결합도 통합 합산** → external 의존이 많은 파일이 신호 부풀림. 1차에선 단순. 후속에서 internal·external 가중 분리 가능.

## Open Questions

- 시간 윈도우(예: 최근 6개월 vs 전체) 옵션 1차 도입할지 — 1차 미도입, 후속 변경에서 `--since` 플래그
- "active_stable"가 정말 OK 카테고리인지 (자주 바뀌면 결합도 작아도 변경 위험은 있음) — 1차에서는 hotspot보다 우선순위 낮음으로 취급
