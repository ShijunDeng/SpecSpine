from __future__ import annotations

__all__ = [
    "VALID_GROUP_BY",
    "SAFETY_NOTES",
]

VALID_GROUP_BY = ("priority", "status", "project", "effort")

SAFETY_NOTES = (
    "Benchmark report is read-only and advisory.",
    "Does not run tests, invoke subprocesses, call network services, or read tokens.",
    "Recommended commands are advisory and are not executed.",
    "Missing evidence sources degrade gracefully.",
)
