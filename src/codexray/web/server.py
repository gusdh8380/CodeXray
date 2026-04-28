from __future__ import annotations

import threading
import webbrowser
from importlib import resources
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api_v2 import create_v2_router
from .routes import create_router


def _frontend_dist() -> Path | None:
    """Locate frontend/dist relative to repo root if present."""
    candidates = [
        Path(__file__).resolve().parents[3] / "frontend" / "dist",
        Path.cwd() / "frontend" / "dist",
    ]
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "index.html").exists():
            return candidate
    return None


def create_app() -> FastAPI:
    package_root = resources.files("codexray.web")
    template_dir = str(package_root.joinpath("templates"))
    static_dir = Path(str(package_root.joinpath("static")))

    app = FastAPI(title="CodeXray Web UI")
    dist = _frontend_dist()

    # SPA route MUST be registered before the legacy router so its `GET /`
    # matches first and the React shell is served instead of the htmx index.
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
    app.include_router(create_router(Jinja2Templates(directory=template_dir)))
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


def serve(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True) -> None:
    url = f"http://{host}:{port}/"
    if open_browser:
        timer = threading.Timer(0.8, webbrowser.open, args=(url,))
        timer.daemon = True
        timer.start()
    uvicorn.run(create_app(), host=host, port=port)
