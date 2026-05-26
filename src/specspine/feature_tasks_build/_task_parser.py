from __future__ import annotations

from ..feature_bundle import (
    FeatureTask,
    parse_feature_tasks,
)

__all__ = [
    "_parse_tasks_from_content",
]


def _parse_tasks_from_content(
    execution_content: str | None,
    source_file: str,
) -> tuple[FeatureTask, ...]:
    if execution_content is None:
        return ()
    return parse_feature_tasks(execution_content, source_file=source_file)
