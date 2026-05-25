from __future__ import annotations

__all__ = [
    "SUPPORTED_FORMATS",
    "SAFETY_NOTES",
]

SUPPORTED_FORMATS = ("github-actions", "gitlab-ci", "generic")

SAFETY_NOTES = (
    "This pipeline is generated read-only: no network calls, no subprocess execution, no token reads.",
    "Acceptance criteria from spec bundles become test gates in the pipeline.",
    "Quality metrics from quality/checklist.md become merge requirements.",
    "Feature readiness gates become deployment conditions when --feature is specified.",
    "Review generated pipeline before committing to CI system.",
)
