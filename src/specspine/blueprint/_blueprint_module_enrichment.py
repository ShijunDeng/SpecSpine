from __future__ import annotations

from .blueprint_models import BlueprintFunction, BlueprintModule

__all__ = [
    "enrich_modules",
]


def enrich_modules(
    modules: list[BlueprintModule],
    module_functions: dict[str, list[BlueprintFunction]],
) -> list[BlueprintModule]:
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
    return enriched_modules
