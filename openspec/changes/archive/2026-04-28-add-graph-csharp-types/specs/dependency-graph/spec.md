## ADDED Requirements

### Requirement: C# type 사용 추출
The system SHALL extract a set of PascalCase type tokens used in each `.cs` file. 추출 전 문자열 리터럴(큰따옴표/작은따옴표), 라인 주석(`//`), 블록 주석(`/* */`)을 제거한 뒤 `\b[A-Z]\w*\b`에 매칭되는 모든 토큰을 set으로 모은다.

#### Scenario: PascalCase 토큰 매칭
- **WHEN** C# 파일에 `var b = new Building();`이 있을 때
- **THEN** 시스템은 `Building`을 사용된 type 토큰으로 추출한다

#### Scenario: 문자열 안 토큰 무시
- **WHEN** C# 파일에 `var s = "Building name";`만 있을 때
- **THEN** 시스템은 `Building`을 사용된 type 토큰으로 추출하지 않는다 (문자열 안 토큰 제거)

#### Scenario: 주석 안 토큰 무시
- **WHEN** C# 파일에 `// uses Building` 만 있을 때
- **THEN** 시스템은 `Building`을 사용된 type 토큰으로 추출하지 않는다

### Requirement: C# implicit own-namespace 스코프
The system SHALL treat type usages within a file's own declared namespace(s) as resolvable to files in those namespace(s) without requiring an explicit `using` directive.

#### Scenario: 같은 namespace 안 type 사용
- **WHEN** `Foo.cs`가 `namespace App.Core { class Foo { void M() { var b = new Building(); } } }`이고 트리의 `Building.cs`가 `namespace App.Core { class Building {} }`일 때
- **THEN** 시스템은 `Foo.cs`에 `using App.Core;`가 없어도 `Foo.cs → Building.cs`인 internal 엣지를 만든다

## MODIFIED Requirements

### Requirement: C# namespace 인덱스 해석
The system SHALL resolve C# `using N;` directives by combining a namespace-to-files index with a `(namespace, type_name)`-to-file index built from a single tree scan. 한 파일이 `using N;`을 가질 때 시스템은 그 파일에서 추출한 type 사용 토큰들 중 `(N, token)`이 type 인덱스에 존재하는 것들에 한해 그 파일들로 internal 엣지를 만든다 (자기 자신 제외, 1:N 가능). `N`이 namespace 인덱스에 없으면 raw 문자열을 `to`로 하는 external 엣지를 만든다. `N`이 인덱스에 있지만 그 namespace 안 어떤 type도 사용되지 않으면 엣지를 만들지 않는다.

#### Scenario: namespace 정확 일치 + type 사용 internal
- **WHEN** 트리에 `Foo.cs`가 `namespace App.Core { class Foo {} }`을 선언하고, `Bar.cs`가 `using App.Core;` + `var f = new Foo();`을 가질 때
- **THEN** 시스템은 `from`이 `Bar.cs`이고 `to`가 `Foo.cs`인 internal 엣지를 만든다

#### Scenario: 사용된 type만 1:N
- **WHEN** 트리의 `A.cs`가 `namespace App.Core { class A {} }`, `B.cs`가 `namespace App.Core { class B {} }`이고 `Main.cs`가 `using App.Core;` + `var a = new A(); var b = new B();`을 가질 때
- **THEN** 시스템은 `Main.cs`에서 `A.cs`와 `B.cs`로 internal 엣지 2개를 만든다

#### Scenario: 사용되지 않는 type 매핑 안 함
- **WHEN** 트리의 `A.cs`가 `namespace App.Core { class A {} }`, `B.cs`가 `namespace App.Core { class B {} }`이고 `Main.cs`가 `using App.Core;` + `var a = new A();`만 가질 때
- **THEN** 시스템은 `Main.cs`에서 `A.cs`로만 internal 엣지를 만들고 `B.cs`로는 엣지를 만들지 않는다

#### Scenario: 사용 type 0개일 때 엣지 없음
- **WHEN** 트리의 `Foo.cs`가 `namespace App.Core { class Foo {} }`을 선언하고 `Bar.cs`가 `using App.Core;`만 있고 App.Core 안 어떤 type도 사용하지 않을 때
- **THEN** 시스템은 `Bar.cs`에서 `App.Core` 또는 `Foo.cs`로 어떤 엣지도 만들지 않는다

#### Scenario: 파일 스코프 namespace
- **WHEN** 트리의 `Foo.cs` 첫 줄이 `namespace App.Core;`이고 `class Foo {}`을 가지고, `Bar.cs`가 `using App.Core;` + `Foo`를 type으로 사용할 때
- **THEN** 시스템은 `from=Bar.cs`, `to=Foo.cs`, `kind=internal`인 엣지를 만든다

#### Scenario: 인덱스에 없는 namespace
- **WHEN** C# 파일에 `using UnityEngine;` 가 있고 트리 어떤 `.cs` 파일도 `namespace UnityEngine`을 선언하지 않을 때
- **THEN** 시스템은 `to`가 `"UnityEngine"`이고 `kind`가 `"external"`인 엣지를 만든다

#### Scenario: 글로벌 namespace 파일
- **WHEN** 트리의 `Free.cs`가 namespace 선언 없이 클래스를 가질 때
- **THEN** 시스템은 `Free.cs`를 internal target으로 매핑하지 않는다 (어떤 `using`으로도 매칭되지 않음)
