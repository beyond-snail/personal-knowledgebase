# Personal Knowledgebase Architecture (Local First)

## Product Shape

- Collector: workflow-statusbar (always-on)
- Engine: local ingest + normalize + index
- Query: search + trace + weekly
- UI: local web dashboard

## Data Flow

1. Collect from project roots (`docs/workflow`, `.ai/memory`, optional test artifacts)
2. Normalize into structured records
3. Upsert into SQLite
4. Build FTS5 index
5. Serve retrieval via API

## Storage

- SQLite: source of truth
- FTS5: keyword retrieval
- Optional next: sqlite-vec for semantic retrieval

## Core Modules

- `kb/ingest`: source collectors, normalizer, importer
- `kb/core`: schema, repository, search, trace
- `kb/api`: FastAPI endpoints
- `web`: dashboard UI

## Planned Milestones

- V0: local search + ingest + basic web (done)
- V1: workflow event inbox, trace links, weekly report
- V1.1: statusbar bridge for auto incremental collection
- V1.2: semantic retrieval + rerank
