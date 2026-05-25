from __future__ import annotations

from .blueprint_models import BlueprintFunction, BlueprintModule

__all__ = [
    "map_functions_to_modules",
]


def map_functions_to_modules(
    modules: list[BlueprintModule],
    functions: list[BlueprintFunction],
) -> dict[str, list[BlueprintFunction]]:
    module_functions: dict[str, list] = {}
    for func in functions:
        target_word = func.name.split("_", 1)[-1] if "_" in func.name else func.name
        for module in modules:
            module_target = module.module_path.rsplit("/", 1)[-1].replace(".py", "")
            if target_word in module_target or module_target in target_word:
                module_functions.setdefault(module.module_path, []).append(func)
                break
    return module_functions
