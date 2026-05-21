from __future__ import annotations

import re

from ..features import parse_acceptance_criteria
from ..proposer import TARGET_NOUNS

from .blueprint_models import (
    _AC_RE,
    _BEHAVIORAL_VERBS,
    _NOUN_PHRASE_RE,
    _SHALL_RE,
)


def _extract_ac_ids(text: str) -> tuple[str, ...]:
    return tuple(sorted({m.group(0).upper() for m in _AC_RE.finditer(text)}))


def _has_shall(text: str) -> bool:
    return bool(_SHALL_RE.search(text))


def _extract_behavioral_verb(text: str) -> str | None:
    lower = text.lower()
    for verb in _BEHAVIORAL_VERBS:
        if re.search(rf"\b{re.escape(verb)}\b", lower):
            return verb
    return None


def _extract_target_noun(text: str) -> str:
    lower = text.lower()
    for noun in TARGET_NOUNS:
        if re.search(rf"\b{re.escape(noun)}\b", lower):
            return noun
    match = _NOUN_PHRASE_RE.search(text)
    if match:
        return match.group(1).strip()
    return "component"


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
    "_extract_ac_ids",
    "_extract_behavioral_domains",
    "_extract_behavioral_verb",
    "_extract_target_noun",
    "_has_shall",
]
