from __future__ import annotations

import re
from textwrap import dedent

from .workspace import normalize_template


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

EARS_PATTERNS = (
    "event-driven",
    "conditional",
    "simple",
    "ubiquitous",
)

BEHAVIOR_PATTERNS = {
    "event-driven": "The system SHALL {behavior} when {condition}",
    "conditional": "The system SHALL {behavior} if {precondition}",
    "simple": "The system SHALL {behavior}",
    "ubiquitous": "The system SHALL {behavior} where {context}",
}

SLUG_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


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


def generate_slug_from_intent(intent: str) -> str:
    normalized = validate_intent(intent)
    tokens = re.findall(r"[a-z0-9]+", normalized.lower())
    filtered = [token for token in tokens if token not in SLUG_STOP_WORDS]
    selected = filtered[:5] or tokens[:5] or ["proposal"]
    slug = "-".join(selected)

    if not slug[0].isalnum():
        slug = f"proposal-{slug}"
    if not slug[-1].isalnum():
        slug = f"{slug}-proposal"

    from .features import validate_feature_slug

    return validate_feature_slug(slug)


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


def _make_meaningful_condition(phrase: str, prep: str) -> str:
    """Transform a noun phrase into a more meaningful condition based on the preposition."""
    condition_templates = {
        "for": [
            "multi-tenant", "all users", "admin users", "guest users",
            "external users", "internal users", "premium users", "free users",
        ],
        "when": [
            "payment fails", "error occurs", "timeout", "connection lost",
            "user logs in", "user logs out", "data changes", "status updates",
        ],
        "if": [
            "user is authenticated", "user has permission", "data is valid",
            "feature is enabled", "service is available",
        ],
        "with": [
            "analytics", "persistence", "real-time updates", "caching",
            "logging enabled", "error handling", "retry logic",
        ],
        "without": [
            "interrupting the user", "data loss", "downtime",
        ],
        "during": [
            "peak hours", "maintenance window", "migration",
        ],
        "after": [
            "user confirmation", "validation passes", "approval",
        ],
        "before": [
            "deployment", "release", "user action",
        ],
    }
    phrase_lower = phrase.lower()
    for template in condition_templates.get(prep, []):
        if template in phrase_lower:
            if prep == "for":
                return f"the feature is needed {prep} {phrase}"
            elif prep == "when":
                return f"{phrase}"
            elif prep == "if":
                return f"{phrase}"
            elif prep == "with":
                return f"{prep} {phrase} enabled"
            else:
                return f"{prep} {phrase}"
    if len(phrase.split()) <= 2:
        return f"the requirement {prep} {phrase} applies"
    return f"{prep} {phrase}"


def _get_action_verb_form(action: str, form: str = "base") -> str:
    """Convert action verb to appropriate grammatical form."""
    common_verbs = {
        "add": {"base": "add", "gerund": "adding", "past": "added"},
        "create": {"base": "create", "gerund": "creating", "past": "created"},
        "implement": {"base": "implement", "gerund": "implementing", "past": "implemented"},
        "build": {"base": "build", "gerund": "building", "past": "built"},
        "enable": {"base": "enable", "gerund": "enabling", "past": "enabled"},
        "support": {"base": "support", "gerund": "supporting", "past": "supported"},
        "integrate": {"base": "integrate", "gerund": "integrating", "past": "integrated"},
        "introduce": {"base": "introduce", "gerund": "introducing", "past": "introduced"},
        "develop": {"base": "develop", "gerund": "developing", "past": "developed"},
        "design": {"base": "design", "gerund": "designing", "past": "designed"},
        "extend": {"base": "extend", "gerund": "extending", "past": "extended"},
        "provide": {"base": "provide", "gerund": "providing", "past": "provided"},
        "generate": {"base": "generate", "gerund": "generating", "past": "generated"},
        "configure": {"base": "configure", "gerund": "configuring", "past": "configured"},
        "display": {"base": "display", "gerund": "displaying", "past": "displayed"},
        "show": {"base": "show", "gerund": "showing", "past": "showed"},
        "hide": {"base": "hide", "gerund": "hiding", "past": "hid"},
        "remove": {"base": "remove", "gerund": "removing", "past": "removed"},
        "delete": {"base": "delete", "gerund": "deleting", "past": "deleted"},
        "update": {"base": "update", "gerund": "updating", "past": "updated"},
        "modify": {"base": "modify", "gerund": "modifying", "past": "modified"},
        "change": {"base": "change", "gerund": "changing", "past": "changed"},
        "allow": {"base": "allow", "gerund": "allowing", "past": "allowed"},
        "permit": {"base": "permit", "gerund": "permitting", "past": "permitted"},
        "restrict": {"base": "restrict", "gerund": "restricting", "past": "restricted"},
        "block": {"base": "block", "gerund": "blocking", "past": "blocked"},
        "track": {"base": "track", "gerund": "tracking", "past": "tracked"},
        "monitor": {"base": "monitor", "gerund": "monitoring", "past": "monitored"},
        "validate": {"base": "validate", "gerund": "validating", "past": "validated"},
        "verify": {"base": "verify", "gerund": "verifying", "past": "verified"},
        "test": {"base": "test", "gerund": "testing", "past": "tested"},
        "document": {"base": "document", "gerund": "documenting", "past": "documented"},
        "migrate": {"base": "migrate", "gerund": "migrating", "past": "migrated"},
        "convert": {"base": "convert", "gerund": "converting", "past": "converted"},
        "import": {"base": "import", "gerund": "importing", "past": "imported"},
        "export": {"base": "export", "gerund": "exporting", "past": "exported"},
        "publish": {"base": "publish", "gerund": "publishing", "past": "published"},
        "deploy": {"base": "deploy", "gerund": "deploying", "past": "deployed"},
        "render": {"base": "render", "gerund": "rendering", "past": "rendered"},
        "animate": {"base": "animate", "gerund": "animating", "past": "animated"},
        "sync": {"base": "sync", "gerund": "syncing", "past": "synced"},
    }
    if action in common_verbs:
        return common_verbs[action].get(form, action)
    return _conjugate_verb(action, form)


