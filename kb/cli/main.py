from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from kb.core.bootstrap import init_store
from kb.ingest.event_bridge import append_event
from kb.ingest.importer import ingest_inbox, ingest_project


def cmd_init() -> None:
    init_store()
    print("initialized")


def cmd_ingest() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", action="append", required=True)
    parser.add_argument("--with-inbox", action="store_true")
    parser.add_argument("--inbox-only", action="store_true")
    args = parser.parse_args()
    init_store()
    for project in args.project:
        root = Path(project)
        if not args.inbox_only:
            result = ingest_project(root)
            print(result)
        if args.with_inbox or args.inbox_only:
            inbox_result = ingest_inbox(root)
            print(inbox_result)


def cmd_serve() -> None:
    uvicorn.run("kb.api.main:app", host="127.0.0.1", port=8787, reload=False)


def cmd_event() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--event-type", default="workflow.execution.note")
    parser.add_argument("--summary", default="manual event")
    parser.add_argument("--req-id", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--source-path", default="")
    parser.add_argument("--json", default="")
    parser.add_argument("--process-now", action="store_true")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    init_store()

    if args.json:
        payload = json.loads(Path(args.json).read_text(encoding="utf-8"))
    else:
        payload = {
            "event_type": args.event_type,
            "summary": args.summary,
        }
        if args.req_id:
            payload["req_id"] = args.req_id
        if args.task_id:
            payload["task_id"] = args.task_id
        if args.source_path:
            payload["source_path"] = args.source_path

    target = append_event(root, payload)
    print({"ok": True, "target_file": str(target)})
    if args.process_now:
        print(ingest_inbox(root))
