from __future__ import annotations

from .helpers import _dedupe_commands
from .feature_commands import _build_feature_commands

__all__ = [
    "_build_packet_commands",
]


def _build_packet_commands(
    feature_slug: str | None,
    impact_recommendations: tuple[str, ...],
    gates_recommended_commands: tuple[str, ...],
) -> tuple[str, ...]:
    feature_commands = _build_feature_commands(feature_slug)
    return _dedupe_commands(
        impact_recommendations,
        gates_recommended_commands,
        (
            "specspine review packet . --json",
            "specspine validate . --fusion --features",
        ),
        feature_commands,
    )
