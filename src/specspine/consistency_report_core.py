from __future__ import annotations

import json
from pathlib import Path

from .consistency_models import (
    ConsistencyReport,
    FeatureConsistency,
)
from .consistency_records import (
    _build_feature_record,
    _missing_feature_record,
)
from .consistency_utils import (
    _dedupe,
    _normalise_changed_file,
)
from .consistency_report_commands import _recommended_commands
from .consistency_report_summary import _summary
from .features import (
    InvalidFeatureSlug,
    list_feature_bundles,
    validate_feature_slug,
)

__all__ = [
    "build_consistency_report",
    "render_consistency_json",
]


def build_consistency_report(
    root: Path,
    *,
    feature_filter: str | None = None,
    changed_files: tuple[str, ...] = (),
) -> ConsistencyReport:
    resolved_root = root.expanduser().resolve()
    if feature_filter is not None:
        feature_filter = validate_feature_slug(feature_filter)
    normalised_changed_files = tuple(
        _dedupe(
            [
                _normalise_changed_file(resolved_root, changed_file)
                for changed_file in changed_files
            ]
        )
    )

    discovered = list_feature_bundles(resolved_root)
    discovered_slugs = tuple(str(feature["slug"]) for feature in discovered)
    if feature_filter is not None:
        slugs = (feature_filter,)
    else:
        slugs = discovered_slugs

    features: list[FeatureConsistency] = []
    for slug in slugs:
        validate_feature_slug(slug)
        if slug not in discovered_slugs:
            features.append(_missing_feature_record(resolved_root, slug))
        else:
            features.append(
                _build_feature_record(
                    resolved_root,
                    slug,
                    changed_files=normalised_changed_files,
                )
            )

    feature_tuple = tuple(sorted(features, key=lambda feature: feature.feature_id))
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
        summary=_summary(feature_tuple, discovered_features=len(discovered)),
        recommended_commands=_recommended_commands(
            tuple(feature.feature_id for feature in feature_tuple)
        ),
        safety_notes=safety_notes,
    )


def render_consistency_json(report: ConsistencyReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
