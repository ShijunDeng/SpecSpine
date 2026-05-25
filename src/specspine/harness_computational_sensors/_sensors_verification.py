from __future__ import annotations

from pathlib import Path

from ..features import (
    FeatureBundleNotFoundError,
    InvalidFeatureSlug,
)
from ..harness_models import HarnessFeedbackSensor
from ..verification import build_verification_matrix
from ..harness_computational_readers import _extract_ac_ids, _read_feature_contents

__all__ = [
    "_build_verification_matrix_sensor",
]


def _build_verification_matrix_sensor(resolved_root: Path, slug: str, ac_ids: tuple[str, ...]) -> HarnessFeedbackSensor:
    try:
        matrix = build_verification_matrix(resolved_root, slug)
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="pass" if matrix.ready else "fail",
            output={
                "verified": matrix.summary.get("verified", 0),
                "unverified": matrix.summary.get("unverified", 0),
                "coverage_complete": matrix.summary.get("coverage_complete", 0),
                "blocking_checks": matrix.summary.get("blocking_checks", 0),
                "gaps": matrix.summary.get("gaps", 0),
            },
            ac_ids=ac_ids,
        )
    except (FeatureBundleNotFoundError, InvalidFeatureSlug, OSError):
        return HarnessFeedbackSensor(
            sensor_type="computational",
            name="verification_matrix",
            status="fail",
            output={"error": "verification_matrix_unavailable"},
            ac_ids=(),
        )
