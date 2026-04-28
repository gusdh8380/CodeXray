## Why

지금까지 만든 그래프·메트릭은 "어떤 의존이 있는가"는 보여주지만 "어디서부터 실행이 시작되는가"는 모른다. 진입점을 식별해야 도달성·죽은 코드·핫스팟 가중치(자주 변경되고 진입점에서 도달 가능한 모듈을 우선)가 의미를 갖는다. 1차는 정적 텍스트만 — AI 비의존, 결정론적, 회귀 검증 쉬움. CivilSim은 Unity라 `Main` 메서드 대신 MonoBehaviour 라이프사이클이 진입점이므로 함께 다룬다.

## What Changes

- 새 CLI 진입점: `codexray entrypoints <path>` — 같은 워킹/무시 규칙 위에 진입점 휴리스틱 적용, JSON 1개 출력
- 출력 스키마 (스키마 v1):
  ```json
  {
    "schema_version": 1,
    "entrypoints": [
      {"path": "src/codexray/cli.py", "language": "Python", "kind": "main_guard", "detail": ""},
      {"path": "pyproject.toml", "language": null, "kind": "pyproject_script", "detail": "codexray"},
      {"path": "package.json", "language": null, "kind": "package_bin", "detail": "codexray"},
      {"path": "Assets/Scripts/Main.cs", "language": "C#", "kind": "main_method", "detail": "void"},
      {"path": "Assets/Scripts/Player.cs", "language": "C#", "kind": "unity_lifecycle", "detail": "Awake, Start, Update"}
    ]
  }
  ```
- 식별 규칙:
  - **Python**: AST로 `if __name__ == "__main__":` 정확 매칭 → `kind: "main_guard"`
  - **`pyproject.toml`**: `[project.scripts]` 각 항목 → `kind: "pyproject_script"`, detail은 entry 이름
  - **`package.json`**: `bin` 항목(string 또는 dict) → `kind: "package_bin"`, `main` → `kind: "package_main"`, `scripts.*` → `kind: "package_script"` (npm script 이름)
  - **C# Main 메서드**: 정규식 — `static\s+(async\s+)?(void|int|Task(<\s*int\s*>)?)\s+Main\s*\(` → `kind: "main_method"`, detail은 반환 타입
  - **Unity 라이프사이클**: `: MonoBehaviour` 상속 + 라이프사이클 메서드(`Awake`, `OnEnable`, `Start`, `FixedUpdate`, `Update`, `LateUpdate`, `OnDisable`, `OnDestroy`) 중 1개 이상 → `kind: "unity_lifecycle"`, detail은 매칭된 메서드들 콤마 join (한 파일 1 entry, 메서드별로 entry 폭증 방지)
- 결정론 정렬: `path` 사전순, 같으면 `kind` 사전순
- `inventory`/`graph`/`metrics` 명령은 변경 없음

## Capabilities

### New Capabilities
- `entrypoints`: 트리 내 정적 진입점(언어 키워드 + 패키지 메타데이터)을 식별해 JSON으로 노출하는 능력. 후속 변경(도달성 분석, 죽은 코드 후보, 핫스팟 가중치)이 입력으로 사용한다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/entrypoints/` 서브패키지
  - `entrypoints/python_detector.py`, `entrypoints/csharp_detector.py`, `entrypoints/unity_detector.py`, `entrypoints/manifest_detector.py` (pyproject + package.json), `entrypoints/build.py`, `entrypoints/serialize.py`, `entrypoints/types.py`
- 신규 의존성 없음 — Python `ast` + `tomllib`(3.11+ stdlib) + `json` + 정규식
- CLI에 `entrypoints` 서브커맨드 추가
- 검증: CodeXray 자기(`pyproject.toml [project.scripts] codexray` + `__main__` 가드 검출), CivilSim(MonoBehaviour 라이프사이클 다수 검출), 5초 내
