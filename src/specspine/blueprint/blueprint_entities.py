from __future__ import annotations

import re

from .blueprint_extraction import _extract_ac_ids
from .blueprint_models import (
    BlueprintDataEntity,
    BlueprintErrorPath,
    _ENTITY_INDICATORS,
    _ERROR_INDICATORS,
    _NOUN_PHRASE_RE,
)

__all__ = [
    "_derive_error_paths",
    "_identify_data_entities",
]


def _identify_data_entities(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintDataEntity]:
    entities: dict[str, BlueprintDataEntity] = {}

    for ac in ac_list:
        text = ac.get("full_text", ac["text"])
        ac_ids = _extract_ac_ids(text)
        target = ac.get("target", "")

        entity_name: str | None = None
        for indicator in _ENTITY_INDICATORS:
            pattern = re.compile(rf"\b(?:the\s+)?(\w+)\s+{indicator}", re.IGNORECASE)
            match = pattern.search(text)
            if match:
                candidate = match.group(1).lower()
                if candidate not in ("a", "an", "the", "new", "one", "any", "each", "every", "some", "another"):
                    entity_name = candidate
                    break
        if entity_name is None:
            if target and target not in ("a", "an", "the", "new"):
                entity_name = target
            else:
                match = _NOUN_PHRASE_RE.search(text)
                if match:
                    entity_name = match.group(1).strip().lower().split()[0]
                else:
                    continue

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

    return sorted(entities.values(), key=lambda e: e.name)


def _derive_error_paths(
    ac_list: list[dict[str, str]],
    slug: str,
) -> list[BlueprintErrorPath]:
    error_paths: list[BlueprintErrorPath] = []

    for ac in ac_list:
        text = ac.get("full_text", ac["text"])
        lower = text.lower()
        ac_ids = _extract_ac_ids(text)

        if not any(indicator in lower for indicator in _ERROR_INDICATORS):
            continue

        condition = text.strip()
        if "when" in lower:
            cond_match = re.search(r"when\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
            if cond_match:
                condition = cond_match.group(1).strip()
        elif "if" in lower:
            cond_match = re.search(r"if\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
            if cond_match:
                condition = cond_match.group(1).strip()

        exception_type = "ValueError"
        if any(w in lower for w in ("missing", "not found", "absent")):
            exception_type = "FileNotFoundError"
        elif any(w in lower for w in ("timeout", "unavailable")):
            exception_type = "TimeoutError"
        elif any(w in lower for w in ("reject", "refuse", "invalid")):
            exception_type = "ValueError"
        elif any(w in lower for w in ("error", "fail")):
            exception_type = "RuntimeError"

        handling = f"Log the error and return a failure indication for: {condition}"

        error_paths.append(
            BlueprintErrorPath(
                condition=condition,
                exception_type=exception_type,
                handling=handling,
                ac_ids=ac_ids,
            )
        )

    return error_paths
