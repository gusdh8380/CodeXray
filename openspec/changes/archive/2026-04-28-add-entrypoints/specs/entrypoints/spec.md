## ADDED Requirements

### Requirement: Entrypoints CLI 진입점
The system SHALL expose a `codexray entrypoints <path>` command that prints a JSON object listing detected entrypoints to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray entrypoints <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray entrypoints`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with top-level keys `schema_version` and `entrypoints`. `schema_version` MUST be the integer `1`. `entrypoints` 배열의 각 원소는 `path`(string), `language`(string 또는 null), `kind`(string), `detail`(string) 네 키만 포함한다.

#### Scenario: 스키마 키
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray entrypoints`를 실행하면
- **THEN** 출력 객체는 `schema_version`, `entrypoints` 키를 모두 포함하고 `schema_version`은 정수 `1`이다

#### Scenario: 진입점 객체 형식
- **WHEN** 출력 JSON에 진입점이 포함될 때
- **THEN** 각 객체는 `path`, `language`, `kind`, `detail` 네 키만 포함한다

### Requirement: Python __main__ 가드 식별
The system SHALL detect Python entrypoints by parsing each `.py` file with the standard library `ast` module and recognizing module-level `if __name__ == "__main__":` blocks. `__name__`이 비교의 좌측, `"__main__"` 문자열이 우측인 형태만 1차에서 매칭한다.

#### Scenario: 표준 가드
- **WHEN** Python 파일에 모듈 레벨 `if __name__ == "__main__":` 가 있을 때
- **THEN** 시스템은 그 파일에 대해 `kind: "main_guard"`, `language: "Python"`인 entry를 1개 만든다

#### Scenario: 함수 내부 가드 미인식
- **WHEN** Python 파일이 함수 안에 `if __name__ == "__main__":`를 가질 때
- **THEN** 시스템은 그 파일을 진입점으로 만들지 않는다 (모듈 레벨에서만 매칭)

#### Scenario: 비대칭 비교 미인식
- **WHEN** Python 파일이 `if "__main__" == __name__:` 처럼 좌우가 뒤집힌 가드만 가질 때
- **THEN** 시스템은 1차에서 그 파일을 진입점으로 만들지 않는다

### Requirement: pyproject.toml 스크립트 식별
The system SHALL parse the tree-root `pyproject.toml` (if present) using `tomllib` and emit one entrypoint per key in `[project.scripts]`. `kind`는 `pyproject_script`, `path`는 `"pyproject.toml"`, `language`는 `null`, `detail`은 스크립트 이름이다. 파싱 실패 시 stderr에 1줄 경고 후 항목을 만들지 않는다.

#### Scenario: 단일 스크립트
- **WHEN** 트리 루트 `pyproject.toml`의 `[project.scripts]`가 `codexray = "codexray.cli:app"`를 가질 때
- **THEN** 시스템은 `path: "pyproject.toml"`, `kind: "pyproject_script"`, `detail: "codexray"`, `language: null`인 entry 1개를 만든다

#### Scenario: pyproject 부재
- **WHEN** 트리 루트에 `pyproject.toml`이 없을 때
- **THEN** 시스템은 pyproject 관련 entry를 만들지 않으며 오류로 종료하지 않는다

### Requirement: package.json 매니페스트 식별
The system SHALL parse the tree-root `package.json` (if present) and emit entrypoints for `bin`, `main`, and `scripts` fields. `kind`는 각각 `package_bin`, `package_main`, `package_script`이며 `path`는 `"package.json"`, `language`는 `null`, `detail`은 (bin) 키 이름 또는 단일 string, (main) 파일 경로 문자열, (script) 스크립트 이름이다.

#### Scenario: bin 단일 string
- **WHEN** `package.json`이 `"bin": "./bin/cli.js"`를 가질 때
- **THEN** 시스템은 `kind: "package_bin"`, `detail: "./bin/cli.js"`인 entry를 1개 만든다

#### Scenario: bin 객체
- **WHEN** `package.json`이 `"bin": {"foo": "./foo.js", "bar": "./bar.js"}`를 가질 때
- **THEN** 시스템은 각 키별로 `kind: "package_bin"` entry 2개를 만들고 `detail`은 각각 `"foo"`, `"bar"`다

#### Scenario: scripts
- **WHEN** `package.json`이 `"scripts": {"build": "tsc", "test": "vitest"}`를 가질 때
- **THEN** 시스템은 각 스크립트 이름별 `kind: "package_script"` entry 2개를 만든다

### Requirement: C# Main 메서드 식별
The system SHALL detect `static void Main(...)`, `static int Main(...)`, `static async Task Main(...)`, `static async Task<int> Main(...)` patterns in `.cs` files using a regular expression. `kind: "main_method"`, `language: "C#"`, `detail`은 반환 타입(`void`, `int`, `Task`, `Task<int>`).

#### Scenario: void Main
- **WHEN** C# 파일에 `static void Main(string[] args) {`가 있을 때
- **THEN** 시스템은 그 파일에 대해 `kind: "main_method"`, `detail: "void"`인 entry를 1개 만든다

#### Scenario: async Task<int> Main
- **WHEN** C# 파일에 `public static async Task<int> Main(string[] args)`가 있을 때
- **THEN** 시스템은 그 파일에 대해 `kind: "main_method"`, `detail: "Task<int>"`인 entry를 1개 만든다

### Requirement: Unity MonoBehaviour 라이프사이클 식별
The system SHALL detect Unity entrypoints by matching classes that inherit from `MonoBehaviour` and define one or more lifecycle methods (`Awake`, `OnEnable`, `Start`, `FixedUpdate`, `Update`, `LateUpdate`, `OnDisable`, `OnDestroy`). 한 파일 1 entry로 dedupe하며 `kind: "unity_lifecycle"`, `detail`은 그 파일에서 매칭된 메서드들을 콤마-스페이스 구분 정렬된 문자열로 표기한다.

#### Scenario: MonoBehaviour 클래스 + Update
- **WHEN** C# 파일이 `class Player : MonoBehaviour { void Update() {} }`를 가질 때
- **THEN** 시스템은 그 파일에 대해 `kind: "unity_lifecycle"`, `detail: "Update"`인 entry를 1개 만든다

#### Scenario: 다중 라이프사이클
- **WHEN** C# 파일이 MonoBehaviour 클래스에 `Awake`, `Start`, `Update` 셋을 가질 때
- **THEN** 시스템은 그 파일에 대해 1 entry, `detail: "Awake, Start, Update"`로 만든다 (정렬·콤마-스페이스 구분)

#### Scenario: MonoBehaviour 미상속
- **WHEN** C# 파일이 `class Foo { void Update() {} }` (MonoBehaviour 미상속)을 가질 때
- **THEN** 시스템은 그 파일에 대해 `unity_lifecycle` entry를 만들지 않는다

### Requirement: 결정론적 정렬
The system SHALL sort the `entrypoints` array by `path` ascending; ties broken by `kind` ascending; further ties by `detail` ascending.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 동일한 입력 트리에 대해 `codexray entrypoints`를 두 번 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete entrypoints output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray entrypoints`를 실행하면
- **THEN** 시스템은 5초 이내에 JSON 출력을 완료한다
