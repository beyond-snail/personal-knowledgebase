from __future__ import annotations

from pathlib import Path

from kb.core.repository import upsert_item, upsert_project
from .collect_projects import collect_markdown_files
from .normalize import normalize_markdown


def ingest_project(project_root: Path) -> dict:
    project_root = project_root.resolve()
    project_id = upsert_project(project_root.name, str(project_root))
    files = collect_markdown_files(project_root)
    imported = 0
    for path in files:
        title, content = normalize_markdown(path)
        upsert_item(project_id, "markdown", title, content, str(path))
        imported += 1
    return {"project_id": project_id, "project": str(project_root), "imported": imported}
