from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from .db import connect


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def upsert_project(name: str, root_path: str) -> str:
    project_id = f"proj-{_sha(root_path)[:12]}"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO projects(project_id, name, root_path)
            VALUES(?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
              name=excluded.name,
              root_path=excluded.root_path,
              updated_at=CURRENT_TIMESTAMP
            """,
            (project_id, name, root_path),
        )
        conn.commit()
    return project_id


def upsert_item(project_id: str, item_type: str, title: str, content: str, source_path: str) -> str:
    content_hash = _sha(content)
    item_id = f"item-{content_hash[:16]}"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO items(item_id, project_id, item_type, title, content_text, source_path, content_hash)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
              title=excluded.title,
              content_text=excluded.content_text,
              source_path=excluded.source_path,
              updated_at=CURRENT_TIMESTAMP
            """,
            (item_id, project_id, item_type, title, content, source_path, content_hash),
        )
        conn.execute("DELETE FROM items_fts WHERE item_id=?", (item_id,))
        conn.execute(
            "INSERT INTO items_fts(item_id, title, content_text, source_path) VALUES(?, ?, ?, ?)",
            (item_id, title, content, source_path),
        )
        conn.commit()
    return item_id


def create_link(from_id: str, to_id: str, relation_type: str) -> str:
    link_id = f"lnk-{uuid.uuid4().hex[:16]}"
    with connect() as conn:
        conn.execute(
            "INSERT INTO links(link_id, from_id, to_id, relation_type) VALUES(?, ?, ?, ?)",
            (link_id, from_id, to_id, relation_type),
        )
        conn.commit()
    return link_id


def search_items(query: str, limit: int = 20) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT i.item_id, i.item_type, i.title, i.source_path,
                   snippet(items_fts, 2, '[', ']', ' … ', 24) AS snippet
            FROM items_fts
            JOIN items i ON i.item_id = items_fts.item_id
            WHERE items_fts MATCH ?
            LIMIT ?
            """,
            (query, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def get_trace(item_id: str) -> dict:
    with connect() as conn:
        item = conn.execute(
            "SELECT item_id, title, item_type, source_path FROM items WHERE item_id=?", (item_id,)
        ).fetchone()
        if not item:
            return {"item": None, "links": []}
        links = conn.execute(
            "SELECT from_id, to_id, relation_type FROM links WHERE from_id=? OR to_id=?",
            (item_id, item_id),
        ).fetchall()
    return {"item": dict(item), "links": [dict(l) for l in links]}
