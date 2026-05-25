from __future__ import annotations

import re

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import BlueprintDataEntity
from ._entity_naming import _extract_entity_name

__all__ = [
    "_extract_attributes",
    "_merge_entity",
    "_identify_data_entities",
]


def _extract_attributes(text: str) -> list[str]:
    attrs: list[str] = []
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in ("with", "has", "containing", "including"):
            rest = " ".join(words[i + 1:])
            parts = re.split(r"\band\b|,|\bor\b", rest)
            for part in parts:
                cleaned = part.strip().rstrip(".")
                if cleaned and len(cleaned) > 2:
                    attrs.append(cleaned.replace(" ", "_"))
    return attrs


def _merge_entity(
    entities: dict[str, BlueprintDataEntity],
    entity_name: str,
    attrs: list[str],
    ac_ids: tuple[str, ...],
) -> None:
    if entity_name in entities:
        existing = entities[entity_name]
        merged_attrs = list(existing.attributes) + [a for a in attrs if a not in existing.attributes]
        merged_ac_ids = tuple(sorted(set(existing.ac_ids + ac_ids)))
        entities[entity_name] = BlueprintDataEntity(
            name=entity_name,
            attributes=tuple(merged_attrs),
            description=existing.description,
            ac_ids=merged_ac_ids,
        )
    else:
        entities[entity_name] = BlueprintDataEntity(
            name=entity_name,
            attributes=tuple(attrs),
            description=f"Data entity for {entity_name}",
            ac_ids=ac_ids,
        )


def _identify_data_entities(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintDataEntity]:
    entities: dict[str, BlueprintDataEntity] = {}

    for ac in ac_list:
        text = ac.get("full_text", ac["text"])
        ac_ids = _extract_ac_ids(text)
        target = ac.get("target", "")

        entity_name = _extract_entity_name(text, target)
        if entity_name is None:
            continue

        attrs = _extract_attributes(text)
        _merge_entity(entities, entity_name, attrs, ac_ids)

    return sorted(entities.values(), key=lambda e: e.name)
