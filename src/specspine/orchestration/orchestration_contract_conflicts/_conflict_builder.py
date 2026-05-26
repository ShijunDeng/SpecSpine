from __future__ import annotations

from pathlib import Path

from ...features import FEATURE_FILE_PATHS
from ..orchestration_models import OrchestrationConflict
from ..orchestration_extraction import _extract_ac_ids


def _build_pairwise_conflicts(
    root: Path,
    features: list[str],
    feature_contracts: dict[str, dict[str, list[str]]],
) -> list[OrchestrationConflict]:
    """Compare feature pairs and build conflict records for shared contracts."""
    conflicts: list[OrchestrationConflict] = []

    for i, slug_a in enumerate(features):
        for slug_b in features[i + 1:]:
            shared_contracts: list[tuple[str, str]] = []
            for contract_type in ("endpoint", "schema", "config"):
                set_a = set(feature_contracts[slug_a].get(contract_type, []))
                set_b = set(feature_contracts[slug_b].get(contract_type, []))
                for name in sorted(set_a & set_b):
                    shared_contracts.append((contract_type, name))

            if shared_contracts:
                affected_files: list[str] = []
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            rel = FEATURE_FILE_PATHS[kind].format(slug=s)
                            if rel not in affected_files:
                                affected_files.append(rel)

                combined_content = ""
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            combined_content += fp.read_text(encoding="utf-8")
                ac_ids = _extract_ac_ids(combined_content)

                contract_types_involved = sorted(set(ct for ct, _ in shared_contracts))
                severity = "critical" if "endpoint" in contract_types_involved else "high"
                contract_details = ", ".join(f"{ct}: {name}" for ct, name in shared_contracts)

                conflicts.append(
                    OrchestrationConflict(
                        conflict_type="contract",
                        affected_files=tuple(affected_files),
                        affected_ac_ids=tuple(ac_ids),
                        features_involved=tuple(sorted([slug_a, slug_b])),
                        severity=severity,
                        description=(
                            f"Features '{slug_a}' and '{slug_b}' modify overlapping contracts: "
                            f"{contract_details}."
                        ),
                    )
                )
    return conflicts


__all__ = [
    "_build_pairwise_conflicts",
]
