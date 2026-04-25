from __future__ import annotations

from .db import connect
from .settings import SCHEMA_PATH, ensure_dirs


def init_store() -> None:
    ensure_dirs()
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(sql)
        conn.commit()
