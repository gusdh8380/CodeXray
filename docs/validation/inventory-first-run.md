# Inventory CLI — 1차 검증

**Change:** `add-inventory-cli`
**Run date:** 2026-04-27 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim` (사용자 본인 작은 게임 프로젝트, Unity C# 기반)

## Result

```
$ uv run codexray inventory /Users/jeonhyeono/Project/personal/CivilSim
┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ language ┃ file_count ┃  loc ┃ last_modified_at          ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ C#       │         53 │ 8878 │ 2026-03-05T17:55:20+09:00 │
└──────────┴────────────┴──────┴───────────────────────────┘
```

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.52s** |
| user | 0.34s |
| sys  | 0.06s |
| budget | 5.00s |
| margin | ≈ 9.6× under budget |

## Tree size

- 총 파일 수(walk 전): 51,063
- 분석 대상 (Default + `.gitignore` 적용 후): C# 소스 53
- `.gitignore`가 `[Ll]ibrary/`, `[Oo]bj/`, `[Bb]uild/`, `[Bb]uilds/`, `[Tt]emp/`, `[Ll]ogs/`, `*.csproj`, `*.sln` 등을 막아 unity 산출물·IDE 메타파일이 정확히 배제됨.

## Environment

- macOS Darwin 25.4.0 (arm64)
- Python 3.14.3 (uv 0.11.7로 격리)
- CodeXray 0.1.0
- 의존성: typer 0.25.0 / rich 15.0.0 / pathspec 1.1.1

## Observations

1. **5초 게이트 통과** — Unity 트리(50k+ 파일)에서도 단일 패스 walk + `pathspec` 필터로 0.52초. 멀티프로세싱 도입 보류 결정 유효.
2. **`.gitignore` 신뢰성** — 직접 구현이었다면 Unity의 `[Cc]ase` 패턴 처리에서 막혔을 것. `pathspec` 채택(Decision 3)이 검증됨.
3. **언어 커버리지 한계** — Unity 프로젝트가 C# 단일 행이라 다국어 정렬 동작은 이번 검증에선 노출되지 않음. 통합 테스트(`tests/test_cli.py`)에서 Python+TypeScript 혼합으로 보완 중.
4. **MVP 첫 단추 통과** — 게임 프로젝트에서 의미 있는 1행 출력. 구조 분석 파이프라인의 입력 단계 확정.

## Next

- `add-dependency-graph`: 같은 walk + classify 파이프라인 위에 import/using 추출.
- 후속 변경에서 검토할 사항:
  - 다국어 검증 케이스로 별도 다국어 샘플 레포 추가
  - Unity 메타파일(`.meta`)을 unknown으로 두는 현재 동작이 적절한지 (현 정책: 매핑 없으면 집계 제외 — 1차 결정 유지)
