# Event Protocol (Statusbar -> Personal Knowledgebase)

## Inbox Path

Statusbar writes JSONL events to one of:

1. `<project-root>/knowledge-store/inbox/*.jsonl`
2. `<project-root>/.ai/runtime/inbox/*.jsonl`

## Minimal Event Schema

```json
{
  "event_type": "workflow.execution.done",
  "req_id": "REQ-2026-04-25-01",
  "task_id": "TASK-2026-04-25-04",
  "summary": "trace api delivered",
  "source_path": "docs/workflow/requirements/任务看板.md",
  "timestamp": "2026-04-25T17:10:00+08:00"
}
```

## Required Fields

- `event_type`: string
- `summary`: string

## Recommended Fields

- `req_id`, `task_id`: used for auto-linking trace graph
- `source_path`: evidence source
- `timestamp`: event time
- `type`: fallback alias for `event_type`
- `message`: fallback alias for `summary`

## Idempotency

- The importer is content-hash based and upsert-safe.
- Processed `.jsonl` is renamed to `.done` to avoid duplicate consumption.

## API Trigger

- Manual trigger: `POST /api/ingest/inbox?project=<path>`
- Auto trigger: server background collector polls every 8 seconds for registered projects.
