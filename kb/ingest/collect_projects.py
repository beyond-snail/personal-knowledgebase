from __future__ import annotations

from pathlib import Path

TARGET_DIRS = ["docs/workflow", ".ai/memory"]


def collect_markdown_files(project_root: Path) -> list[Path]:
    files: list[Path] = []
    for rel in TARGET_DIRS:
        base = project_root / rel
        if not base.exists():
            continue
        files.extend(base.rglob("*.md"))
    return files
