from __future__ import annotations

from ..features import validate_feature_slug

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import BlueprintFunction, BlueprintModule

__all__ = [
    "_derive_module_structure",
    "_generate_function_signatures",
]


def _derive_module_structure(
    domains: dict[str, list[dict[str, str]]],
    slug: str,
) -> list[BlueprintModule]:
    modules: list[BlueprintModule] = []
    grouped_by_target: dict[str, list[tuple[str, list[dict[str, str]]]]] = {}

    for domain_key, ac_list in sorted(domains.items()):
        verb, target = domain_key.split("_", 1)
        grouped_by_target.setdefault(target, []).append((domain_key, ac_list))

    for target, domain_entries in sorted(grouped_by_target.items()):
        module_name = target.replace(" ", "_").replace("-", "_")
        module_path = f"src/{module_name}.py"
        all_ac_ids: list[str] = []
        all_ac_texts: list[str] = []

        for domain_key, ac_list in sorted(domain_entries):
            for ac in ac_list:
                ac_id = _extract_ac_ids(ac.get("full_text", ""))
                all_ac_ids.extend(ac_id)
                all_ac_texts.append(ac["text"])

        unique_ac_ids = tuple(sorted(set(all_ac_ids)))
        responsibility = f"Manage {target.replace('_', ' ')} operations"

        modules.append(
            BlueprintModule(
                module_path=module_path,
                responsibility=responsibility,
                functions=(),
                ac_ids=unique_ac_ids,
            )
        )

    return modules


def _generate_function_signatures(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintFunction]:
    from .blueprint_models import _PARAMETER_PATTERNS

    functions: list[BlueprintFunction] = []

    for ac in ac_list:
        text = ac["text"]
        verb = ac.get("verb", "process")
        target = ac.get("target", "item")
        ac_ids = _extract_ac_ids(ac.get("full_text", ""))

        func_name = f"{verb}_{target.replace(' ', '_').replace('-', '_')}"

        parameters: list[str] = []
        for pattern in _PARAMETER_PATTERNS:
            match = pattern.search(text)
            if match:
                param = match.group(1).strip()
                param_name = param.replace(" ", "_").replace("-", "_")
                if param_name not in parameters:
                    parameters.append(param_name)

        if not parameters:
            parameters = [target.replace(" ", "_")]

        return_type = "bool"
        if any(w in text.lower() for w in ("return", "provide", "give", "yield", "produce")):
            return_type = target.replace(" ", "_").title()
        elif any(w in text.lower() for w in ("list", "all", "collection", "items")):
            return_type = f"list[{target.replace(' ', '_').title()}]"

        description = text.strip()

        functions.append(
            BlueprintFunction(
                name=func_name,
                parameters=tuple(parameters),
                return_type=return_type,
                description=description,
                ac_ids=ac_ids,
            )
        )

    return functions
