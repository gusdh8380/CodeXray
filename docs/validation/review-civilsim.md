{
  "schema_version": 1,
  "backend": "codex",
  "files_reviewed": 1,
  "skipped": [],
  "reviews": [
    {
      "path": "Assets/Scripts/Core/GameManager.cs",
      "dimensions": {
        "readability": {
          "score": 78,
          "evidence_lines": [
            11,
            21,
            59,
            102,
            144
          ],
          "comment": "헤더/주석으로 역할 구분이 잘 되어 있고 공개 접근자 이름도 의도가 비교적 명확합니다. 다만 `AutoDiscoverSystems`와 `ValidateSystems`의 장문 반복 분기 때문에 핵심 흐름을 한눈에 파악하기 어렵습니다.",
          "suggestion": "반복되는 null-check/로그 패턴을 공통 헬퍼나 테이블 기반 처리로 추출해 메서드 길이를 줄이세요. 접근자/필드 네이밍 정렬 규칙을 통일하면 스캔 속도가 더 좋아집니다."
        },
        "design": {
          "score": 57,
          "evidence_lines": [
            16,
            19,
            21,
            60,
            102,
            122
          ],
          "comment": "싱글턴 + 다수 서브시스템 직접 노출 구조는 사용성은 높지만 결합도를 크게 올리는 서비스 로케이터 형태입니다. 런타임 자동 탐색/자동 추가까지 포함되어 의존성 경계가 불명확해집니다.",
          "suggestion": "도메인별 파사드(예: 건설/인구/인프라)로 분리하고 `GameManager`는 조립 역할로 축소하세요. 필수 의존성은 명시적 주입(Inspector 강제 또는 부트스트랩)으로 전환해 설계 의도를 드러내는 편이 좋습니다."
        },
        "maintainability": {
          "score": 51,
          "evidence_lines": [
            23,
            60,
            104,
            146,
            168
          ],
          "comment": "동일 시스템 목록이 필드/프로퍼티/자동탐색/검증 로직에 중복되어 있어 변경 시 수정 지점이 많습니다. 일부 시스템만 `AddComponent`로 보정하는 정책도 산발적으로 섞여 유지보수 규칙이 일관되지 않습니다.",
          "suggestion": "시스템 메타데이터(필수/선택, 탐색 가능 여부, 자동 추가 허용 여부)를 한곳에 선언하고 그 선언으로 탐색/검증을 공통 처리하세요. 정책 차이는 enum/설정값으로 표현해 신규 시스템 추가 시 누락 가능성을 줄이세요."
        },
        "risk": {
          "score": 43,
          "evidence_lines": [
            91,
            93,
            104,
            122,
            137,
            168
          ],
          "comment": "`FindFirstObjectByType`는 씬에 동일 타입이 여러 개일 때 비결정적 연결 위험이 있고, `AddComponent` 자동 보정은 초기화 순서/상태 불일치 문제를 숨길 수 있습니다. `OnDestroy`에서 전역 버스를 즉시 `Clear`하는 동작과 편의 메서드의 null-조건 호출은 장애를 조용히 은닉할 가능성이 있습니다.",
          "suggestion": "필수 시스템 누락 시 조기 실패(명시적 에러 후 비활성화)로 전환하고, 자동 생성은 개발 모드에서만 허용하는 가드가 필요합니다. 이벤트 버스 수명주기와 초기화 순서를 명시하고 다중 인스턴스/씬 전환 케이스 테스트를 추가하세요."
        }
      },
      "confidence": "medium",
      "limitations": "단일 파일만 보았고 실제 씬 구성, 호출자, 실행 순서(다른 MonoBehaviour의 Awake/Start), 테스트 코드 여부를 확인하지 못했습니다. 따라서 런타임 리스크 평가는 잠재 위험 중심이며 실제 재현 가능성은 프로젝트 맥락에 따라 달라질 수 있습니다."
    }
  ]
}
