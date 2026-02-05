from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.memory import router as memory_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title=settings.app_name)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(memory_router)

web_dir = Path(__file__).resolve().parent / "web"
app.mount("/static", StaticFiles(directory=web_dir), name="static")


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    index_path = web_dir / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))
