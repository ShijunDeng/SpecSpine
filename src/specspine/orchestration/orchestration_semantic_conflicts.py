from __future__ import annotations

from pathlib import Path

from ..features import validate_feature_slug
from ..dependency import _read_all_feature_content
from .orchestration_models import OrchestrationConflict

__all__ = [
    "_detect_semantic_conflicts",
]


def _detect_semantic_conflicts(
    features: list[str],
    root: Path,
) -> list[OrchestrationConflict]:
    """Detect semantic conflicts from mutually exclusive behaviors."""
    conflicts: list[OrchestrationConflict] = []
    feature_configs: dict[str, dict[str, str]] = {}

    for feature_id in features:
        feature_id = validate_feature_slug(feature_id)
        content = _read_all_feature_content(root, feature_id)
        configs: dict[str, str] = {}
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") and ("enable" in line or "disable" in line):
                for keyword in ["enable", "disable", "toggle", "flag"]:
                    if keyword in line.lower():
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if keyword in part.lower() and i + 1 < len(parts):
                                flag_name = parts[i + 1].strip(".,;:")
                                if flag_name and flag_name not in ("the", "a", "an"):
                                    configs[flag_name.lower()] = keyword
        feature_configs[feature_id] = configs

    checked_pairs: set[tuple[str, str]] = set()
    for feature_a in features:
        for feature_b in features:
            if feature_a == feature_b:
                continue
            pair = tuple(sorted([feature_a, feature_b]))
            if pair in checked_pairs:
                continue
            checked_pairs.add(pair)

            configs_a = feature_configs.get(feature_a, {})
            configs_b = feature_configs.get(feature_b, {})

            for flag, action_a in configs_a.items():
                if flag in configs_b:
                    action_b = configs_b[flag]
                    if action_a != action_b:
                        conflicts.append(
                            OrchestrationConflict(
                                conflict_type="semantic",
                                severity="critical",
                                description=f"Features {feature_a} and {feature_b} have conflicting {flag} configuration ({action_a} vs {action_b})",
                                features_involved=tuple(sorted([feature_a, feature_b])),
                                affected_ac_ids=(),
                                affected_files=(),
                            )
                        )

    return conflicts
