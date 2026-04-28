## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/hotspots/__init__.py` — 공개 API
- [x] 1.2 `src/codexray/hotspots/types.py` — `FileHotspot`, `Thresholds`, `Summary`, `HotspotsReport`

## 2. git log 어댑터

- [x] 2.1 `hotspots/git_log.py` — `is_git_repo`, `change_counts`
- [x] 2.2 `git rev-parse --is-inside-work-tree` 검사
- [x] 2.3 `git log --name-only --pretty=format:` 파싱 + allowed paths 필터
- [x] 2.4 단위 테스트 — git repo + 카운트 / 비-git 폴백 / allowed 필터

## 3. 빌더

- [x] 3.1 `hotspots/build.py` — `build_hotspots`
- [x] 3.2 graph + metrics → 노드별 coupling = `fan_in+fan_out+external_fan_out`
- [x] 3.3 git 가능 여부에 따라 change_counts 또는 0
- [x] 3.4 중앙값 계산 + 4 카테고리 분류
- [x] 3.5 비-git 폴백 — coupling 단일 차원, hotspot/stable만
- [x] 3.6 정렬: path 사전순
- [x] 3.7 단위 테스트 — git repo 분류 / 비-git 폴백 / summary 합 검증 / 정렬

## 4. 직렬화

- [x] 4.1 `hotspots/serialize.py` — to_json
- [x] 4.2 단위 테스트 — 스키마 키 / 결정론

## 5. CLI 통합

- [x] 5.1 `cli.py`에 `hotspots` 서브커맨드
- [x] 5.2 경로 검증 재사용
- [x] 5.3 단위 테스트 — JSON 파싱, 키 일관성

## 6. 검증

- [x] 6.1 통합 테스트 — 임시 git repo + 변경 시뮬레이션
- [x] 6.2 비-git 트리 통합 테스트
- [x] 6.3 결정론 회귀
- [x] 6.4 CodeXray 자기 자신 실측 — 0.22s, 42 hotspots, top: cli.py(5×17). `docs/validation/hotspots-self.md`
- [x] 6.5 CivilSim 실측 — 0.69s, 23 hotspots, top: GameManager.cs(15×45). `docs/validation/hotspots-civilsim.md`
- [x] 6.6 `openspec validate add-hotspots` 통과
- [x] 6.7 `ruff check` + `pytest` 모두 통과 (177/177)
