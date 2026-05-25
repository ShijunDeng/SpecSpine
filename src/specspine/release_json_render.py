from __future__ import annotations

import json

from .release_models import ReleaseNotesReport

__all__ = [
    "render_release_notes_json",
    "render_release_notes_json_lines",
]


def render_release_notes_json(report: ReleaseNotesReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_release_notes_json_lines(report: ReleaseNotesReport) -> str:
    json_lines: list[str] = []
    json_lines.append(json.dumps({"type": "release_notes", **report.as_dict()}, sort_keys=True))

    for group_name, entries in report.grouped_features.items():
        for entry in entries:
            json_lines.append(
                json.dumps(
                    {"type": "feature", "group": group_name, **entry.as_dict()},
                    sort_keys=True,
                )
            )

    for bc in report.breaking_changes:
        json_lines.append(
            json.dumps({"type": "breaking_change", **bc.as_dict()}, sort_keys=True)
        )

    return "\n".join(json_lines) + "\n"
