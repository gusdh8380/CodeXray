from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FolderPickerResult:
    path: str | None
    error: str | None = None
    cancelled: bool = False


def choose_folder() -> FolderPickerResult:
    if platform.system() != "Darwin":
        return FolderPickerResult(
            None,
            "Folder picker is currently supported on macOS only.",
        )
    script = 'POSIX path of (choose folder with prompt "Choose a folder to analyze")'
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return FolderPickerResult(None, f"Folder picker failed: {exc}")
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if "User canceled" in stderr or result.returncode == 1:
            return FolderPickerResult(None, cancelled=True)
        return FolderPickerResult(None, f"Folder picker failed: {stderr}")
    path = result.stdout.strip()
    if not path:
        return FolderPickerResult(None, cancelled=True)
    return FolderPickerResult(path)
