# Entrypoints — CodeXray 자기 검증

**Change:** `add-entrypoints`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CodeXray`

## Result

```
$ uv run codexray entrypoints .
{
  "schema_version": 1,
  "entrypoints": [
    { "path": "pyproject.toml", "language": null, "kind": "pyproject_script", "detail": "codexray" },
    { "path": "src/codexray/cli.py", "language": "Python", "kind": "main_guard", "detail": "" }
  ]
}
```

| metric | value |
|---|---|
| count | 2 |
| pyproject_script | 1 (`codexray`) |
| main_guard | 1 (`src/codexray/cli.py`) |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.20s** |
| budget | 5.00s |
| margin | ≈ 25× under budget |

## Observations

1. **올바른 결과** — `pyproject.toml [project.scripts] codexray = "codexray.cli:app"` 검출 + `cli.py`의 `if __name__ == "__main__":` 검출
2. CodeXray는 단일 진입점 라이브러리(typer 앱) → 진입점 2개로 명확
3. 후속 도달성 분석 시작점 — 이 두 entry에서 출발해 `graph` 의 internal 엣지를 따라 도달 가능 모듈 식별 가능

## Environment

- macOS Darwin 25.4.0 (arm64)
- Python 3.14.3 / uv 0.11.7
- CodeXray 0.1.0 (entrypoints 추가본)
