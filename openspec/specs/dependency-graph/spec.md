# dependency-graph Specification

## Purpose
TBD - created by archiving change add-dependency-graph. Update Purpose after archive.
## Requirements
### Requirement: 그래프 CLI 진입점
The system SHALL expose a `codexray graph <path>` command that prints a JSON graph to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray graph <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray graph`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with the top-level keys `schema_version`, `nodes`, and `edges`. `schema_version` MUST be the integer `1`. Each node MUST contain `path` (입력 루트 기준 POSIX 상대경로) and `language` (string). Each edge MUST contain `from` (POSIX 상대경로), `to` (POSIX 상대경로 또는 raw 모듈 문자열), and `kind` (`"internal"` 또는 `"external"`).

#### Scenario: 스키마 키
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray graph`를 실행하면
- **THEN** 출력 JSON 객체는 `schema_version`, `nodes`, `edges` 키를 모두 포함하고 `schema_version`은 정수 `1`이다

#### Scenario: 노드 형식
- **WHEN** 출력 JSON에 노드가 포함될 때
- **THEN** 각 노드 객체는 `path`(string)와 `language`(string)만 포함하며, `path`는 입력 루트 기준 POSIX 슬래시 상대경로다

#### Scenario: 엣지 형식
- **WHEN** 출력 JSON에 엣지가 포함될 때
- **THEN** 각 엣지 객체는 `from`(string), `to`(string), `kind`(`"internal"` 또는 `"external"`)만 포함한다

