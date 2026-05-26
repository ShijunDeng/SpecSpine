from __future__ import annotations

from pathlib import Path

from ..orchestration_models import OrchestrationConflict
from ._contract_aggregator import _aggregate_feature_contracts
from ._conflict_builder import _build_pairwise_conflicts


def _detect_contract_conflicts(root: Path, features: list[str]) -> list[OrchestrationConflict]:
    """Detect contract conflicts between features by aggregating and comparing contracts."""
    feature_contracts = _aggregate_feature_contracts(root, features)
    return _build_pairwise_conflicts(root, features, feature_contracts)


__all__ = [
    "_detect_contract_conflicts",
]
