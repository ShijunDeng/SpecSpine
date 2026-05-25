from __future__ import annotations

from typing import Any

from ..features import FeatureTestsReport
from ._recommend_commands import _command_for_coverage_target

__all__ = [
    "_feature_block",
]


def _feature_block(report: FeatureTestsReport) -> dict[str, Any]:
    coverage_targets = tuple(
        sorted(
            {
                link.target_path or link.target
                for link in report.test_coverage
                if link.target_path or link.target
            }
        )
    )
    coverage_commands = tuple(
        command
        for command in (
            _command_for_coverage_target(target)
            for target in coverage_targets
        )
        if command is not None
    )
    recommended_commands = tuple(dict.fromkeys(coverage_commands)) or report.recommended_commands
    return {
        "coverage_targets": list(coverage_targets),
        "feature_id": report.feature_id,
        "has_native_files": report.has_native_files,
        "missing_files": list(report.missing_files),
        "ready": report.ready,
        "recommended_commands": list(recommended_commands),
        "status": report.status,
        "test_coverage": [link.as_dict() for link in report.test_coverage],
    }
