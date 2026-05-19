from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .features import (
    FEATURE_FILE_PATHS,
    FeatureBundleNotFoundError,
    feature_bundle_paths,
    parse_acceptance_criteria,
    validate_feature_slug,
)
from .proposer import ACTION_VERBS, MODIFIER_PREPOSITIONS, TARGET_NOUNS


@dataclass(frozen=True)
class BlueprintFunction:
    name: str
    parameters: tuple[str, ...]
    return_type: str
    description: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "description": self.description,
            "name": self.name,
            "parameters": list(self.parameters),
            "return_type": self.return_type,
        }


@dataclass(frozen=True)
class BlueprintModule:
    module_path: str
    responsibility: str
    functions: tuple[BlueprintFunction, ...]
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "functions": [fn.as_dict() for fn in self.functions],
            "module_path": self.module_path,
            "responsibility": self.responsibility,
        }


@dataclass(frozen=True)
class BlueprintDataEntity:
    name: str
    attributes: tuple[str, ...]
    description: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "attributes": list(self.attributes),
            "description": self.description,
            "name": self.name,
        }


@dataclass(frozen=True)
class BlueprintErrorPath:
    condition: str
    exception_type: str
    handling: str
    ac_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "ac_ids": list(self.ac_ids),
            "condition": self.condition,
            "exception_type": self.exception_type,
            "handling": self.handling,
        }


@dataclass(frozen=True)
class BlueprintReport:
    feature_id: str
    modules: tuple[BlueprintModule, ...]
    functions: tuple[BlueprintFunction, ...]
    data_entities: tuple[BlueprintDataEntity, ...]
    error_paths: tuple[BlueprintErrorPath, ...]
    coverage_summary: dict[str, object]
    safety_notes: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "coverage_summary": self.coverage_summary,
            "data_entities": [e.as_dict() for e in self.data_entities],
            "error_paths": [p.as_dict() for p in self.error_paths],
            "feature_id": self.feature_id,
            "functions": [f.as_dict() for f in self.functions],
            "modules": [m.as_dict() for m in self.modules],
            "safety_notes": list(self.safety_notes),
        }


_AC_RE = re.compile(r"\bAC\d{3,}\b", re.IGNORECASE)
_SHALL_RE = re.compile(r"\bSHALL\b")
_BEHAVIORAL_VERBS = {
    "add", "allow", "check", "create", "delete", "display", "enable",
    "fetch", "filter", "generate", "get", "handle", "import", "list",
    "load", "log", "monitor", "notify", "parse", "persist", "process",
    "read", "reject", "remove", "render", "report", "request", "restrict",
    "retrieve", "save", "send", "show", "sort", "store", "sync",
    "track", "transform", "update", "validate", "verify", "write",
}
_ERROR_INDICATORS = {
    "error", "fail", "failures", "invalid", "malformed", "missing",
    "refuse", "reject", "timeout", "unavailable", "unexpected", "unknown",
}
_ENTITY_INDICATORS = {
    "entity", "object", "model", "record", "item", "document", "resource",
    "config", "configuration", "setting", "profile", "user", "account",
    "data", "metadata", "payload", "result", "response", "request",
}
_NOUN_PHRASE_RE = re.compile(
    r"\b(?:the|a|an)\s+([a-z][a-z0-9_\-\s]*?(?:s\b|\b))",
    re.IGNORECASE,
)
_PARAMETER_PATTERNS = [
    re.compile(r"\bfor\s+(?:the\s+)?([a-z][a-z0-9_\-\s]*?)\b", re.IGNORECASE),
    re.compile(r"\b(?:with|using)\s+(?:the\s+)?([a-z][a-z0-9_\-\s]*?)\b", re.IGNORECASE),
    re.compile(r"\b(?:from|in)\s+(?:the\s+)?([a-z][a-z0-9_\-\s]*?)\b", re.IGNORECASE),
    re.compile(r"\bif\s+(?:the\s+)?([a-z][a-z0-9_\-\s]*?)\b", re.IGNORECASE),
    re.compile(r"\bwhen\s+(?:the\s+)?([a-z][a-z0-9_\-\s]*?)\b", re.IGNORECASE),
]


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


def render_blueprint_json(report: BlueprintReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def render_blueprint_text(report: BlueprintReport) -> str:
    lines = [
        f"Implementation Blueprint: {report.feature_id}",
        "",
        f"Coverage: {report.coverage_summary['modules_total']} modules, "
        f"{report.coverage_summary['functions_total']} functions, "
        f"{report.coverage_summary['data_entities_total']} entities, "
        f"{report.coverage_summary['error_paths_total']} error paths, "
        f"{report.coverage_summary['unique_ac_covered']} ACs covered",
        "",
        "Modules:",
    ]

    if report.modules:
        for module in report.modules:
            lines.append(f"  {module.module_path}")
            lines.append(f"    Responsibility: {module.responsibility}")
            if module.functions:
                lines.append("    Functions:")
                for func in module.functions:
                    params = ", ".join(func.parameters)
                    lines.append(
                        f"      {func.name}({params}) -> {func.return_type}"
                    )
            ac_str = ", ".join(module.ac_ids) if module.ac_ids else "none"
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No modules derived from acceptance criteria.")

    lines.append("Data Entities:")
    if report.data_entities:
        for entity in report.data_entities:
            attrs = ", ".join(entity.attributes) if entity.attributes else "none"
            ac_str = ", ".join(entity.ac_ids) if entity.ac_ids else "none"
            lines.append(f"  {entity.name}")
            lines.append(f"    Attributes: {attrs}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No data entities identified.")

    lines.append("Error Paths:")
    if report.error_paths:
        for ep in report.error_paths:
            ac_str = ", ".join(ep.ac_ids) if ep.ac_ids else "none"
            lines.append(f"  Condition: {ep.condition}")
            lines.append(f"    Exception: {ep.exception_type}")
            lines.append(f"    Handling: {ep.handling}")
            lines.append(f"    AC: {ac_str}")
            lines.append("")
    else:
        lines.append("  No error paths detected.")

    lines.append("Safety Notes:")
    if report.safety_notes:
        for note in report.safety_notes:
            lines.append(f"  - {note}")
    else:
        lines.append("  None.")

    return "\n".join(lines) + "\n"
