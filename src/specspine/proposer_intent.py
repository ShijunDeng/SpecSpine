from __future__ import annotations

import re

from .workspace import normalize_template

__all__ = [
    "InvalidProposalIntent",
    "MAX_INTENT_CHARS",
    "ACTION_VERBS",
    "TARGET_NOUNS",
    "MODIFIER_PREPOSITIONS",
    "COMPONENT_SPLITTERS",
    "STOP_WORDS",
    "normalize_intent",
    "validate_intent",
    "parse_intent",
    "_extract_action",
    "_extract_target",
    "_extract_modifiers",
    "_build_modifier_phrase",
    "_normalize_modifier",
    "_normalize_to_base_form",
    "_singularize",
    "_truncation_warning",
]


class InvalidProposalIntent(ValueError):
    """Raised when natural-language proposal text is empty or not meaningful."""


MAX_INTENT_CHARS = 5000

ACTION_VERBS = (
    "add",
    "create",
    "implement",
    "build",
    "support",
    "enable",
    "integrate",
    "introduce",
    "develop",
    "design",
    "extend",
    "provide",
    "generate",
    "configure",
    "display",
    "show",
    "hide",
    "remove",
    "delete",
    "update",
    "modify",
    "change",
    "allow",
    "permit",
    "restrict",
    "block",
    "track",
    "monitor",
    "validate",
    "verify",
    "test",
    "document",
    "migrate",
    "convert",
    "import",
    "export",
    "publish",
    "deploy",
    "render",
    "animate",
    "sync",
)

TARGET_NOUNS = (
    "feature",
    "toggle",
    "mode",
    "button",
    "page",
    "panel",
    "dialog",
    "modal",
    "menu",
    "sidebar",
    "header",
    "footer",
    "toolbar",
    "form",
    "input",
    "field",
    "dropdown",
    "select",
    "checkbox",
    "radio",
    "tab",
    "card",
    "list",
    "table",
    "chart",
    "graph",
    "widget",
    "component",
    "module",
    "service",
    "api",
    "endpoint",
    "handler",
    "middleware",
    "plugin",
    "extension",
    "adapter",
    "connector",
    "integration",
    "pipeline",
    "workflow",
    "report",
    "dashboard",
    "notification",
    "alert",
    "toast",
    "banner",
    "badge",
    "tooltip",
    "popover",
    "accordion",
    "carousel",
    "slider",
    "progress",
    "spinner",
    "loader",
    "skeleton",
    "theme",
    "layout",
    "template",
    "style",
    "animation",
    "transition",
    "routing",
    "navigation",
    "search",
    "filter",
    "sort",
    "pagination",
    "validation",
    "authentication",
    "authorization",
    "permission",
    "role",
    "setting",
    "config",
    "preference",
    "profile",
    "account",
    "session",
    "cache",
    "store",
    "database",
    "model",
    "schema",
    "migration",
    "seed",
    "fixture",
    "mock",
    "stub",
    "test",
    "spec",
    "doc",
    "documentation",
    "readme",
    "changelog",
    "version",
    "release",
    "build",
    "deploy",
    "ci",
    "cd",
    "pipeline",
    "hook",
    "trigger",
    "event",
    "listener",
    "subscriber",
    "publisher",
    "broker",
    "queue",
    "stream",
    "log",
    "logging",
    "metric",
    "monitor",
    "health",
    "status",
    "check",
    "gate",
    "policy",
    "rule",
    "constraint",
    "limit",
    "quota",
    "rate",
    "throttle",
    "retry",
    "timeout",
    "circuit",
    "breaker",
    "fallback",
    "default",
    "gateway",
    "payment",
    "tenant",
    "user",
    "group",
    "organization",
    "team",
    "project",
    "workspace",
    "environment",
    "server",
    "client",
    "proxy",
    "loadbalancer",
    "storage",
    "bucket",
    "container",
    "volume",
    "network",
    "firewall",
    "certificate",
    "token",
    "key",
    "secret",
    "password",
    "email",
    "message",
    "sms",
    "webhook",
    "callback",
    "response",
    "request",
    "header",
    "body",
    "payload",
    "file",
    "attachment",
    "image",
    "video",
    "audio",
    "document",
    "spreadsheet",
    "presentation",
    "archive",
    "backup",
    "snapshot",
    "restore",
    "import",
    "export",
    "sync",
    "notification",
    "realtime",
    "websocket",
    "sse",
    "polling",
    "subscription",
    "preference",
    "configuration",
    "registry",
    "catalog",
    "directory",
    "index",
    "lookup",
    "reference",
    "mapping",
    "translation",
    "localization",
    "internationalization",
)

MODIFIER_PREPOSITIONS = (
    "with",
    "when",
    "if",
    "for",
    "to",
    "where",
    "while",
    "unless",
    "after",
    "before",
    "during",
    "without",
    "by",
    "via",
    "through",
    "on",
    "in",
    "at",
    "from",
    "between",
    "among",
)

COMPONENT_SPLITTERS = re.compile(r"\band\b|\bwith\b|\bplus\b|;")

STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them",
    "my", "your", "his", "its", "our", "their",
    "mine", "yours", "hers", "ours", "theirs",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
    "this", "that", "these", "those",
    "what", "which", "who", "whom", "whose",
    "and", "but", "or", "nor", "for", "yet", "so",
    "if", "then", "than", "else",
    "because", "as", "until", "while", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "many", "much", "some", "any",
    "no", "not", "only", "own", "same", "such",
    "just", "also", "too", "very", "really", "quite", "rather",
    "of", "in", "to", "for", "with", "on", "at", "from", "by", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "again", "further", "once", "here", "there",
    "up", "down", "out", "off", "over", "under", "more", "most",
    "other", "another", "even", "still", "already", "always", "never",
    "sometimes", "often", "usually", "generally", "commonly",
})