def _conjugate_verb(verb: str, form: str) -> str:
    """Apply English conjugation rules for verbs not in the explicit table."""
    if form == "base":
        return verb
    if form == "gerund":
        return _to_gerund(verb)
    if form == "past":
        return _to_past(verb)
    return verb


def _to_gerund(verb: str) -> str:
    """Convert verb to gerund (-ing) form."""
    if not verb:
        return verb
    if verb.endswith("ie"):
        return verb[:-2] + "ying"
    if verb.endswith("ee"):
        return verb + "ing"
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ing"
    return verb + "ing"


def _to_past(verb: str) -> str:
    """Convert verb to past tense (-ed) form."""
    if not verb:
        return verb
    if verb.endswith("e"):
        return verb + "d"
    if verb.endswith("y") and len(verb) >= 2 and verb[-2] not in "aeiou":
        return verb[:-1] + "ied"
    if len(verb) >= 3 and _is_cvc(verb) and _is_stressed_syllable(verb):
        return verb + verb[-1] + "ed"
    return verb + "ed"


def _is_cvc(word: str) -> bool:
    """Check if word ends in consonant-vowel-consonant pattern."""
    if len(word) < 3:
        return False
    vowels = set("aeiou")
    return (word[-3] not in vowels and
            word[-2] in vowels and
            word[-1] not in vowels)


def _is_stressed_syllable(word: str) -> bool:
    """Heuristic: single syllable or stress on last syllable."""
    if len(word) <= 2:
        return True
    vowels = set("aeiou")
    vowel_count = sum(1 for c in word.lower() if c in vowels)
    return vowel_count <= 2


def generate_ears_criteria(parsed_intent: dict) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    modifiers = parsed_intent["modifiers"]
    components = parsed_intent["components"]
    is_complex = parsed_intent["is_complex"]

    action_base = _get_action_verb_form(action, "base")
    action_gerund = _get_action_verb_form(action, "gerund")
    action_past = _get_action_verb_form(action, "past")

    criteria: list[dict] = []
    counter = 1

    if modifiers:
        first_mod = modifiers[0]
        normalized_mod = _normalize_modifier(first_mod)
        criteria.append(
            {
                "id": f"AC{counter:03d}",
                "text": BEHAVIOR_PATTERNS["conditional"].format(
                    behavior=f"allow users to {action_base} the {target}",
                    precondition=normalized_mod,
                ),
                "pattern": "conditional",
            }
        )
        counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["event-driven"].format(
                behavior=f"allow the user to {action_base} the {target}",
                condition=f"the user requests to {action_base} the {target}",
            ),
            "pattern": "event-driven",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["simple"].format(
                behavior=f"validate all inputs before {action_gerund} the {target}",
            ),
            "pattern": "simple",
        }
    )
    counter += 1

    criteria.append(
        {
            "id": f"AC{counter:03d}",
            "text": BEHAVIOR_PATTERNS["ubiquitous"].format(
                behavior=f"handle errors gracefully when {action_gerund} fails",
                context=f"any error occurs during the operation",
            ),
            "pattern": "ubiquitous",
        }
    )
    counter += 1

    if is_complex and len(components) > 1:
        for component in components[1:3]:
            criteria.append(
                {
                    "id": f"AC{counter:03d}",
                    "text": BEHAVIOR_PATTERNS["simple"].format(
                        behavior=f"support {component} as part of the overall feature",
                    ),
                    "pattern": "simple",
                }
            )
            counter += 1

    if len(criteria) < 3:
        while len(criteria) < 3:
            criteria.append(
                {
                    "id": f"AC{counter:03d}",
                    "text": BEHAVIOR_PATTERNS["simple"].format(
                        behavior=f"handle edge cases related to {action_gerund} the {target}",
                    ),
                    "pattern": "simple",
                }
            )
            counter += 1

    return criteria[:8]


