"""Detección del ejecutable Blender."""
import os
import shutil
from pathlib import Path


def find_blender():
    configured = os.environ.get("BLENDER_EXECUTABLE", "").strip().strip('"')
    candidates = [Path(configured)] if configured else []
    located = shutil.which("blender") or shutil.which("blender.exe")
    if located:
        candidates.append(Path(located))
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in {".exe", ""}:
            return candidate.resolve()
    return None
