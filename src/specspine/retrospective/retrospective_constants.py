from __future__ import annotations

SAFETY_NOTES = (
    "Read-only local report: does not write files.",
    "Does not run tests or invoke subprocesses.",
    "Does not call network services, GitHub, or upstream CLIs.",
    "Does not read environment variables or tokens.",
    "Recommended commands are advisory and are not executed.",
)

__all__ = ["SAFETY_NOTES"]
