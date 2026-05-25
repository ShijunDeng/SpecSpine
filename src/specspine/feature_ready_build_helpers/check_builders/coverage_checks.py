from __future__ import annotations

__all__ = [
    "_build_coverage_check",
]


def _build_coverage_check(
    acceptance_criteria: tuple,
    test_coverage: tuple,
):
    from ...feature_bundle import FeatureReadyCheck
    from ...feature_ready_checks import _ready_check
    from ...feature_ready_coverage import _coverage_ready_message

    passed, message = _coverage_ready_message(
        acceptance_criteria,
        test_coverage,
    )
    return _ready_check("feature.test_coverage", passed, message)
