from __future__ import annotations

from .features import FEATURE_FILE_PATHS
from .evolution_classification_models import ClassifiedChange
from .evolution_classification_helpers import (
    _extract_metadata,
)

__all__ = [
    "_compare_metadata",
]


def _compare_metadata(
    base_spec: str | None,
    current_spec: str | None,
    slug: str,
    change_counter: int,
) -> tuple[list[ClassifiedChange], int]:
    changes: list[ClassifiedChange] = []

    if base_spec != current_spec:
        before_meta = _extract_metadata(base_spec or "")
        after_meta = _extract_metadata(current_spec or "")
        if before_meta != after_meta:
            change_counter += 1
            changes.append(
                ClassifiedChange(
                    change_id=f"CHG{change_counter:03d}",
                    change_type="modified",
                    category="metadata",
                    file=FEATURE_FILE_PATHS["spec"].format(slug=slug),
                    line=0,
                    before=str(before_meta),
                    after=str(after_meta),
                )
            )

    return changes, change_counter
