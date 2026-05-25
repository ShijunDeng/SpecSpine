from __future__ import annotations

from ._blueprint_func_module_mapping import map_functions_to_modules
from ._blueprint_module_enrichment import enrich_modules
from .blueprint_entities import _derive_error_paths, _identify_data_entities
from .blueprint_models import (
    BlueprintFunction,
    BlueprintModule,
    BlueprintReport,
)
from .blueprint_structure import (
    _derive_module_structure,
    _generate_function_signatures,
)
from .blueprint_coverage_summary import _compute_coverage_summary
from .blueprint_coverage_safety import _derive_safety_notes

__all__ = [
    "assemble_blueprint_report",
]


def assemble_blueprint_report(
    slug: str,
    ac_list: list,
    domains: dict,
) -> BlueprintReport:
    modules = _derive_module_structure(domains, slug)

    functions = _generate_function_signatures(ac_list, slug)

    entities = _identify_data_entities(ac_list, slug)

    error_paths = _derive_error_paths(ac_list, slug)

    module_functions = map_functions_to_modules(modules, functions)

    enriched_modules = enrich_modules(modules, module_functions)

    coverage_summary = _compute_coverage_summary(
        enriched_modules, functions, entities, error_paths,
    )
    safety_notes = _derive_safety_notes(functions, error_paths)

    return BlueprintReport(
        feature_id=slug,
        modules=tuple(enriched_modules),
        functions=tuple(functions),
        data_entities=tuple(entities),
        error_paths=tuple(error_paths),
        coverage_summary=coverage_summary,
        safety_notes=safety_notes,
    )
