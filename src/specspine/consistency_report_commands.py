from __future__ import annotations

from typing import Any

from .consistency_models import (
    FeatureConsistency,
)
from .consistency_utils import (
    _dedupe,
)

__all__ = [
    "_recommended_commands",
]


def _recommended_commands(feature_ids: tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = ["specspine consistency scan . --json"]
    for slug in feature_ids:
        commands.extend(
            [
                f"specspine consistency scan . --feature {slug} --json",
                f"specspine feature trace {slug} . --json",
                f"specspine tests impact . --feature {slug} --json",
                f"specspine review packet . --feature {slug} --json",
            ]
        )
    commands.append("specspine validate . --fusion --features")
    return _dedupe(commands)
