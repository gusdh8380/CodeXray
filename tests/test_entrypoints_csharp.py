from codexray.entrypoints.csharp_detector import detect_main_method
from codexray.entrypoints.unity_detector import detect_unity_lifecycle


def test_void_main() -> None:
    src = "class P { static void Main(string[] args) {} }"
    assert detect_main_method(src) == "void"


def test_int_main() -> None:
    src = "public static int Main() { return 0; }"
    assert detect_main_method(src) == "int"


def test_async_task_main() -> None:
    src = "static async Task Main(string[] args) { }"
    assert detect_main_method(src) == "Task"


def test_async_task_int_main() -> None:
    src = "public static async Task<int> Main(string[] args) { return 0; }"
    assert detect_main_method(src) == "Task<int>"


def test_no_main() -> None:
    src = "class P { void NotMain() {} }"
    assert detect_main_method(src) is None


def test_unity_class_with_update() -> None:
    src = "class Player : MonoBehaviour { void Update() {} }"
    assert detect_unity_lifecycle(src) == ["Update"]


def test_unity_multiple_lifecycle_methods_sorted() -> None:
    src = """
    class Player : MonoBehaviour {
        void Update() {}
        void Awake() {}
        void Start() {}
    }
    """
    assert detect_unity_lifecycle(src) == ["Awake", "Start", "Update"]


def test_no_monobehaviour_no_match() -> None:
    src = "class Foo { void Update() {} }"
    assert detect_unity_lifecycle(src) == []


def test_monobehaviour_with_interface() -> None:
    src = "class Player : MonoBehaviour, IDisposable { void OnEnable() {} }"
    assert detect_unity_lifecycle(src) == ["OnEnable"]


def test_monobehaviour_no_lifecycle() -> None:
    src = "class Foo : MonoBehaviour { void Custom() {} }"
    assert detect_unity_lifecycle(src) == []
