from __future__ import annotations

import re
from dataclasses import dataclass, field


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


__all__ = [
    "_AC_RE",
    "_BEHAVIORAL_VERBS",
    "_ENTITY_INDICATORS",
    "_ERROR_INDICATORS",
    "_NOUN_PHRASE_RE",
    "_PARAMETER_PATTERNS",
    "_SHALL_RE",
    "BlueprintDataEntity",
    "BlueprintErrorPath",
    "BlueprintFunction",
    "BlueprintModule",
    "BlueprintReport",
]
