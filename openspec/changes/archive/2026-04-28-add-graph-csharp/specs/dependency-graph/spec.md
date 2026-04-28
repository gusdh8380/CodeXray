## ADDED Requirements

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

## MODIFIED Requirements

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
