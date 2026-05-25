from __future__ import annotations

import json

from .archive_models import FeatureArchiveReport

__all__ = [
    "render_feature_archive_json",
]


def render_feature_archive_json(report: FeatureArchiveReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"
