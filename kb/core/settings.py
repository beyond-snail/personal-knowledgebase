from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORE_ROOT = PROJECT_ROOT / "knowledge-store"
DB_DIR = STORE_ROOT / "db"
DB_PATH = DB_DIR / "knowledge.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
RAW_DIR = STORE_ROOT / "raw"
NORM_DIR = STORE_ROOT / "normalized"
INBOX_DIR = STORE_ROOT / "inbox"
SNAPSHOT_DIR = STORE_ROOT / "snapshots"
LOG_DIR = STORE_ROOT / "logs"
WEB_DIR = PROJECT_ROOT / "web"


def ensure_dirs() -> None:
    for p in (DB_DIR, RAW_DIR, NORM_DIR, INBOX_DIR, SNAPSHOT_DIR, LOG_DIR):
        p.mkdir(parents=True, exist_ok=True)
