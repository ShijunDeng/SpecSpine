from __future__ import annotations

from ..coverage_utils import _coverage_detail_command, _feature_tests_command

__all__ = [
    "_build_recommended_commands",
]


def _build_recommended_commands(
    slug: str,
    *,
    coverage_required: bool,
    missing_ids: list[str],
    use_policy: bool,
) -> list[str]:
    if coverage_required and missing_ids:
        return [
            _coverage_detail_command(slug, use_policy=use_policy),
            _feature_tests_command(slug),
        ]
    return []