def generate_tasks(parsed_intent: dict, criteria: list[dict]) -> list[dict]:
    action = parsed_intent["action"]
    target = parsed_intent["target"]
    tasks: list[dict] = []

    tasks.append(
        {
            "id": "T001",
            "text": f"Set up file structure and module scaffolding for {action} {target}",
            "boundary": f"Project structure and module creation for {target}",
            "depends": "none",
        }
    )

    for criterion in criteria[:3]:
        criterion_text = criterion["text"].replace("The system SHALL ", "")
        tasks.append(
            {
                "id": f"T{len(tasks) + 1:03d}",
                "text": f"Implement core logic: {criterion_text}",
                "boundary": f"Core behavior for {criterion['pattern']} criterion {criterion['id']}",
                "depends": "T001",
            }
        )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Wire CLI interface and validate {action} {target} integration",
            "boundary": f"CLI integration and validation for {target}",
            "depends": ", ".join(t["id"] for t in tasks[1:]),
        }
    )

    tasks.append(
        {
            "id": f"T{len(tasks) + 1:03d}",
            "text": f"Add unit tests, integration tests, and documentation for {action} {target}",
            "boundary": f"Test suite and documentation for {target}",
            "depends": tasks[-1]["id"],
        }
    )

    return tasks


def generate_quality_checks(criteria: list[dict]) -> list[str]:
    checks: list[str] = []
    for criterion in criteria:
        checks.append(
            f"Verify {criterion['id']}: {criterion['text']}"
        )
    return checks


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def build_proposal_content(
    slug: str,
    intent: str,
    *,
    priority: str = "medium",
    owner: str = "unassigned",
    milestone: str = "unassigned",
    target_release: str = "unassigned",
    project: str = "unassigned",
    effort: str = "unknown",
) -> dict[str, str]:
    from .features import FEATURE_FILE_PATHS

    intent = validate_intent(intent)
    resolved_slug = slug
    title = _slug_to_title(resolved_slug)
    parsed = parse_intent(intent)
    criteria = generate_ears_criteria(parsed)
    tasks = generate_tasks(parsed, criteria)
    quality_checks = generate_quality_checks(criteria)

    ac_lines = "\n".join(f"- [ ] {c['id']} {c['text']}" for c in criteria)
    edge_case_lines = _generate_edge_cases(parsed)
    constraint_lines = _generate_constraints(parsed)
    traceability_lines = _generate_traceability_notes(resolved_slug, criteria)

    task_lines = "\n".join(
        f"- [ ] {t['id']}: {t['text']}\n  _Boundary: {t['boundary']}\n  _Depends: {t['depends']}"
        for t in tasks
    )
    dependency_lines = _generate_dependencies(parsed)
    open_questions_lines = _generate_open_questions(parsed)

    quality_check_lines = "\n".join(
        f"- [ ] QC{i+1:03d}: {check}" for i, check in enumerate(quality_checks)
    )
    test_coverage_lines = "\n".join(
        f"- [ ] {c['id']} -> tests/test_{resolved_slug.replace('-', '_')}.py"
        for c in criteria
    )
    test_plan_lines = _generate_test_plan(parsed, criteria)

    why_text = _generate_why(parsed, intent)

    spec_content = normalize_template(f"""
# {title}

Feature ID: {resolved_slug}
Status: proposed
Priority: {priority}
Owner: {owner}
Milestone: {milestone}
Target Release: {target_release}
Project: {project}
Effort: {effort}

## Why

{why_text}

## Users

- End users who need to {parsed['action']} the {parsed['target']}
- Developers maintaining the {parsed['target']} functionality
- Operators configuring the {parsed['target']} in production

## Scope

- {_generate_scope(parsed)}
- Support for {parsed['action']}ing the {parsed['target']} in all relevant contexts
- Integration with existing system components

## Non-Goals

- This feature will not modify unrelated system behavior
- Migration of existing data is out of scope unless explicitly required
- Third-party integrations beyond core functionality

## Acceptance Criteria

{ac_lines}

## Edge Cases

{edge_case_lines}

## Constraints

{constraint_lines}

## Traceability Notes

{traceability_lines}
""")

    execution_content = normalize_template(f"""
# {title} Execution

Feature ID: {resolved_slug}
Status: proposed
Why: {why_text}

## Milestones

- M1: Module scaffolding and file structure in place
- M2: Core {parsed['action']} logic implemented for all acceptance criteria
- M3: CLI integration and validation complete
- M4: Tests written and passing, documentation updated

## Tasks

{task_lines}

## Dependencies

{dependency_lines}

## Open Questions

{open_questions_lines}

## Agent Handoff

- Run `specspine feature handoff {resolved_slug} . --json` before implementation or review handoff.
- Run `specspine adapters handoff {resolved_slug} . --json` when OpenSpec, Spec Kit, or Superpowers adapter context is needed.
- Run `specspine feature tasks {resolved_slug} . --json` for the focused implementation checklist.
- Run `specspine feature task-issues {resolved_slug} . --json` to draft one local GitHub issue per execution task.
- Run `specspine feature trace {resolved_slug} . --json` to inspect acceptance, tasks, quality checks, test plan, and gaps.
- Run `specspine feature tests {resolved_slug} . --json` to build the acceptance-test packet.
- Run `specspine tests impact . --feature {resolved_slug} --json` to inspect local source-to-test impact recommendations.
- Run `specspine consistency scan . --feature {resolved_slug} --json` to inspect local spec-code-test-doc drift.
- Run `specspine hygiene scan . --json` to inspect generated artifacts and denylisted repository residue.
- Run `specspine retrospective report . --json` before planning the next iteration.
- Run `specspine coverage plan . --feature {resolved_slug} --json` when missing AC coverage needs read-only remediation steps.
- Run `specspine verify matrix {resolved_slug} . --json` to inspect AC-level verification evidence.
- Run `specspine change risk . --feature {resolved_slug} --json` to inspect local changed-path risk evidence.
- Run `specspine security cues . --feature {resolved_slug} --json` to inspect local security-sensitive review cues.
- Run `specspine provenance manifest . --feature {resolved_slug} --json` to hash local evidence artifacts before review or archive.
- Run `specspine review packet . --feature {resolved_slug} --json` to compose local pre-merge review evidence.
- Run `specspine feature ready {resolved_slug} . --json` after implementation evidence is complete.
- Run `specspine feature pr {resolved_slug} . --json` to draft local Pull Request review notes.
- Run `specspine feature sync-plan {resolved_slug} . --json` to review GitHub CLI sync intent without executing it.
- Run `specspine feature sync-plan {resolved_slug} . --output-dir .specspine/sync-plan/{resolved_slug}` to materialize local sync review artifacts.
- Run `specspine feature archive {resolved_slug} . --json` to package local archive evidence before lifecycle closure.
- Run `specspine validate . --fusion --features` before handoff or release.
""")

    quality_content = normalize_template(f"""
# {title} Quality

Feature ID: {resolved_slug}
Status: proposed
Why: {why_text}

## Required Checks

{quality_check_lines}

## Test Coverage

Use `- [ ] AC001 -> tests/...` to link existing local test files or test selectors.

{test_coverage_lines}

## Test Plan

{test_plan_lines}

## Review Notes

- Review each acceptance criterion against implementation evidence.
- Verify edge case handling matches the spec.
- Confirm test coverage links are valid and targets exist.

## Release Readiness

- [ ] RR001: Acceptance criteria, tasks, required checks, and test plan evidence are complete.
- [ ] RR002: Docs, release notes, or `specspine feature pr {resolved_slug} . --json` output are ready for reviewers.
- [ ] RR003: `specspine tests impact . --feature {resolved_slug} --json` has been reviewed for focused local test commands.
- [ ] RR004: `specspine consistency scan . --feature {resolved_slug} --json` has been reviewed for local spec-code-test-doc drift.
- [ ] RR005: `specspine hygiene scan . --json` has been reviewed for generated artifacts and denylisted repository residue.
- [ ] RR006: `specspine retrospective report . --json` has been reviewed for local feature improvement signals.
- [ ] RR007: `specspine coverage plan . --feature {resolved_slug} --json` has been reviewed if missing AC coverage remains.
- [ ] RR008: `specspine verify matrix {resolved_slug} . --json` has been reviewed for AC-level verification evidence.
- [ ] RR009: `specspine change risk . --feature {resolved_slug} --json` has been reviewed for changed-path risk evidence.
- [ ] RR010: `specspine security cues . --feature {resolved_slug} --json` has been reviewed for security-sensitive cues.
- [ ] RR011: `specspine provenance manifest . --feature {resolved_slug} --json` has been reviewed for local evidence hashes.
- [ ] RR012: `specspine review packet . --feature {resolved_slug} --json` has been reviewed for local pre-merge evidence.
- [ ] RR013: `specspine feature sync-plan {resolved_slug} . --json` or `--output-dir .specspine/sync-plan/{resolved_slug}` has been reviewed before any remote GitHub sync.
- [ ] RR014: `specspine feature archive {resolved_slug} . --json` has been reviewed before marking status archived.
- [ ] RR015: `specspine feature ready {resolved_slug} . --json` and `specspine validate . --fusion --features` have been run.
- [ ] RR016: No known blockers remain, or blockers are documented in review notes.
""")

    return {
        FEATURE_FILE_PATHS["spec"].format(slug=resolved_slug): spec_content,
        FEATURE_FILE_PATHS["execution"].format(slug=resolved_slug): execution_content,
        FEATURE_FILE_PATHS["quality"].format(slug=resolved_slug): quality_content,
    }


