from __future__ import annotations

import threading
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api_v2 import create_v2_router


def _frontend_dist() -> Path | None:
    """Locate frontend dist directory.

    Two scenarios:
    - 개발 환경 (git checkout): repo root 의 `frontend/dist`
    - PyPI 설치: 패키지 안 `codexray/_frontend` (hatchling force-include)
    """
    package_root = Path(__file__).resolve().parent.parent  # codexray/
    candidates = [
        package_root / "_frontend",  # PyPI 설치본
        Path(__file__).resolve().parents[3] / "frontend" / "dist",  # 개발용
        Path.cwd() / "frontend" / "dist",
    ]
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "index.html").exists():
            return candidate
    return None


def create_app() -> FastAPI:
    app = FastAPI(title="CodeXray Web UI")
    dist = _frontend_dist()

    if dist is not None:

        @app.get("/", include_in_schema=False)
        async def spa_index() -> FileResponse:
            return FileResponse(dist / "index.html")

        app.mount(
            "/assets",
            StaticFiles(directory=dist / "assets"),
            name="frontend-assets",
        )

    app.include_router(create_v2_router())
    return app


def serve(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True) -> None:
    url = f"http://{host}:{port}/"
    if open_browser:
        timer = threading.Timer(0.8, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    uvicorn.run(create_app(), host=host, port=port)
