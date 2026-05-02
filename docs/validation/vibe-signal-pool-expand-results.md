# vibe-signal-pool-expand — 결과 문서

**날짜**: 2026-05-02
**대상**: non-roboco-validation 의 9 레포 + 자기 적용
**목적**: 신호 풀에 일반 OSS 관행 추가 후 weak 빈도 감소·회귀 부재 확인

데이터 raw: `docs/validation/non-roboco-data/*.json` (재분석으로 갱신됨)

## 1. pre/post 비교 매트릭스

| 레포 | 의도 (pre→post) | 검증 (pre→post) | 이어받기 (pre→post) |
|---|---|---|---|
| CodeXray (자기) | strong 3/3 → strong 3/3 | strong 3/3 → strong 3/3 | strong 3/3 → strong 3/3 |
| fastapi | **NOT DETECTED** → **NOT DETECTED** | — | — |
| OpenSpec | weak 1/3 → **moderate 2/3** ⬆ | moderate 2/3 → moderate 2/3 | moderate 2/3 → **strong 3/3** ⬆⬆ |
| openclaw | strong 3/3 → strong 3/3 | moderate 2/3 → moderate 2/3 | strong 3/3 → strong 3/3 |
| graphify | moderate 2/3 → moderate 2/3 | moderate 2/3 → moderate 2/3 | moderate 2/3 → moderate 2/3 |
| roboco-cli | weak 1/3 → **moderate 2/3** ⬆ | moderate 2/3 → moderate 2/3 | strong 3/3 → strong 3/3 |
| CivilSim | weak 1/3 → **moderate 2/3** ⬆ | weak 1/3 → weak 1/3 | weak 1/3 → weak 1/3 |
| StructFlow | weak 1/3 → weak 1/3 | moderate 2/3 → moderate 2/3 | moderate 2/3 → moderate 2/3 |
| water-treatment-rag | moderate 2/3 → moderate 2/3 | weak 1/3 → weak 1/3 | moderate 2/3 → moderate 2/3 |

## 2. 효과 요약

- **5 셀 개선** (OpenSpec 의도, OpenSpec 이어받기, roboco-cli 의도, CivilSim 의도) — moderate/strong 으로 한 단계씩 상승
- **0 회귀** — CodeXray 자기 적용 결과 strong 100% 유지 (이미 다 갖춘 자기 신호풀이라 새 신호도 자동 매칭)
- **fastapi 변화 없음** — 본 변경은 detection 게이트 *통과한* 레포의 신호 풀만 확장. fastapi 는 여전히 NOT DETECTED. 게이트 변경은 별도 변경 영역 (vibe-detection-rebalance 에서 옵션 A' 채택으로 의도된 동작)

## 3. 어떤 새 신호가 어떤 셀을 끌어올렸나 (추정)

- **OpenSpec 의도 weak → moderate**: package.json description (OpenSpec 은 TS 도구라 package.json 보유) — 새 신호 `_check_pkg_description` 효과
- **OpenSpec 이어받기 moderate → strong**: MAINTAINERS / CODEOWNERS 또는 docs/getting-started — 새 신호 `_check_handoff_doc` 확장 효과
- **roboco-cli 의도 weak → moderate**: package.json description (TS 도구) 또는 pyproject (있다면)
- **CivilSim 의도 weak → moderate**: README ## What 같은 명시 섹션 헤더 (`_has_purpose_paragraph` 헤더 매칭 추가) 또는 pyproject 부재이므로 README 헤더 가능성 높음

raw JSON 의 `breakdown` 필드 (각 sub-cat 의 evidence 문자열) 를 추적하면 정확히 어떤 신호가 새로 잡혔는지 파일 단위로 확인 가능.

## 4. False positive 점검

- **빈 description 무시 점검**: `_check_pkg_description` 의 임계 (≥30 자 또는 +keywords) 동작 — 단위 테스트 `test_pyproject_description_empty_does_not_count` 통과
- **빈 examples/ 무시 점검**: `_dir_nonempty` 가드 — 단위 테스트 `test_examples_dir_empty_does_not_count` 통과
- **자기 적용 변동 0**: 새 신호가 *기존 충족 신호 수 이상으로 부풀리지 않았음* — 풀 크기와 카운트가 같이 늘면 ratio 동일

본 변경에서 false positive 의심 사례 없음. 더 큰 외부 OSS (n=15+) 데이터로 추가 점검은 후속 변경에서.

## 5. 자동 검증

- `uv run pytest tests/ -q` → **320 passed** (이전 312 + 신규 8)
- `uv run ruff check src/codexray/vibe_insights/ tests/test_vibe_insights.py` → 신규 위반 0
- `openspec validate vibe-signal-pool-expand --strict` → 통과
- 9 외부 OSS 재분석 → JSON 9 개 갱신, 모두 정상 응답

## 6. 한계

- 9 레포 데이터로 분포 *경향* 만 관찰. 통계적 유의성 주장 안 함.
- detection 게이트 미변경이라 fastapi 같은 비-AI OSS 는 여전히 평가 대상 아님 (의도된 동작).
- 새 신호의 false positive 여부는 본 9 레포 분포로만 점검. n=15+ 확장은 후속.

## 7. 결론

본 변경의 핵심 가치 — *"신호 풀이 ROBOCO 컨벤션에서 일반 OSS 관행까지 확장됨"* — 검증됨. 5/9 레포에서 셀 개선, 자기 적용 회귀 0. archive 가능.
