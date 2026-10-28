"""Detect fixture bytes changed by a test run."""

from __future__ import annotations

import hashlib
from pathlib import Path

from support.fixtures import FIXTURES


def snapshot(root: Path = FIXTURES) -> dict[str, str]:
    digests = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        digests[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def changes(before: dict[str, str], after: dict[str, str] | None = None) -> list[str]:
    after = snapshot() if after is None else after
    return sorted(
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )
