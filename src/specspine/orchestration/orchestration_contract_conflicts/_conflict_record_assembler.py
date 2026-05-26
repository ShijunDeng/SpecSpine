from __future__ import annotations

from pathlib import Path

from ..orchestration_models import OrchestrationConflict
from ._conflict_pair_scanner import scan_feature_pair_contracts

__all__ = [
    "_build_pairwise_conflicts",
]


def _build_pairwise_conflicts(
    root: Path,
    features: list[str],
    feature_contracts: dict[str, dict[str, list[str]]],
) -> list[OrchestrationConflict]:
    """Compare feature pairs and build conflict records for shared contracts."""
    conflicts: list[OrchestrationConflict] = []

    for i, slug_a in enumerate(features):
        for slug_b in features[i + 1:]:
            pair_info = scan_feature_pair_contracts(
                root, slug_a, slug_b, feature_contracts,
            )
            if pair_info is None:
                continue

            conflicts.append(
                OrchestrationConflict(
                    conflict_type="contract",
                    affected_files=tuple(pair_info.affected_files),
                    affected_ac_ids=tuple(pair_info.ac_ids),
                    features_involved=tuple(sorted([pair_info.slug_a, pair_info.slug_b])),
                    severity=pair_info.severity,
                    description=(
                        f"Features '{pair_info.slug_a}' and '{pair_info.slug_b}' modify overlapping contracts: "
                        f"{pair_info.contract_details}."
                    ),
                )
            )
    return conflicts
