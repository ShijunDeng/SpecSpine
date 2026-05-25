from __future__ import annotations

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import BlueprintFunction, _PARAMETER_PATTERNS

__all__ = [
    "_generate_function_signatures",
]


def _generate_function_signatures(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintFunction]:
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
