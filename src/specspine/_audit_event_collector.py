from __future__ import annotations

from pathlib import Path

from ._audit_event_parser import _parse_audit_event_line
from ._audit_event_resolver import _resolve_audit_event_paths
from .audit_models import AuditEvent
from .evolution import _run_git

__all__ = [
    "_collect_audit_events",
]


def _collect_audit_events(slug: str, root: Path, since: str | None) -> list[AuditEvent]:
    events: list[AuditEvent] = []
    rel_paths, has_files = _resolve_audit_event_paths(slug, root)
    if not has_files:
        return events

    git_args = ["log", "--format=%H|%ai|%an|%s", "--"] + rel_paths
    result = _run_git(git_args, root)
    if result.returncode != 0:
        return events

    for line in result.stdout.strip().splitlines():
        event = _parse_audit_event_line(line, since, slug, root, _run_git)
        if event is not None:
            events.append(event)

    return events
