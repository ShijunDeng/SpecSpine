from __future__ import annotations

from pathlib import Path

from .orchestration_detection import (
    _detect_contract_conflicts,
    _detect_file_conflicts,
    _detect_semantic_conflicts,
)

__all__ = [
    "_detect_conflicts",
]


def _detect_conflicts(
    resolved_root: Path,
    slugs: list[str],
) -> list:
    file_conflicts = _detect_file_conflicts(resolved_root, slugs)
    contract_conflicts = _detect_contract_conflicts(resolved_root, slugs)
    semantic_conflicts = _detect_semantic_conflicts(slugs, resolved_root)
    return file_conflicts + contract_conflicts + semantic_conflicts
