from __future__ import annotations

import re

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
]
