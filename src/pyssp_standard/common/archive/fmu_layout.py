from __future__ import annotations

import re

_PLATFORM_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


def platform_component(platform: str) -> str:
    """Return *platform* when it is a safe FMI binaries path component."""
    if not _PLATFORM_PATTERN.fullmatch(platform):
        raise ValueError(f"Invalid platform token: {platform!r}")
    return platform
