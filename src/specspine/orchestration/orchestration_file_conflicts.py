from __future__ import annotations

from pathlib import Path

from ..features import FEATURE_FILE_PATHS
from .orchestration_models import OrchestrationConflict
from .orchestration_extraction import _scan_feature_file_paths, _extract_ac_ids

__all__ = [
    "_detect_file_conflicts",
]


def _detect_file_conflicts(root: Path, features: list[str]) -> list[OrchestrationConflict]:
    conflicts: list[OrchestrationConflict] = []
    feature_paths: dict[str, set[str]] = {}
    for slug in features:
        feature_paths[slug] = _scan_feature_file_paths(root, slug)

    for i, slug_a in enumerate(features):
        for slug_b in features[i + 1:]:
            shared = sorted(feature_paths[slug_a] & feature_paths[slug_b])
            if shared:
                combined_content = ""
                for kind in FEATURE_FILE_PATHS:
                    for s in (slug_a, slug_b):
                        fp = root / FEATURE_FILE_PATHS[kind].format(slug=s)
                        if fp.exists():
                            combined_content += fp.read_text(encoding="utf-8")
                ac_ids = _extract_ac_ids(combined_content)
                conflicts.append(
                    OrchestrationConflict(
                        conflict_type="file",
                        affected_files=tuple(shared),
                        affected_ac_ids=tuple(ac_ids),
                        features_involved=tuple(sorted([slug_a, slug_b])),
                        severity="high" if len(shared) > 3 else "medium",
                        description=(
                            f"Features '{slug_a}' and '{slug_b}' target "
                            f"{len(shared)} overlapping file paths."
                        ),
                    )
                )
    return conflicts
