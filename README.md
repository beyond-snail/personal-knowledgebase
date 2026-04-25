# Personal Knowledgebase (Local First)

A local-first personal knowledgebase with automatic collection, SQLite + FTS5 search, and traceable evidence.

## Features (V0)

- Local storage with SQLite
- Full-text search with FTS5
- Auto ingest from workflow docs (`.ai/memory`, `docs/workflow`)
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
kb-serve
```

Open: `http://127.0.0.1:8787`

## Project Layout

- `kb/api`: FastAPI app and routes
- `kb/core`: database and search core
- `kb/ingest`: collectors and importers
- `knowledge-store`: local runtime data
- `web`: static frontend