def _truncation_warning(original_length: int) -> str:
    return (
        f"Proposal intent exceeded {MAX_INTENT_CHARS} characters and was "
        f"truncated from {original_length} characters."
    )


def normalize_intent(intent: str) -> tuple[str, list[str]]:
    normalized = intent.strip()
    if not normalized:
        raise InvalidProposalIntent("Proposal intent must not be empty.")
    if not any(char.isalnum() for char in normalized):
        raise InvalidProposalIntent(
            "Proposal intent must include meaningful words or numbers."
        )
    if len(normalized) > MAX_INTENT_CHARS:
        return normalized[:MAX_INTENT_CHARS], [_truncation_warning(len(normalized))]
    return normalized, []


def validate_intent(intent: str) -> str:
    normalized, _warnings = normalize_intent(intent)
    return normalized


def parse_intent(intent: str) -> dict:
    text = validate_intent(intent).lower()

    raw_components = COMPONENT_SPLITTERS.split(text)
    components = [c.strip() for c in raw_components if c.strip()]
    is_complex = len(components) > 1

    if is_complex:
        primary = components[0]
    else:
        primary = text

    action = _extract_action(primary)
    target = _extract_target(primary)
    modifiers = _extract_modifiers(primary)

    return {
        "action": action,
        "target": target,
        "modifiers": modifiers,
        "components": components,
        "is_complex": is_complex,
    }


def _extract_action(text: str) -> str:
    words = text.split()
    for word in words:
        cleaned = word.strip(".,;:!?()[]{}'\"")
        if cleaned in ACTION_VERBS:
            return cleaned
    return "implement"


def _singularize(word: str) -> str:
    """Convert plural word to singular form using simple rules."""
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("ses") or word.endswith("xes") or word.endswith("zes") or word.endswith("ches") or word.endswith("shes"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _normalize_to_base_form(word: str) -> str:
    """Normalize word to base form for matching against TARGET_NOUNS."""
    stripped = word.strip(".,;:!?()[]{}'\"")
    if not stripped:
        return stripped
    singular = _singularize(stripped)
    if stripped.endswith("ing") and len(stripped) > 4:
        base = stripped[:-3]
        if base + "e" in TARGET_NOUNS:
            return base + "e"
        if base in TARGET_NOUNS:
            return base
    return singular


def _extract_target(text: str) -> str:
    words = text.split()
    found_nouns = []
    preposition_nouns = []
    in_preposition_phrase = False
    for i, word in enumerate(words):
        cleaned = word.strip(".,;:!?()[]{}'\"")
        normalized = _normalize_to_base_form(cleaned)
        if normalized in TARGET_NOUNS:
            if in_preposition_phrase:
                preposition_nouns.append(normalized)
            else:
                found_nouns.append(normalized)
        if cleaned in MODIFIER_PREPOSITIONS:
            in_preposition_phrase = True
        elif cleaned not in ("and", "or", "but", "the", "a", "an", "this", "that"):
            if i > 0 and words[i-1].strip(".,;:!?()[]{}'\"") not in MODIFIER_PREPOSITIONS:
                in_preposition_phrase = False
    if found_nouns:
        return found_nouns[-1]
    if preposition_nouns:
        return preposition_nouns[0]
    return "feature"


def _extract_modifiers(text: str) -> list:
    modifiers = []
    words = text.split()
    action_words = set(ACTION_VERBS)
    i = 0
    while i < len(words):
        cleaned = words[i].strip(".,;:!?()[]{}'\"")
        if cleaned in MODIFIER_PREPOSITIONS:
            rest_words = words[i:]
            modifier_text = _build_modifier_phrase(rest_words, action_words)
            modifier = modifier_text.strip().rstrip(".")
            if modifier and modifier not in modifiers and len(modifier) > len(cleaned):
                modifiers.append(modifier)
                i += len(modifier.split())
                continue
        i += 1
    return modifiers


def _build_modifier_phrase(words: list, action_words: set) -> str:
    """Build a meaningful modifier phrase from words starting with a preposition."""
    if not words:
        return ""
    prep = words[0].strip(".,;:!?()[]{}'\"")
    phrase_words = []
    for i in range(1, len(words)):
        word = words[i].strip(".,;:!?()[]{}'\"")
        if i == 1 and word.lower() in action_words:
            break
        if word.lower() in MODIFIER_PREPOSITIONS and phrase_words:
            if len(phrase_words) >= 2:
                break
        if word.lower() in action_words and phrase_words:
            prev_word = phrase_words[-1].strip(".,;:!?()[]{}'\"").lower() if phrase_words else ""
            if prev_word not in ("the", "a", "an", "this", "that", "these", "those", "my", "your", "their", "our"):
                pass
            elif len(phrase_words) >= 2:
                break
        phrase_words.append(words[i])
    if phrase_words:
        return prep + " " + " ".join(phrase_words)
    return prep


def _normalize_modifier(modifier: str) -> str:
    from .proposer_criteria import _make_meaningful_condition
    result = modifier
    for prep in MODIFIER_PREPOSITIONS:
        if result.startswith(prep + " "):
            rest = result[len(prep):].strip()
            if rest:
                result = _make_meaningful_condition(rest, prep)
                break
    if not result or len(result) < 3:
        return "the necessary conditions are met"
    return result
