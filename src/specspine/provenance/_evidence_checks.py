from __future__ import annotations

from typing import Iterable

from ..features import (
    FeatureReadyCheck,
)

__all__ = [
    "_check_dicts",
]


def _check_dicts(checks: Iterable[FeatureReadyCheck]) -> list[dict[str, str]]:
    return [check.as_dict() for check in checks]
