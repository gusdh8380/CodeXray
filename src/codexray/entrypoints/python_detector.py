from __future__ import annotations

import ast


def detect_main_guard(source_code: str) -> bool:
    """Return True if the module has a top-level ``if __name__ == "__main__":``.

    Only matches the canonical asymmetric form (``__name__`` on the left,
    ``"__main__"`` on the right). Function- and class-scoped guards do not
    count.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return False
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        if _is_main_compare(node.test):
            return True
    return False


def _is_main_compare(test: ast.expr) -> bool:
    if not isinstance(test, ast.Compare):
        return False
    if not (
        isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
    ):
        return False
    if len(test.ops) != 1 or not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    right = test.comparators[0]
    return isinstance(right, ast.Constant) and right.value == "__main__"
