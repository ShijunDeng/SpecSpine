from __future__ import annotations

from pathlib import Path

from .release_breaking import _compute_summary, _detect_breaking_changes
from .release_features import _collect_release_features, _group_features
from .release_models import ReleaseNotesReport

__all__ = [
    "_safety_notes",
    "build_release_notes_report",
]


def _safety_notes() -> tuple[str, ...]:
    return (
        "This release notes report is advisory only.",
        "Breaking change detection uses heuristic pattern matching on spec content.",
        "SpecSpine did not run commands, run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, read environment variables, or read tokens.",
    )


def build_release_notes_report(
    root: Path,
    since: str | None = None,
    until: str | None = None,
    group_by: str = "priority",
) -> ReleaseNotesReport:
    resolved_root = root.expanduser().resolve()

    features = _collect_release_features(resolved_root, since=since, until=until)
    grouped = _group_features(features, group_by)
    breaking_changes = _detect_breaking_changes(features, resolved_root)
    summary = _compute_summary(features, breaking_changes)

    date_range = ""
    if since and until:
        date_range = f"{since}..{until}"
    elif since:
        date_range = f"{since}..latest"
    elif until:
        date_range = f"initial..{until}"
    else:
        date_range = "all"

    return ReleaseNotesReport(
        version="1",
        date_range=date_range,
        grouped_features=grouped,
        breaking_changes=breaking_changes,
        summary=summary,
        safety_notes=_safety_notes(),
    )
