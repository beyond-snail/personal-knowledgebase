from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _inbox_dir(project_root: Path) -> Path:
    # Align with workflow conventions for easy statusbar integration.
    return project_root / ".ai" / "runtime" / "inbox"


def append_event(project_root: Path, payload: dict[str, Any]) -> Path:
    root = project_root.resolve()
    inbox = _inbox_dir(root)
    inbox.mkdir(parents=True, exist_ok=True)

    line = dict(payload)
    if "timestamp" not in line:
        line["timestamp"] = datetime.now().astimezone().isoformat(timespec="seconds")

    fname = f"statusbar-{datetime.now().strftime('%Y%m%d')}.jsonl"
    target = inbox / fname
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return target
