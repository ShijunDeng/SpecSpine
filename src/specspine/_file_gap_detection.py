from __future__ import annotations

from .feature_bundle import _trace_gap

__all__ = ["_detect_file_gaps"]


def _detect_file_gaps(missing_files: list[str]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for relative_path in missing_files:
        gaps.append(
            _trace_gap(
                "missing_file",
                relative_path,
                f"Missing native feature file: {relative_path}",
            )
        )
    return gaps