def _generate_why(parsed: dict, intent: str) -> str:
    action = parsed["action"]
    target = parsed["target"]
    return (
        f"This feature enables users to {action} the {target}, "
        f"improving the overall system usability and functionality. "
        f"The intent is: {intent}"
    )


def _generate_scope(parsed: dict) -> str:
    action = parsed["action"]
    target = parsed["target"]
    return f"Implement the ability to {action} the {target} with proper validation and error handling"


def _generate_edge_cases(parsed: dict) -> str:
    action = parsed["action"]
    target = parsed["target"]
    lines = [
        f"- Behavior when {action}ing the {target} fails due to missing prerequisites",
        f"- Handling of concurrent {action} requests for the same {target}",
        f"- Recovery from partial failures during {action} operations",
        f"- Validation of {target} state before and after {action}",
    ]
    if parsed["modifiers"]:
        lines.append(
            f"- Edge cases specific to the constraint: {parsed['modifiers'][0]}"
        )
    return "\n".join(lines)


def _generate_constraints(parsed: dict) -> str:
    target = parsed["target"]
    return "\n".join([
        f"- The {target} must maintain backward compatibility with existing configurations",
        "- Performance impact must be negligible under normal load",
        "- All changes must be auditable and reversible",
    ])


def _generate_traceability_notes(slug: str, criteria: list[dict]) -> str:
    lines = [
        f"- Each acceptance criterion (AC001-AC{len(criteria):03d}) maps to one or more implementation tasks",
        f"- Test coverage links in quality/features/{slug}.md prove criterion coverage",
        "- Use `specspine feature trace` to verify end-to-end traceability",
    ]
    for idx, criterion in enumerate(criteria[:3]):
        lines.append(f"- {criterion['id']} -> T00{idx + 2}: core logic implementation")
    return "\n".join(lines)


def _generate_dependencies(parsed: dict) -> str:
    target = parsed["target"]
    lines = [
        f"- Existing {target} infrastructure and configuration",
        "- System-level feature flags or toggle mechanisms",
        "- Test framework and CI/CD pipeline access",
    ]
    if parsed["is_complex"]:
        lines.append(f"- Coordination across components: {', '.join(parsed['components'][1:])}")
    return "\n".join(lines)


def _generate_open_questions(parsed: dict) -> str:
    target = parsed["target"]
    return "\n".join([
        f"- What is the expected scope of {target} in production environments?",
        f"- Are there any existing {target} implementations to integrate with?",
        "- What are the performance requirements for this feature?",
        "- Should this be behind a feature flag for gradual rollout?",
    ])


def _generate_test_plan(parsed: dict, criteria: list[dict]) -> str:
    lines = [
        "- Unit tests for each acceptance criterion behavior",
        "- Integration tests for CLI wiring and end-to-end flows",
        "- Edge case tests for error handling and boundary conditions",
    ]
    for criterion in criteria[:3]:
        lines.append(f"- Test for {criterion['id']}: verify {criterion['text'].replace('The system SHALL ', '')}")
    return "\n".join(lines)
