from __future__ import annotations

from ..features import parse_acceptance_criteria
from ._behavioral_extractors import _extract_behavioral_verb, _extract_target_noun


def _extract_behavioral_domains(
    spec_content: str,
    slug: str,
) -> dict[str, list[dict[str, str]]]:
    items = parse_acceptance_criteria(spec_content, source_file=f"specs/features/{slug}.md")
    domains: dict[str, list[dict[str, str]]] = {}

    for item in items:
        if not item.done:
            text = item.text
        else:
            text = item.text

        shall_text = text.split("SHALL", 1)[-1].strip() if "SHALL" in text else text
        verb = _extract_behavioral_verb(shall_text) or "process"
        target = _extract_target_noun(shall_text)
        domain_key = f"{verb}_{target}"

        domains.setdefault(domain_key, []).append({
            "text": shall_text,
            "full_text": text,
            "verb": verb,
            "target": target,
        })

    return domains


def _collect_all_ac_items(spec_content: str, slug: str) -> list[dict[str, str]]:
    items = parse_acceptance_criteria(spec_content, source_file=f"specs/features/{slug}.md")
    result: list[dict[str, str]] = []
    for item in items:
        full_text = item.text
        shall_text = full_text.split("SHALL", 1)[-1].strip() if "SHALL" in full_text else full_text
        verb = _extract_behavioral_verb(shall_text) or "process"
        target = _extract_target_noun(shall_text)
        result.append({
            "text": shall_text,
            "full_text": full_text,
            "verb": verb,
            "target": target,
        })
    return result


__all__ = [
    "_collect_all_ac_items",
    "_extract_behavioral_domains",
]
