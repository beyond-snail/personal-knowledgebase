from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from kb.core.bootstrap import init_store
from kb.ingest.importer import ingest_project


def cmd_init() -> None:
    init_store()
    print("initialized")


def cmd_ingest() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", action="append", required=True)
    args = parser.parse_args()
    init_store()
    for project in args.project:
        result = ingest_project(Path(project))
        print(result)


def cmd_serve() -> None:
    uvicorn.run("kb.api.main:app", host="127.0.0.1", port=8787, reload=False)
