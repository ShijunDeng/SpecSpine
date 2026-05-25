from __future__ import annotations

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

    module_functions: dict[str, list] = {}
    for func in functions:
        target_word = func.name.split("_", 1)[-1] if "_" in func.name else func.name
        for module in modules:
            module_target = module.module_path.rsplit("/", 1)[-1].replace(".py", "")
            if target_word in module_target or module_target in target_word:
                module_functions.setdefault(module.module_path, []).append(func)
                break

    enriched_modules = []
    for module in modules:
        mod_funcs = tuple(module_functions.get(module.module_path, []))
        all_ac = set(module.ac_ids)
        for f in mod_funcs:
            all_ac.update(f.ac_ids)
        enriched_modules.append(
            BlueprintModule(
                module_path=module.module_path,
                responsibility=module.responsibility,
                functions=mod_funcs,
                ac_ids=tuple(sorted(all_ac)),
            )
        )

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
