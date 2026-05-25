from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features import validate_feature_slug
from .models import SecurityCueReport
from .helpers import (
    _dedupe,
    _feature_slug_from_path,
    _normalise_changed_file,
)
from ._report_file_analysis import _analyze_changed_files
from ._report_assembly import _assemble_security_report

__all__ = [
    "build_security_cue_report",
]


def build_security_cue_report(
    root: Path,
    *,
    changed_files: tuple[str, ...] = (),
    feature: str | None = None,
) -> SecurityCueReport:
    resolved_root = root.resolve()
    feature_slug = validate_feature_slug(feature) if feature is not None else None
    normalised_pairs = [
        _normalise_changed_file(resolved_root, path) for path in changed_files
    ]
    normalised_changed_files = _dedupe([path for path, _resolved in normalised_pairs])
    resolved_by_path = {path: resolved for path, resolved in normalised_pairs}

    files, cues, categories, files_existing = _analyze_changed_files(
        resolved_root, normalised_changed_files, resolved_by_path,
    )

    inferred_features: list[str] = []
    for path in normalised_changed_files:
        inferred = _feature_slug_from_path(path)
        if inferred is not None:
            inferred_features.append(inferred)

    return _assemble_security_report(
        resolved_root=resolved_root,
        feature_slug=feature_slug,
        normalised_changed_files=normalised_changed_files,
        files=files,
        cues=cues,
        categories=categories,
        files_existing=files_existing,
        inferred_features=inferred_features,
    )