### Requirement: 워킹·언어 분류 재사용
The system SHALL reuse the existing inventory walk/ignore rules and language classification. 그래프 노드는 `inventory` capability가 정의한 1차 매핑(Python, JavaScript, TypeScript, Java, C#) 중 1차 변경 대상 4개 언어(Python, JavaScript, TypeScript, C#) 파일에 한정한다.

#### Scenario: 무시 규칙 일치
- **WHEN** 입력 디렉토리에 `node_modules/`가 존재할 때 `codexray graph`를 실행하면
- **THEN** 시스템은 `node_modules/` 내부 파일을 노드로 만들지 않고 엣지의 `to`로도 해석하지 않는다 (해석 결과가 무시 디렉토리에 떨어지면 `external`로 강등)

#### Scenario: 비대상 언어 파일
- **WHEN** 입력 디렉토리에 Java(`.java`) 파일이 존재할 때 `codexray graph`를 실행하면
- **THEN** 시스템은 해당 파일을 노드로 만들지 않고 엣지의 `from` 또는 internal `to`로 해석하지 않는다

#### Scenario: C# 파일 포함
- **WHEN** 입력 디렉토리에 C#(`.cs`) 파일이 존재할 때 `codexray graph`를 실행하면
- **THEN** 시스템은 해당 파일을 `language: "C#"`인 노드로 만든다

### Requirement: Python import 추출
The system SHALL parse Python source files using the standard library `ast` module and extract `Import` and `ImportFrom` statements. 문법 오류 파일은 노드는 추가하되 엣지를 만들지 않으며 stderr에 1줄 경고를 출력한다.

#### Scenario: 절대 import
- **WHEN** Python 파일에 `import os`, `import json`, `from typing import Any` 가 있을 때
- **THEN** 시스템은 그 파일에서 `os`, `json`, `typing`으로의 엣지 3개를 만들고 (해당 모듈이 트리 내 파일이 아니라면) 모두 `external`로 분류한다

#### Scenario: 상대 import
- **WHEN** `src/codexray/cli.py`에 `from .inventory import aggregate` 가 있고 `src/codexray/inventory.py` 가 트리에 존재할 때
- **THEN** 시스템은 `from`이 `src/codexray/cli.py`이고 `to`가 `src/codexray/inventory.py`인 엣지를 만들고 `kind`는 `"internal"`이다

#### Scenario: 문법 오류 파일
- **WHEN** Python 파일이 `ast.parse`로 파싱 불가능할 때
- **THEN** 시스템은 해당 파일을 노드로 추가하되 엣지는 만들지 않고 stderr에 경고 1줄을 출력한다

### Requirement: JavaScript/TypeScript import 추출
The system SHALL extract import/require/dynamic-import statements from `.js`/`.jsx`/`.mjs`/`.cjs`/`.ts`/`.tsx` files using regular expressions over the file text. 추출 대상 패턴은 `import ... from "X"`, `import "X"`, `import("X")` (정적 문자열 인수), `require("X")` (정적 문자열 인수)다. 따옴표는 `"`, `'`, `` ` `` 모두 허용한다.

#### Scenario: ES module import
- **WHEN** TS 파일에 `import { foo } from "./util";` 가 있고 `util.ts`가 같은 디렉토리에 존재할 때
- **THEN** 시스템은 해당 파일에서 `util.ts`로의 internal 엣지를 만든다

#### Scenario: bare specifier
- **WHEN** JS 파일에 `import React from "react";` 가 있을 때
- **THEN** 시스템은 `to`가 `"react"`이고 `kind`가 `"external"`인 엣지를 만든다

#### Scenario: dynamic import 정적 인수
- **WHEN** TS 파일에 `await import("./lazy")` 가 있고 `lazy.ts`가 같은 디렉토리에 존재할 때
- **THEN** 시스템은 internal 엣지를 만든다

#### Scenario: dynamic import 변수 인수
- **WHEN** TS 파일에 `const m = name; await import(m)` 처럼 변수 인수 dynamic import만 있을 때
- **THEN** 시스템은 해당 import에 대해 엣지를 만들지 않는다

### Requirement: 모듈 → 파일 해석
The system SHALL attempt to resolve each extracted import to a file inside the input tree. 해석 결과가 트리 내 분석 대상 파일이면 `kind: "internal"`로, 아니면 `kind: "external"`로 분류하며, external의 경우 `to`는 코드에 적힌 raw 모듈 문자열을 그대로 사용한다. JS/TS 해석은 상대 경로(`./`, `../`)에 한정하며 확장자 후보(`.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`)와 `index.*` 디렉토리 진입을 시도한다. Python 해석은 절대 import에 대해 입력 루트 및 `src/` 기준 모듈 경로를 시도하고, 상대 import는 `level` 만큼 부모 디렉토리를 거슬러 해석한다.

#### Scenario: 확장자 자동 추정
- **WHEN** TS 파일에 `import x from "./util"` 가 있고 트리에 `util.ts`만 존재할 때
- **THEN** 시스템은 `./util` 을 `util.ts`로 해석해 internal 엣지를 만든다

#### Scenario: index 디렉토리
- **WHEN** TS 파일에 `import x from "./mod"` 가 있고 트리에 `mod/index.ts`가 존재할 때
- **THEN** 시스템은 `./mod`를 `mod/index.ts`로 해석해 internal 엣지를 만든다

#### Scenario: 해석 실패
- **WHEN** TS 파일에 `import x from "./missing"` 가 있고 어떤 확장자 후보로도 파일이 없을 때
- **THEN** 시스템은 `to`가 raw 문자열 `"./missing"`이고 `kind`가 `"external"`인 엣지를 만든다

#### Scenario: 해석 결과가 무시 디렉토리
- **WHEN** import의 해석 결과가 `node_modules/` 같은 무시 디렉토리에 떨어질 때
- **THEN** 시스템은 해당 엣지를 internal로 만들지 않고 external로 강등한다

### Requirement: 결정론적 정렬
The system SHALL sort nodes and edges deterministically. `nodes`는 `path` 사전순 오름차순. `edges`는 `from` 사전순, 같으면 `to` 사전순, 같으면 `kind` 사전순.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 동일한 입력 트리에 대해 `codexray graph`를 두 번 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete graph output within 5 seconds on the validation codebase (CodeXray repo 자체 또는 그에 준하는 수천 파일 이하 Python/JS/TS 트리).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray graph`를 실행하면
- **THEN** 시스템은 5초 이내에 JSON 출력을 완료한다

### Requirement: C# using 추출
The system SHALL extract `using` statements from `.cs` files using regular expressions. 추출 대상은 `using X.Y.Z;`와 `using static X.Y.Type;`의 두 형태이며, 라인 시작 위치(앞에 공백만 허용)에서 매칭되어야 한다. alias 형식(`using A = X.Y;`)과 `global using`은 1차에서 추출하지 않으며 향후 변경의 대상이다.

#### Scenario: 단순 using
- **WHEN** C# 파일에 `using System;` 와 `using System.Collections.Generic;` 가 있을 때
- **THEN** 시스템은 두 namespace 문자열(`System`, `System.Collections.Generic`)을 추출한다

#### Scenario: using static
- **WHEN** C# 파일에 `using static System.Math;` 가 있을 때
- **THEN** 시스템은 namespace 문자열 `System.Math`를 추출한다

#### Scenario: alias 미추출
- **WHEN** C# 파일에 `using G = System.Collections.Generic;` 만 있을 때
- **THEN** 시스템은 해당 라인에서 namespace를 추출하지 않는다

#### Scenario: global using 미추출
- **WHEN** C# 파일에 `global using System;` 가 있을 때
- **THEN** 시스템은 해당 라인에서 namespace를 추출하지 않는다 (1차 비대상)

### Requirement: C# namespace 인덱스 해석
The system SHALL build a namespace-to-files index by scanning every C# file in the input tree once and recording each declared namespace. 한 `using X.Y;`가 인덱스에서 정확히 일치하는 namespace를 찾으면 그 namespace에 속한 모든 파일로 internal 엣지를 만든다 (1:N 허용). 정확 일치 실패 시 entire raw 문자열을 `to`로 하는 external 엣지 1개를 만든다.

#### Scenario: namespace 정확 일치 internal
- **WHEN** 트리에 `Foo.cs` 가 `namespace App.Core { ... }`을 선언하고, `Bar.cs`가 `using App.Core;`를 가질 때
- **THEN** 시스템은 `from`이 `Bar.cs`이고 `to`가 `Foo.cs`인 internal 엣지를 만든다

#### Scenario: 1:N 엣지
- **WHEN** 트리에 `A.cs`와 `B.cs`가 모두 `namespace App.Core { ... }`을 선언하고, `Main.cs`가 `using App.Core;`를 가질 때
- **THEN** 시스템은 `from`이 `Main.cs`인 internal 엣지를 `to=A.cs`, `to=B.cs` 두 개 만든다

#### Scenario: 파일 스코프 namespace
- **WHEN** 트리의 `Foo.cs` 첫 줄(코드)이 `namespace App.Core;` (C# 10 file-scoped)이고, `Bar.cs`가 `using App.Core;`를 가질 때
- **THEN** 시스템은 `from=Bar.cs`, `to=Foo.cs`, `kind=internal`인 엣지를 만든다

#### Scenario: 인덱스에 없는 namespace
- **WHEN** C# 파일에 `using UnityEngine;` 가 있고 트리 어떤 `.cs` 파일도 `namespace UnityEngine`을 선언하지 않을 때
- **THEN** 시스템은 `to`가 `"UnityEngine"`이고 `kind`가 `"external"`인 엣지를 만든다

#### Scenario: 글로벌 namespace 파일
- **WHEN** 트리의 `Free.cs`가 namespace 선언 없이 클래스를 가질 때
- **THEN** 시스템은 `Free.cs`를 internal target으로 매핑하지 않는다 (어떤 `using`도 매칭되지 않음)

