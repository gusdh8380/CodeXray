# Dependency Graph CLI — 1차 검증

**Change:** `add-dependency-graph`
**Run date:** 2026-04-27 (KST)
**Target:** CodeXray 자기 자신 (`/Users/jeonhyeono/Project/personal/CodeXray`)

## Why CodeXray itself

1차 변경에서 다루는 언어가 Python/JS/TS이고, CivilSim(C# only)은 비대상. 자기참조(`from .x import y`) 해석 정확도와 결정론적 출력 검증에는 자기 자신이 가장 직접적인 표적.

## Result

```
$ uv run codexray graph .
{
  "schema_version": 1,
  "nodes": [...25 entries...],
  "edges": [...85 entries...]
}
```

| metric | value |
|---|---|
| nodes | 25 (Python 자기참조 트리: src/codexray + tests) |
| edges total | 85 |
| internal edges | 31 |
| external edges | 54 (stdlib, typer, pytest 등) |
| schema_version | 1 |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.21s** |
| user | 0.10s |
| sys  | 0.03s |
| budget | 5.00s |
| margin | ≈ 24× under budget |

## Determinism

연속 2회 실행 stdout 바이트 단위 일치 확인:

```
$ uv run codexray graph . > /tmp/run1.json
$ uv run codexray graph . > /tmp/run2.json
$ diff -q /tmp/run1.json /tmp/run2.json
# (no output)
```

## Spot checks

- `src/codexray/cli.py` → `src/codexray/inventory.py` (kind=internal): `from .inventory import aggregate` 정확히 internal로 분류
- `src/codexray/cli.py` → `typer` (kind=external): bare specifier raw 그대로 보존
- `tests/test_language.py` → `src/codexray/language.py` (kind=internal): `from codexray.language import classify` 절대 import가 `src/` 루트 후보로 해석됨
- Java/C# 파일 없음 (대상 언어 아님). 비대상 언어가 트리에 있더라도 노드/엣지 미생성은 단위 테스트(`test_only_target_languages_become_nodes`)로 보장

## Environment

- macOS Darwin 25.4.0 (arm64)
- Python 3.14.3 / uv 0.11.7
- CodeXray 0.1.0 (graph subcommand 추가본)
- 의존성: 변동 없음 (Python `ast` stdlib + 정규식만)

## Observations

1. **5초 게이트 압도적 통과** — 0.21s, 인벤토리 0.52s 대비 더 빠름. 워킹·필터·classify가 inventory와 같은 패스인데 LoC 카운트(전 라인 strip)를 안 하기 때문에 자연스러운 결과.
2. **`from .x import y` 해석 정확** — CodeXray 자기참조 31개 internal 엣지 모두 spot check에서 의도대로 매핑.
3. **JS/TS 검증은 단위/통합 테스트로 충당** — CodeXray 자체엔 JS/TS 없음. `test_graph_cli_emits_valid_json`, `test_graph_js_parser`, `test_graph_resolve.test_js_*` 가 커버.
4. **MVP 구조 분석 두 번째 단추 통과** — `inventory` (무엇이) + `graph` (무엇이 무엇에 의존하는가). 다음 분석(중심성·핫스팟·진입점)이 같은 JSON을 입력으로 받을 수 있는 안정 스키마(v1) 확정.

## Next

- `add-graph-jvm-clr` (가칭): Java `import` + C# `using` 추출. CivilSim 검증은 그때부터 가능.
- `add-graph-metrics` 또는 `add-entrypoints`: 중심성·진입점·SCC 등을 같은 JSON 위에 얹는 변경.
- alias 해석(`@/components`, tsconfig `paths`)은 별도 변경에서.
