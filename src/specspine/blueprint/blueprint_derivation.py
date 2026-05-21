from __future__ import annotations

import re
from pathlib import Path

from ..features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    validate_feature_slug,
)
from ..proposer import ACTION_VERBS, MODIFIER_PREPOSITIONS, TARGET_NOUNS

from .blueprint_extraction import (
    _collect_all_ac_items,
    _extract_ac_ids,
    _extract_behavioral_domains,
    _extract_behavioral_verb,
    _extract_target_noun,
)
from .blueprint_models import (
    _ENTITY_INDICATORS,
    _ERROR_INDICATORS,
    _NOUN_PHRASE_RE,
    _PARAMETER_PATTERNS,
    BlueprintDataEntity,
    BlueprintErrorPath,
    BlueprintFunction,
    BlueprintModule,
    BlueprintReport,
)


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


def _compute_coverage_summary(
    modules: list[BlueprintModule],
    functions: list[BlueprintFunction],
    entities: list[BlueprintDataEntity],
    error_paths: list[BlueprintErrorPath],
) -> dict[str, object]:
    all_ac_ids: set[str] = set()
    for module in modules:
        all_ac_ids.update(module.ac_ids)
    for func in functions:
        all_ac_ids.update(func.ac_ids)
    for entity in entities:
        all_ac_ids.update(entity.ac_ids)
    for ep in error_paths:
        all_ac_ids.update(ep.ac_ids)

    return {
        "modules_total": len(modules),
        "functions_total": len(functions),
        "data_entities_total": len(entities),
        "error_paths_total": len(error_paths),
        "unique_ac_covered": len(all_ac_ids),
        "ac_ids_covered": sorted(all_ac_ids),
    }


def _derive_safety_notes(
    functions: list[BlueprintFunction],
    error_paths: list[BlueprintErrorPath],
) -> tuple[str, ...]:
    notes: list[str] = []

    has_validation = any("validate" in f.name.lower() or "verify" in f.name.lower() for f in functions)
    if not has_validation:
        notes.append("No explicit validation function detected; add input validation before processing.")

    has_error_handling = bool(error_paths)
    if not has_error_handling:
        notes.append("No error paths detected; ensure all external interactions have failure handling.")

    has_persistence = any(w in f.name.lower() for w in ("save", "store", "persist", "write") for f in functions)
    if has_persistence:
        notes.append("Persistence operations detected; verify transactional integrity and rollback paths.")

    notes.append("Review all generated function signatures for correct parameter types and return values.")
    notes.append("Verify error handling covers all identified failure conditions before implementation.")

    return tuple(notes)


def build_spec_code_blueprint(root: Path, slug: str) -> BlueprintReport:
    slug = validate_feature_slug(slug)
    resolved_root = root.expanduser().resolve()
    paths = feature_bundle_paths(resolved_root, slug)
    spec_path = paths["spec"]

    if not spec_path.exists():
        raise FeatureBundleNotFoundError(
            slug=slug,
            root=resolved_root,
            missing_paths=tuple(paths.values()),
        )

    spec_content = spec_path.read_text(encoding="utf-8")
    ac_list = _collect_all_ac_items(spec_content, slug)

    if not ac_list:
        domains: dict[str, list[dict[str, str]]] = {}
    else:
        domains = _extract_behavioral_domains(spec_content, slug)

    modules = _derive_module_structure(domains, slug)

    functions = _generate_function_signatures(ac_list, slug)

    entities = _identify_data_entities(ac_list, slug)

    error_paths = _derive_error_paths(ac_list, slug)

    module_functions: dict[str, list[BlueprintFunction]] = {}
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


__all__ = [
    "_compute_coverage_summary",
    "_derive_error_paths",
    "_derive_module_structure",
    "_derive_safety_notes",
    "_generate_function_signatures",
    "_identify_data_entities",
    "build_spec_code_blueprint",
]
