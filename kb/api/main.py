from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import Body, FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from kb.core.bootstrap import init_store
from kb.core.repository import get_stats, get_trace, list_projects, search_items, upsert_project
from kb.ingest.event_bridge import append_event
from kb.ingest.importer import ingest_inbox
from kb.core.settings import WEB_DIR

app = FastAPI(title="Personal Knowledgebase", version="0.1.0")
_collector_task: asyncio.Task | None = None
_poll_seconds = 8


@app.on_event("startup")
async def startup() -> None:
    init_store()
    # Register current workspace as a default watched project.
    workspace = WEB_DIR.parent
    upsert_project(workspace.name, str(workspace))
    global _collector_task
    _collector_task = asyncio.create_task(_collector_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    global _collector_task
    if _collector_task is not None:
        _collector_task.cancel()
        try:
            await _collector_task
        except asyncio.CancelledError:
            pass
        _collector_task = None


async def _collector_loop() -> None:
    while True:
        for project in list_projects():
            try:
                ingest_inbox(Path(project["root_path"]))
            except Exception:
                # Keep collector alive even when one project has temporary issues.
                continue
        await asyncio.sleep(_poll_seconds)


@app.get("/api/search")
def api_search(q: str = Query(..., min_length=1)):
    return {"query": q, "items": search_items(q)}


@app.get("/api/trace/{item_id}")
def api_trace(item_id: str):
    return get_trace(item_id)


@app.get("/api/stats")
def api_stats():
    return get_stats()


@app.get("/api/projects")
def api_projects():
    return {"projects": list_projects()}


@app.post("/api/projects/register")
def api_register_project(path: str = Query(..., min_length=1), name: str | None = Query(default=None)):
    root = Path(path).resolve()
    project_id = upsert_project(name or root.name, str(root))
    return {"project_id": project_id, "path": str(root)}


@app.post("/api/ingest/inbox")
def api_ingest_inbox(project: str = Query(..., min_length=1)):
    return ingest_inbox(Path(project))


@app.post("/api/events/push")
def api_events_push(
    project: str = Query(..., min_length=1),
    process_now: bool = Query(default=True),
    event: dict = Body(...),
):
    root = Path(project).resolve()
    upsert_project(root.name, str(root))
    target_file = append_event(root, event)
    processed = None
    if process_now:
        processed = ingest_inbox(root)
    return {"ok": True, "target_file": str(target_file), "processed": processed}


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
