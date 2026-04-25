from __future__ import annotations

import json
import re
from pathlib import Path

from kb.core.repository import create_link, find_item_ids_by_token, upsert_item, upsert_project
from .collect_projects import collect_markdown_files
from .normalize import normalize_markdown

REQ_RE = re.compile(r"(REQ-\d{4}-\d{2}-\d{2}-\d+)")
TASK_RE = re.compile(r"(TASK-\d{4}-\d{2}-\d{2}-\d+)")


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


def _event_tokens(raw: str) -> tuple[list[str], list[str]]:
    return REQ_RE.findall(raw), TASK_RE.findall(raw)


def ingest_inbox(project_root: Path) -> dict:
    project_root = project_root.resolve()
    project_id = upsert_project(project_root.name, str(project_root))
    inbox_candidates = [
        project_root / "knowledge-store" / "inbox",
        project_root / ".ai" / "runtime" / "inbox",
    ]
    inbox_dirs = [p for p in inbox_candidates if p.exists()]
    if not inbox_dirs:
        return {"project_id": project_id, "project": str(project_root), "events": 0, "processed_files": 0}

    events = 0
    processed_files = 0
    for inbox_dir in inbox_dirs:
        for jsonl in sorted(inbox_dir.glob("*.jsonl")):
            moved_lines: list[str] = []
            for line in jsonl.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                summary = str(payload.get("summary") or payload.get("message") or "workflow event")
                event_type = str(payload.get("event_type") or payload.get("type") or "event")
                req_id = str(payload.get("req_id") or payload.get("requirement_id") or "")
                task_id = str(payload.get("task_id") or "")
                title_parts = [event_type]
                if req_id:
                    title_parts.append(req_id)
                if task_id:
                    title_parts.append(task_id)
                title = " | ".join(title_parts)
                content = json.dumps(payload, ensure_ascii=False, indent=2)
                source_path = str(payload.get("source_path") or jsonl)
                event_item_id = upsert_item(project_id, "event", title, f"{summary}\n\n{content}", source_path)

                tokens_req, tokens_task = _event_tokens(f"{content}\n{summary}\n{req_id}\n{task_id}")
                for token in tokens_req:
                    for target_id in find_item_ids_by_token(project_id, token):
                        create_link(event_item_id, target_id, "references_req")
                for token in tokens_task:
                    for target_id in find_item_ids_by_token(project_id, token):
                        create_link(event_item_id, target_id, "references_task")
                events += 1
                moved_lines.append(line)

            if moved_lines:
                processed_files += 1
                done_file = jsonl.with_suffix(".done")
                done_file.write_text("\n".join(moved_lines) + "\n", encoding="utf-8")
                jsonl.unlink(missing_ok=True)

    return {"project_id": project_id, "project": str(project_root), "events": events, "processed_files": processed_files}
