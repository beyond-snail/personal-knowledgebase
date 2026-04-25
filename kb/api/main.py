from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from kb.core.bootstrap import init_store
from kb.core.repository import get_trace, search_items
from kb.core.settings import WEB_DIR

app = FastAPI(title="Personal Knowledgebase", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    init_store()


@app.get("/api/search")
def api_search(q: str = Query(..., min_length=1)):
    return {"query": q, "items": search_items(q)}


@app.get("/api/trace/{item_id}")
def api_trace(item_id: str):
    return get_trace(item_id)


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
