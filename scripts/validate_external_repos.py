"""Run CodeXray's deterministic vibe-insights pipeline over a list of repos.

본 스크립트는 임계값·신호 풀의 외부 검증 (`non-roboco-validation` change) 을 위한
*결정론* 데이터 수집기다. AI 호출(narrative / 카드 합성) 은 의도적으로 차단되어
같은 입력에서 항상 같은 출력을 내야 한다.

사용법:
    uv run python scripts/validate_external_repos.py \
        ~/Project/external/fastapi \
        ~/Project/external/OpenSpec \
        ...

또는 텍스트 파일에 한 줄당 한 경로:
    uv run python scripts/validate_external_repos.py --from-file paths.txt

출력:
    docs/validation/non-roboco-data/{repo-name}.json — 결정론 vibe_insights payload
    + 콘솔 요약 표.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Allow running from repo root without install.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from codexray.briefing.git_history import build_git_history  # noqa: E402
from codexray.hotspots import build_hotspots  # noqa: E402
from codexray.quality import build_quality  # noqa: E402
from codexray.vibe import build_vibe_coding_report  # noqa: E402
from codexray.vibe_insights import build_vibe_insights  # noqa: E402

_OUTPUT_DIR = _REPO_ROOT / "docs" / "validation" / "non-roboco-data"


def collect_one(repo: Path) -> dict[str, Any]:
    """Return the deterministic vibe_insights payload for `repo`.

    AI 호출은 하지 않는다 — `ai_key_insight=None` 이라 narrative 는 fallback 사용.
    비감지 시 `build_vibe_insights` 가 None 을 반환하므로, 검증 데이터 파일이
    항상 의미 있는 정보를 담도록 ``{"detected": False}`` 로 wrap 한다.
    """
    resolved = repo.resolve()
    vibe = build_vibe_coding_report(resolved)
    quality = build_quality(resolved)
    hotspots = build_hotspots(resolved)
    history = build_git_history(resolved)
    payload = build_vibe_insights(
        root=resolved,
        vibe=vibe,
        quality=quality,
        hotspots=hotspots,
        history=history,
        ai_key_insight=None,
    )
    return payload if payload is not None else {"detected": False}


def summarize_axis(axis: dict[str, Any]) -> str:
    return (
        f"{axis['label']:<8} {axis['state']:<9} "
        f"{axis['signal_count']}/{axis['signal_pool_size']} "
        f"({axis['signal_ratio'] * 100:.0f}%)"
    )


def write_payload(repo_name: str, payload: dict[str, Any], output_dir: Path) -> Path:
    out_path = output_dir / f"{repo_name}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="레포 경로들")
    parser.add_argument(
        "--from-file",
        type=Path,
        default=None,
        help="한 줄당 한 경로가 적힌 텍스트 파일",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_OUTPUT_DIR,
        help=f"JSON 출력 디렉토리 (기본: {_OUTPUT_DIR.relative_to(_REPO_ROOT)})",
    )
    args = parser.parse_args(argv)

    paths: list[Path] = list(args.paths)
    if args.from_file:
        for line in args.from_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                paths.append(Path(stripped).expanduser())

    if not paths:
        parser.error("최소 한 개의 레포 경로가 필요합니다.")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"# Non-ROBOCO 외부 검증 — {len(paths)}개 레포")
    print(f"# 출력 디렉토리: {output_dir}")
    print()

    failures: list[tuple[str, Exception]] = []
    for repo in paths:
        repo = repo.expanduser().resolve()
        if not repo.exists():
            print(f"[SKIP] {repo} — 경로 없음")
            failures.append((str(repo), FileNotFoundError(str(repo))))
            continue

        name = repo.name or "root"
        start = time.perf_counter()
        try:
            payload = collect_one(repo)
        except Exception as exc:  # noqa: BLE001 — 분석 실패도 기록 대상
            elapsed = time.perf_counter() - start
            print(f"[FAIL] {name:<32} ({elapsed:.1f}s) — {type(exc).__name__}: {exc}")
            failures.append((name, exc))
            continue

        out_path = write_payload(name, payload, output_dir)
        elapsed = time.perf_counter() - start

        if payload.get("detected"):
            axes = payload.get("axes", [])
            axis_summary = " | ".join(summarize_axis(a) for a in axes)
            print(f"[OK]   {name:<32} ({elapsed:.1f}s) detected → {axis_summary}")
        else:
            print(
                f"[OK]   {name:<32} ({elapsed:.1f}s) "
                "not-detected → vibe insights 섹션 비노출"
            )
        try:
            display_path = out_path.relative_to(_REPO_ROOT)
        except ValueError:
            display_path = out_path
        print(f"       → {display_path}")

    print()
    if failures:
        print(f"# 실패 {len(failures)}건:")
        for name, exc in failures:
            print(f"  - {name}: {type(exc).__name__}: {exc}")
        return 1

    print(f"# 완료 — JSON {len(paths) - len(failures)}개 생성")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
