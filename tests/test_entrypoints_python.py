from codexray.entrypoints.python_detector import detect_main_guard


def test_canonical_main_guard() -> None:
    src = 'if __name__ == "__main__":\n    print("hi")\n'
    assert detect_main_guard(src) is True


def test_function_scoped_guard_not_detected() -> None:
    src = 'def f():\n    if __name__ == "__main__":\n        pass\n'
    assert detect_main_guard(src) is False


def test_class_scoped_guard_not_detected() -> None:
    src = 'class C:\n    if __name__ == "__main__":\n        x = 1\n'
    assert detect_main_guard(src) is False


def test_inverted_compare_not_detected() -> None:
    src = 'if "__main__" == __name__:\n    pass\n'
    assert detect_main_guard(src) is False


def test_syntax_error_returns_false() -> None:
    src = "def broken(\n"
    assert detect_main_guard(src) is False


def test_no_guard() -> None:
    src = "x = 1\nprint(x)\n"
    assert detect_main_guard(src) is False
