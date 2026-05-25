from __future__ import annotations

from .analysis_models import AC_REFERENCE_RE

__all__ = [
    "_referenced_ac_ids_for_task",
]


def _referenced_ac_ids_for_task(text: str) -> set[str]:
    return {f"AC{int(match.group(1)):03d}" for match in AC_REFERENCE_RE.finditer(text)}
