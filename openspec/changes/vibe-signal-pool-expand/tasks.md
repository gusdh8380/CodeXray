## 1. axes.py — 헬퍼 추가

- [x] 1.1 `_dir_nonempty(root, path)` 헬퍼 추가 (디렉토리 존재 + 비어있지 않음 보장)
- [x] 1.2 `_check_pkg_description(root)` 헬퍼 추가 — pyproject.toml + package.json description 충실도 (≥ 30 자 또는 keywords 동봉) 점검

## 2. 의도 축 — 프로젝트 의도 문서 신호 풀 확장

- [x] 2.1 `_check_project_intent_doc` 에 pyproject.toml description 검사 추가
- [x] 2.2 `_check_project_intent_doc` 에 package.json description 검사 추가
- [x] 2.3 `_has_purpose_paragraph` 에 README 명시 섹션 헤더 매칭 (`## What`, `## Why`, `## Purpose`, `## About`, 한국어 `## 이 프로젝트` 등) 추가

## 3. 검증 축 — 손 검증 흔적 신호 풀 확장

- [x] 3.1 `_check_manual_validation` 에 `examples/`, `demo/`, `samples/`, `examples-*` 패턴 검사 추가 (디렉토리 비어있지 않음 가드 사용)
- [x] 3.2 `_check_manual_validation` 에 `.storybook/` 디렉토리 검사 추가

## 4. 이어받기 축 — 핸드오프 문서 신호 풀 확장

- [x] 4.1 `_check_handoff_doc` 에 `MAINTAINERS.md`, `MAINTAINERS`, `CODEOWNERS`, `.github/CODEOWNERS` 검사 추가
- [x] 4.2 `_check_handoff_doc` 에 `docs/getting-started/`, `docs/onboarding/`, `docs/contributing/` 디렉토리 검사 추가

## 5. 단위 테스트

- [x] 5.1 `tests/test_vibe_insights.py` 에 신규 신호별 테스트 추가:
  - [x] 5.1.1 pyproject description 30 자 이상 → 의도 신호 충족
  - [x] 5.1.2 pyproject description 빈 문자열 → 의도 신호 미충족
  - [x] 5.1.3 package.json description + keywords → 의도 신호 충족
  - [x] 5.1.4 README `## What` 섹션 → 의도 신호 충족 (첫 5 단락 키워드 없는 케이스)
  - [x] 5.1.5 examples/ 비어있지 않음 → 검증 신호 충족
  - [x] 5.1.6 examples/ 빈 디렉토리 → 검증 신호 미충족
  - [x] 5.1.7 MAINTAINERS.md 존재 → 이어받기 신호 충족
  - [x] 5.1.8 docs/getting-started/ 존재 → 이어받기 신호 충족

## 6. 회귀 점검

- [x] 6.1 `uv run pytest tests/ -q` 통과 (예상: 312 → 320 정도)
- [x] 6.2 `uv run ruff check src/codexray/vibe_insights/ tests/test_vibe_insights.py` 통과
- [x] 6.3 자기 적용 — `validate_external_repos.py` 로 CodeXray 분석, 의도/검증/이어받기 모두 strong 유지 확인. 이전 `docs/validation/non-roboco-data/CodeXray.json` 과 비교
- [x] 6.4 9 외부 OSS 재분석 — `docs/validation/non-roboco-data/*.json` 갱신
- [x] 6.5 `docs/validation/vibe-signal-pool-expand-results.md` 작성 — 9 레포 pre/post 비교 표 + weak 감소 분포 요약 + false positive 점검 결과

## 7. 검증 + 문서화

- [x] 7.1 `openspec validate vibe-signal-pool-expand --strict` 통과
- [x] 7.2 CLAUDE.md "Current Sprint" 갱신
- [x] 7.3 git commit (atomic 단위)

## 8. Archive

- [x] 8.1 `openspec archive vibe-signal-pool-expand`
- [x] 8.2 archive 후 main spec 동기화 확인 — vibe-coding-insights 에 ADDED 2 개 반영
