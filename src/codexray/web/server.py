from __future__ import annotations

import threading
import webbrowser
from importlib import resources
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import create_router


def create_app() -> FastAPI:
    package_root = resources.files("codexray.web")
    template_dir = str(package_root.joinpath("templates"))
    static_dir = Path(str(package_root.joinpath("static")))

    app = FastAPI(title="CodeXray Web UI")
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
