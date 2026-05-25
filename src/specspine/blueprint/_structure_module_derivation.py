from __future__ import annotations

from ..features import validate_feature_slug

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import BlueprintModule

__all__ = [
    "_derive_module_structure",
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
