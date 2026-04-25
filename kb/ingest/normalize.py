from __future__ import annotations

from pathlib import Path


def normalize_markdown(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else path.stem
    return title or path.stem, text
