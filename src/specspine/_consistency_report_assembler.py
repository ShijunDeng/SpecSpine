from __future__ import annotations

from pathlib import Path

from ._consistency_feature_loader import (
    _load_feature_consistency_records,
    _resolve_and_validate_slug,
)
from .consistency_models import ConsistencyReport
from .consistency_report_commands import _recommended_commands
from .consistency_report_summary import _summary

__all__ = [
    "build_consistency_report",
]


def build_consistency_report(
    root: Path,
    *,
    feature_filter: str | None = None,
    changed_files: tuple[str, ...] = (),
) -> ConsistencyReport:
    resolved_root = root.expanduser().resolve()
    feature_filter = _resolve_and_validate_slug(feature_filter)

    feature_tuple, normalised_changed_files, discovered_count = (
        _load_feature_consistency_records(
            resolved_root,
            feature_filter,
            changed_files,
        )
    )

    safety_notes = (
        "This report reads local workspace files only.",
        "Recommended commands are advisory only and are not executed.",
        "SpecSpine did not run tests, invoke subprocesses, call network services, call GitHub APIs, invoke upstream CLIs, or read tokens.",
    )
    return ConsistencyReport(
        root=resolved_root,
        feature_filter=feature_filter,
        changed_files=normalised_changed_files,
        features=feature_tuple,
        summary=_summary(feature_tuple, discovered_features=discovered_count),
        recommended_commands=_recommended_commands(
            tuple(feature.feature_id for feature in feature_tuple)
        ),
        safety_notes=safety_notes,
    )
