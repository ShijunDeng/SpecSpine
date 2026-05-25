from __future__ import annotations

from .harness_models import HarnessFeedbackReport, RepairStrategy
from ._repair_ac_collection import _collect_failing_ac_ids
from ._repair_strategy_builder import _build_ac_repair_strategy
from ._repair_computational_fallback import _add_computational_fallback_strategies

__all__ = [
    "_generate_repair_strategies",
]


def _generate_repair_strategies(feedback_report: HarnessFeedbackReport) -> list[RepairStrategy]:
    strategies: list[RepairStrategy] = []
    seen_ac_ids: set[str] = set()

    all_failing_ac_ids = _collect_failing_ac_ids(feedback_report)

    for ac_id in sorted(all_failing_ac_ids):
        if ac_id in seen_ac_ids:
            continue
        seen_ac_ids.add(ac_id)

        strategies.append(_build_ac_repair_strategy(ac_id, feedback_report))

    if not strategies:
        _add_computational_fallback_strategies(feedback_report, strategies)

    return strategies
