from __future__ import annotations

from .features import (
    FEATURE_FILE_PATHS,
    FeatureReadyCheck,
)
from .analysis_models import _PendingIssue
from .analysis_traceability_commands import _feature_ready_command
from .analysis_traceability_ac_helpers import (
    _ready_check_severity,
    _ready_check_category,
)

__all__ = [
    "_readiness_issues",
]


def _readiness_issues(
    slug: str,
    checks: tuple[FeatureReadyCheck, ...],
) -> list[_PendingIssue]:
    issues: list[_PendingIssue] = []
    for check in checks:
        if check.status != "fail":
            continue
        issues.append(
            _PendingIssue(
                feature_id=slug,
                severity=_ready_check_severity(check),
                category=_ready_check_category(check),
                code=check.id,
                message=check.message,
                source_file=FEATURE_FILE_PATHS["quality"].format(slug=slug),
                evidence={"check_id": check.id},
                recommended_command=_feature_ready_command(slug),
            )
        )
    return issues
