from __future__ import annotations

from typing import Any

from ._content_parser import _parse_contents
from ._step_assemble_core import _assemble_steps


def _build_steps_from_contents(
    contents: dict[str, str],
    slug: str,
    relative_paths: dict[str, str],
) -> list[dict[str, Any]]:
    ac_items, task_items, quality_items, ac_by_id, task_dep_map, source_files = _parse_contents(
        contents, relative_paths
    )
    return _assemble_steps(task_items, ac_by_id, task_dep_map, source_files, slug)


__all__ = [
    "_build_steps_from_contents",
]
