# Personal Knowledgebase (Local First)

A local-first personal knowledgebase with automatic collection, SQLite + FTS5 search, and traceable evidence.

## Features (V0)

- Local storage with SQLite
- Full-text search with FTS5
- Auto ingest from workflow docs (`.ai/memory`, `docs/workflow`)
- Inbox event ingest from statusbar/workflow (`knowledge-store/inbox/*.jsonl`)
- Background auto collector (polls registered projects every 8s)
- Evidence trace endpoint
- Minimal web dashboard

## Run

```bash
cd personal-knowledgebase
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
kb-init
kb-ingest --project /Users/wucongpeng/Documents/ai/skill
kb-ingest --project /Users/wucongpeng/Documents/ai/skill --with-inbox
kb-event --project /Users/wucongpeng/Documents/ai/skill --event-type workflow.execution.done --summary "manual bridge test" --process-now
kb-serve
```

Open: `http://127.0.0.1:8787`

## Inbox Event Format

Drop JSONL events into `knowledge-store/inbox/`, then run `kb-ingest --project <root> --inbox-only`.

Example line:

```json
{"event_type":"workflow.execution.done","req_id":"REQ-2026-04-25-01","task_id":"TASK-2026-04-25-04","summary":"trace API delivered","source_path":"docs/workflow/requirements/任务看板.md"}
```

See full protocol: `docs-event-protocol.md`

## Statusbar Direct Push

Statusbar can push events directly:

```bash
curl -X POST \"http://127.0.0.1:8787/api/events/push?project=/path/to/repo&process_now=true\" \\\n+  -H \"Content-Type: application/json\" \\\n+  -d '{\"event_type\":\"workflow.execution.done\",\"req_id\":\"REQ-2026-04-25-01\",\"task_id\":\"TASK-2026-04-25-04\",\"summary\":\"delivered\"}'\n+```

## Project Layout

- `kb/api`: FastAPI app and routes
- `kb/core`: database and search core
- `kb/ingest`: collectors and importers
- `knowledge-store`: local runtime data
- `web`: static frontend
