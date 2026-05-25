from __future__ import annotations

from .blueprint_models import (
    BlueprintFunction,
)

__all__ = [
    "_compute_coverage_summary",
]


def _compute_coverage_summary(
    modules: list,
    functions: list[BlueprintFunction],
    entities: list,
    error_paths: list,
) -> dict[str, object]:
    all_ac_ids = set()
    for module in modules:
        all_ac_ids.update(module.ac_ids)
    for func in functions:
        all_ac_ids.update(func.ac_ids)
    for entity in entities:
        all_ac_ids.update(entity.ac_ids)
    for ep in error_paths:
        all_ac_ids.update(ep.ac_ids)

    return {
        "modules_total": len(modules),
        "functions_total": len(functions),
        "data_entities_total": len(entities),
        "error_paths_total": len(error_paths),
        "unique_ac_covered": len(all_ac_ids),
        "ac_ids_covered": sorted(all_ac_ids),
    }
