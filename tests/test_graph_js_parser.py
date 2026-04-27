from pathlib import Path

from codexray.graph.js_parser import extract_imports


def _raws(imports) -> set[str]:
    return {i.raw for i in imports}


def test_es_import_with_from() -> None:
    src = """
    import { foo } from "./util";
    import x from '../lib/x';
    import * as N from `react`;
    import type { Y } from "./types";
    """
    raws = _raws(extract_imports(src, Path("a.ts"), "TypeScript"))
    assert raws == {"./util", "../lib/x", "react", "./types"}


def test_side_effect_import() -> None:
    src = 'import "./styles.css";\nimport "polyfill";\n'
    raws = _raws(extract_imports(src, Path("a.ts"), "TypeScript"))
    assert raws == {"./styles.css", "polyfill"}


def test_require() -> None:
    src = 'const x = require("./util");\nconst y = require("react");\n'
    raws = _raws(extract_imports(src, Path("a.js"), "JavaScript"))
    assert raws == {"./util", "react"}


def test_dynamic_import_static_arg() -> None:
    src = 'await import("./lazy");\nconst m = await import(`./other`);\n'
    raws = _raws(extract_imports(src, Path("a.ts"), "TypeScript"))
    assert raws == {"./lazy", "./other"}


def test_dynamic_import_variable_arg_skipped() -> None:
    src = 'const name = "x"; await import(name);\n'
    raws = _raws(extract_imports(src, Path("a.ts"), "TypeScript"))
    assert raws == set()


def test_no_duplicates_per_pattern() -> None:
    src = 'import a from "./x";\nimport b from "./x";\n'
    raws = _raws(extract_imports(src, Path("a.ts"), "TypeScript"))
    assert raws == {"./x"}
