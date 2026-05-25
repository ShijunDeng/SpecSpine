from __future__ import annotations

__all__ = [
    "HYGIENE_SAFETY_NOTES",
]

HYGIENE_SAFETY_NOTES: tuple[str, ...] = (
    "This scan reads local workspace files only.",
    "It does not delete files, run tests, invoke subprocesses, call network services, call GitHub, invoke upstream CLIs, read environment variables, or read tokens.",
    "Binary, symlinked, generated, and unreadable files are skipped rather than treated as clean.",
)
